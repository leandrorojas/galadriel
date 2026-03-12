"""Tests for galadriel.utils.jira."""

import pytest
import json
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def mock_config():
    """Provide a fake rxconfig.config for all jira tests."""
    fake_config = MagicMock()
    fake_config.jira_url = "https://jira.example.com"
    fake_config.jira_user = "user@example.com"
    fake_config.jira_token = "fake-token"
    fake_config.jira_project = "PROJ"
    fake_config.jira_issue_type = "Bug"
    with patch("galadriel.utils.jira.config", fake_config):
        yield fake_config


class TestCreateIssue:
    @patch("galadriel.utils.jira.requests.request")
    def test_successful_creation(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-123"}
        mock_request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        result = create_issue("Bug title", description="Bug description")
        assert result == "PROJ-123"

    @patch("galadriel.utils.jira.requests.request")
    def test_non_201_raises(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        with pytest.raises(HTTPError):
            create_issue("title", description="desc")

    @patch("galadriel.utils.jira.requests.request")
    def test_connection_error_raises(self, mock_request):
        mock_request.side_effect = Exception("connection refused")

        from galadriel.utils.jira import create_issue
        with pytest.raises(ConnectionError):
            create_issue("title", description="desc")


class TestGetIssue:
    @patch("galadriel.utils.jira.requests.request")
    def test_returns_parsed_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = json.dumps({"key": "PROJ-1", "fields": {"summary": "s"}})
        mock_request.return_value = mock_response

        from galadriel.utils.jira import get_issue
        result = get_issue("PROJ-1")
        assert result["key"] == "PROJ-1"

    @patch("galadriel.utils.jira.requests.request")
    def test_connection_error_returns_none(self, mock_request):
        mock_request.side_effect = Exception("timeout")

        from galadriel.utils.jira import get_issue
        result = get_issue("PROJ-1")
        assert result is None


class TestCreateIssueWithAdfNodes:
    @patch("galadriel.utils.jira.requests.request")
    def test_adf_nodes_passed_directly(self, mock_request):
        """ADF nodes passed via description_adf_nodes go straight into the payload."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-99"}
        mock_request.return_value = mock_response

        from galadriel.utils.jira import create_issue, paragraph, text_node
        nodes = [paragraph([text_node("hello")])]
        result = create_issue("title", description_adf_nodes=nodes)
        assert result == "PROJ-99"

        payload = json.loads(mock_request.call_args.kwargs.get("data", mock_request.call_args[1].get("data", "")))
        assert payload["fields"]["description"]["content"] == nodes

    @patch("galadriel.utils.jira.requests.request")
    def test_no_description_uses_empty_paragraph(self, mock_request):
        """When no description is given, content should be a single empty paragraph."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-1"}
        mock_request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        create_issue("title")

        payload = json.loads(mock_request.call_args.kwargs.get("data", mock_request.call_args[1].get("data", "")))
        content = payload["fields"]["description"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "paragraph"


class TestHtmlToAdfNodes:
    def test_plain_text(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("hello world")
        assert nodes == [{"type": "paragraph", "content": [{"type": "text", "text": "hello world"}]}]

    def test_bold(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<b>bold</b>")
        text_node = nodes[0]["content"][0]
        assert text_node["text"] == "bold"
        assert text_node["marks"] == [{"type": "strong"}]

    def test_italic(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<i>italic</i>")
        text_node = nodes[0]["content"][0]
        assert text_node["marks"] == [{"type": "em"}]

    def test_underline_and_strike(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<u>underlined</u> and <s>struck</s>")
        assert nodes[0]["content"][0]["marks"] == [{"type": "underline"}]
        assert nodes[0]["content"][2]["marks"] == [{"type": "strike"}]

    def test_nested_marks(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<b><i>both</i></b>")
        marks = nodes[0]["content"][0]["marks"]
        mark_types = {m["type"] for m in marks}
        assert "strong" in mark_types
        assert "em" in mark_types

    def test_paragraph_tags(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<p>first</p><p>second</p>")
        assert len(nodes) == 2
        assert nodes[0]["content"][0]["text"] == "first"
        assert nodes[1]["content"][0]["text"] == "second"

    def test_heading(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<h2>Title</h2>")
        assert nodes[0]["type"] == "heading"
        assert nodes[0]["attrs"]["level"] == 2
        assert nodes[0]["content"][0]["text"] == "Title"

    def test_unordered_list(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<ul><li>one</li><li>two</li></ul>")
        assert len(nodes) == 1
        assert nodes[0]["type"] == "bulletList"
        assert len(nodes[0]["content"]) == 2
        assert nodes[0]["content"][0]["type"] == "listItem"
        assert nodes[0]["content"][1]["type"] == "listItem"

    def test_ordered_list(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<ol><li>first</li><li>second</li></ol>")
        assert len(nodes) == 1
        assert nodes[0]["type"] == "orderedList"
        assert len(nodes[0]["content"]) == 2

    def test_empty_string(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("")
        assert len(nodes) == 1
        assert nodes[0]["type"] == "paragraph"

    def test_br_tag(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("line1<br>line2")
        content = nodes[0]["content"]
        assert any(n["type"] == "hardBreak" for n in content)


class TestPlainTextToAdfNodes:
    def test_single_line(self):
        from galadriel.utils.jira import plain_text_to_adf_nodes
        nodes = plain_text_to_adf_nodes("hello")
        assert len(nodes) == 1
        assert nodes[0]["content"][0]["text"] == "hello"

    def test_multiple_lines(self):
        from galadriel.utils.jira import plain_text_to_adf_nodes
        nodes = plain_text_to_adf_nodes("line1\nline2\nline3")
        assert len(nodes) == 3

    def test_empty_string(self):
        from galadriel.utils.jira import plain_text_to_adf_nodes
        assert plain_text_to_adf_nodes("") == []

    def test_skips_blank_lines(self):
        from galadriel.utils.jira import plain_text_to_adf_nodes
        nodes = plain_text_to_adf_nodes("a\n\nb")
        assert len(nodes) == 2


class TestGetIssueUrl:
    def test_formats_url(self):
        from galadriel.utils.jira import get_issue_url
        result = get_issue_url("PROJ-42")
        assert result == "https://jira.example.com/browse/PROJ-42"
