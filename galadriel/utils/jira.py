"""Jira REST API integration for creating and retrieving issues."""

from rxconfig import config

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import json
from html.parser import HTMLParser
from typing import ClassVar, Dict, List, Optional
from ..utils import debug

# https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/

REQUEST_POST = "POST"
REQUEST_GET = "GET"
API_ISSUE = "/rest/api/3/issue"
API_ISSUE_STATUS = "/{issueIdOrKey}"

def __jira_hit(type:str, url:str, payload:str = None):
    debug.set_log(False)
    debug.set_module("JIRA")

    url = config.jira_url + url
    auth = HTTPBasicAuth(config.jira_user, config.jira_token)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    debug.log(f"JIRA URL: {url}")
    
    try:
        if payload is None:
            response = requests.request(type, url, headers=headers, auth=auth, timeout=30)
        else:
            debug.log(f"JIRA Payload: {payload}")
            response = requests.request(type, url, data=payload, headers=headers, auth=auth, timeout=30)
    except Exception as err:
        debug.log(f"Error [jira_hit]: {err}")
        response = None

    debug.log(f"JIRA response: {response}")
    return response

def __get_issue_api_url(issue_key) -> str:
    return API_ISSUE + API_ISSUE_STATUS.format(issueIdOrKey=issue_key)

def text_node(text: str, marks: Optional[List[str]] = None) -> dict:
    """Build an ADF text node with optional marks."""
    node = {"type": "text", "text": text}
    if marks:
        node["marks"] = [{"type": m} for m in marks]
    return node


def paragraph(content: list) -> dict:
    """Build an ADF paragraph node."""
    return {"type": "paragraph", "content": content}


class _HtmlToAdfParser(HTMLParser):
    """Convert simple HTML from the rich text editor into Jira ADF nodes."""

    _MARK_TAGS: ClassVar[Dict[str, str]] = {
        "b": "strong", "strong": "strong", "i": "em", "em": "em",
        "u": "underline", "s": "strike", "strike": "strike",
    }
    _HEADING_TAGS: ClassVar[Dict[str, int]] = {f"h{i}": i for i in range(1, 7)}
    _LIST_TAGS: ClassVar[Dict[str, str]] = {"ul": "bulletList", "ol": "orderedList"}

    def __init__(self):
        super().__init__()
        self.nodes: list = []
        self._current: list = []
        self._marks: list = []
        self._list_stack: list = []
        self._list_items: list = []
        self._list_item_content: list = []
        self._heading_level: int = 0

    def handle_starttag(self, tag, attrs):
        """Handle an opening HTML tag."""
        if tag in self._MARK_TAGS:
            self._marks.append(self._MARK_TAGS[tag])
        elif tag in self._HEADING_TAGS:
            self._heading_level = self._HEADING_TAGS[tag]
            self._current = []
        elif tag in self._LIST_TAGS:
            if self._current:
                self.nodes.append(paragraph(self._current))
                self._current = []
            self._list_stack.append(self._LIST_TAGS[tag])
            self._list_items.append([])
        elif tag == "li":
            self._list_item_content = []
        elif tag == "br":
            target = self._list_item_content if self._list_stack else self._current
            target.append({"type": "hardBreak"})
        elif tag == "p":
            if self._current:
                self.nodes.append(paragraph(self._current))
                self._current = []

    def handle_endtag(self, tag):
        """Handle a closing HTML tag."""
        if tag in self._MARK_TAGS:
            mark = self._MARK_TAGS[tag]
            if mark in self._marks:
                self._marks.remove(mark)
        elif tag in self._HEADING_TAGS and self._heading_level:
            self.nodes.append({"type": "heading", "attrs": {"level": self._heading_level}, "content": self._current})
            self._current = []
            self._heading_level = 0
        elif tag == "li" and self._list_stack:
            self._list_items[-1].append(
                {"type": "listItem", "content": [paragraph(self._list_item_content)]}
            )
        elif tag in self._LIST_TAGS and self._list_stack:
            list_type = self._list_stack.pop()
            items = self._list_items.pop()
            self.nodes.append({"type": list_type, "content": items})
        elif tag == "p":
            self.nodes.append(paragraph(self._current))
            self._current = []

    def handle_data(self, data):
        """Handle raw text data between tags."""
        if not data.strip() and not self._marks:
            return
        node = text_node(data, list(self._marks) if self._marks else None)
        if self._list_stack and not self._heading_level:
            self._list_item_content.append(node)
        else:
            self._current.append(node)

    def get_adf_nodes(self) -> list:
        """Return the collected ADF content nodes."""
        if self._current:
            self.nodes.append(paragraph(self._current))
            self._current = []
        return self.nodes if self.nodes else [paragraph([text_node("")])]


def html_to_adf_nodes(html: str) -> list:
    """Convert HTML string to a list of Jira ADF content nodes."""
    parser = _HtmlToAdfParser()
    parser.feed(html)
    return parser.get_adf_nodes()


def plain_text_to_adf_nodes(text: str) -> list:
    """Convert a plain text string to ADF paragraph nodes."""
    if not text:
        return []
    paragraphs = text.split("\n")
    nodes = []
    for para in paragraphs:
        if para:
            nodes.append(paragraph([text_node(para)]))
    return nodes


def create_issue(summary: str, description_adf_nodes: Optional[list] = None, description: Optional[str] = None) -> str:
    """Create a Jira issue and return its key.

    Accepts either pre-built ADF nodes or a plain text description.
    """
    if description_adf_nodes is not None:
        content = description_adf_nodes
    elif description is not None:
        content = plain_text_to_adf_nodes(description)
    else:
        content = [paragraph([text_node("")])]

    payload = json.dumps(
        {
        "fields": {
            "project": {"key": config.jira_project},
            "summary": summary,
            "description": {
            "type": "doc",
            "version": 1,
            "content": content
            },
            "issuetype": {"name": config.jira_issue_type}
        }
        }
    )

    response = __jira_hit(REQUEST_POST, API_ISSUE, payload)

    if response is None:
        raise ConnectionError("Jira request failed: no response received")

    if (response.status_code != 201):
        raise HTTPError(f"Error: {response.status_code} - {response.text}")

    return response.json()["key"]

def get_issue_url(issue_key) -> str:
    """Return the browsable URL for a Jira issue."""
    return f"{config.jira_url}/browse/{issue_key}"

def get_issue(issue_key):
    """Fetch a Jira issue by key and return its parsed JSON."""
    raw_response = __jira_hit(REQUEST_GET, __get_issue_api_url(issue_key))
    if raw_response is None:
        return None
    return json.loads(raw_response.text)