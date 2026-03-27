"""Jira REST API integration for creating and retrieving issues."""

import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import json
from html.parser import HTMLParser
from typing import ClassVar, Optional
from ..utils import debug
from ..config.helpers import get_setting, JIRA_URL, JIRA_USER, JIRA_PROJECT, JIRA_ISSUE_TYPE

# https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/

API_ISSUE = "/rest/api/3/issue"
API_ISSUE_BY_KEY = "/rest/api/3/issue/{issueIdOrKey}"
API_ISSUE_BULK_FETCH = "/rest/api/3/issue/bulkfetch"


class JiraClient:
    """Jira REST API client with persistent HTTP connection."""

    def __init__(self):
        self._session: requests.Session | None = None

    def _get_session(self) -> requests.Session:
        """Return the shared session, creating it on first use."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "Accept": "application/json",
                "Content-Type": "application/json",
            })
        self._session.auth = HTTPBasicAuth(
            get_setting(JIRA_USER),
            os.environ.get("GALADRIEL_JIRA_TOKEN", ""),
        )
        return self._session

    def _request(self, method: str, path: str, payload: str = None):
        """Send a request to Jira using the persistent session."""
        debug.set_log(False)
        debug.set_module("JIRA")

        url = get_setting(JIRA_URL) + path
        debug.log(f"JIRA URL: {url}")

        try:
            session = self._get_session()
            if payload is None:
                response = session.request(method, url, timeout=30)
            else:
                debug.log(f"JIRA Payload: {payload}")
                response = session.request(method, url, data=payload, timeout=30)
        except requests.RequestException as err:
            debug.log(f"Error [_request]: {err}")
            response = None

        debug.log(f"JIRA response: {response}")
        return response

    def create_issue(self, summary: str, description_adf_nodes: Optional[list] = None, description: Optional[str] = None) -> str:
        """Create a Jira issue and return its key."""
        if description_adf_nodes is not None:
            content = description_adf_nodes
        elif description is not None:
            content = plain_text_to_adf_nodes(description)
        else:
            content = [paragraph([text_node("")])]

        payload = json.dumps({
            "fields": {
                "project": {"key": get_setting(JIRA_PROJECT)},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": content,
                },
                "issuetype": {"name": get_setting(JIRA_ISSUE_TYPE)},
            }
        })

        response = self._request("POST", API_ISSUE, payload)

        if response is None:
            raise ConnectionError("Jira request failed: no response received")

        if response.status_code != 201:
            raise HTTPError(f"Error: {response.status_code} - {response.text}")

        return response.json()["key"]

    def get_issue(self, issue_key: str) -> dict | None:
        """Fetch a Jira issue by key and return its parsed JSON."""
        response = self._request("GET", API_ISSUE_BY_KEY.format(issueIdOrKey=issue_key))
        if response is None:
            return None
        try:
            return json.loads(response.text)
        except (json.JSONDecodeError, AttributeError):
            return None

    def check_connection(self) -> tuple[bool, str]:
        """Verify the Jira connection by calling /rest/api/3/myself."""
        response = self._request("GET", "/rest/api/3/myself")
        if response is None:
            return False, "Connection failed: no response from Jira"
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                return True, f"Connected as {data.get('displayName', data.get('emailAddress', 'unknown'))}"
            except (json.JSONDecodeError, AttributeError):
                return True, "Connected (could not parse user info)"
        if response.status_code == 401:
            return False, "Authentication failed: invalid credentials"
        if response.status_code == 403:
            return False, "Authorization failed: insufficient permissions"
        return False, f"Unexpected response: {response.status_code}"

    def bulk_fetch_issues(self, issue_keys: list[str], fields: list[str] | None = None) -> dict[str, dict]:
        """Fetch multiple Jira issues in a single request, returning a dict keyed by issue key."""
        if not issue_keys:
            return {}

        payload = json.dumps({
            "issueIdsOrKeys": issue_keys,
            "fields": fields or ["summary", "status", "updated"],
        })

        response = self._request("POST", API_ISSUE_BULK_FETCH, payload)
        if response is None:
            return {}

        try:
            data = json.loads(response.text)
        except (json.JSONDecodeError, AttributeError):
            return {}

        return {issue["key"]: issue for issue in data.get("issues", [])}


# Singleton client — reuses TCP/TLS connection across calls
_client = JiraClient()


def text_node(text: str, marks: Optional[list[str]] = None) -> dict:
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

    _MARK_TAGS: ClassVar[dict[str, str]] = {
        "b": "strong", "strong": "strong", "i": "em", "em": "em",
        "u": "underline", "s": "strike", "strike": "strike",
    }
    _HEADING_TAGS: ClassVar[dict[str, int]] = {f"h{i}": i for i in range(1, 7)}
    _LIST_TAGS: ClassVar[dict[str, str]] = {"ul": "bulletList", "ol": "orderedList"}

    def __init__(self) -> None:
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
        elif tag == "p" and self._current:
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
        if not data:
            return
        target = self._list_item_content if self._list_stack and not self._heading_level else self._current
        if not data.strip() and not target and not self._marks:
            return
        node = text_node(data, list(self._marks) if self._marks else None)
        target.append(node)

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


# Module-level functions — delegate to singleton client
def create_issue(summary: str, description_adf_nodes: Optional[list] = None, description: Optional[str] = None) -> str:
    """Create a Jira issue and return its key."""
    return _client.create_issue(summary, description_adf_nodes, description)

def check_connection() -> tuple[bool, str]:
    """Verify the Jira connection and return (success, message)."""
    return _client.check_connection()

def get_issue_url(issue_key) -> str:
    """Return the browsable URL for a Jira issue."""
    return f"{get_setting(JIRA_URL)}/browse/{issue_key}"

def get_issue(issue_key):
    """Fetch a Jira issue by key and return its parsed JSON."""
    return _client.get_issue(issue_key)

def bulk_fetch_issues(issue_keys: list[str], fields: list[str] | None = None) -> dict[str, dict]:
    """Fetch multiple Jira issues in a single request, returning a dict keyed by issue key."""
    return _client.bulk_fetch_issues(issue_keys, fields)
