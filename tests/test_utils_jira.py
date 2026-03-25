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


@pytest.fixture(autouse=True)
def fresh_client():
    """Reset the singleton client session before each test."""
    from galadriel.utils.jira import _client
    _client._session = None
    yield
    _client._session = None


@pytest.fixture
def mock_session():
    """Patch requests.Session so the client uses a mock session."""
    mock_sess = MagicMock()
    with patch("galadriel.utils.jira.requests.Session", return_value=mock_sess):
        yield mock_sess


class TestCreateIssue:
    def test_successful_creation(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-123"}
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        result = create_issue("Bug title", description="Bug description")
        assert result == "PROJ-123"

    def test_non_201_raises(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        with pytest.raises(HTTPError):
            create_issue("title", description="desc")

    def test_connection_error_raises(self, mock_session):
        mock_session.request.side_effect = Exception("connection refused")

        from galadriel.utils.jira import create_issue
        with pytest.raises(ConnectionError):
            create_issue("title", description="desc")


class TestGetIssue:
    def test_returns_parsed_json(self, mock_session):
        mock_response = MagicMock()
        mock_response.text = json.dumps({"key": "PROJ-1", "fields": {"summary": "s"}})
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import get_issue
        result = get_issue("PROJ-1")
        assert result["key"] == "PROJ-1"

    def test_connection_error_returns_none(self, mock_session):
        mock_session.request.side_effect = Exception("timeout")

        from galadriel.utils.jira import get_issue
        result = get_issue("PROJ-1")
        assert result is None

    def test_malformed_json_returns_none(self, mock_session):
        """Malformed JSON response should return None instead of raising."""
        mock_response = MagicMock()
        mock_response.text = "<html>Server Error</html>"
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import get_issue
        result = get_issue("PROJ-1")
        assert result is None


class TestBulkFetchIssues:
    def test_returns_dict_keyed_by_issue_key(self, mock_session):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "issues": [
                {"key": "PROJ-1", "fields": {"summary": "a"}},
                {"key": "PROJ-2", "fields": {"summary": "b"}},
            ]
        })
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import bulk_fetch_issues
        result = bulk_fetch_issues(["PROJ-1", "PROJ-2"])
        assert "PROJ-1" in result
        assert "PROJ-2" in result

    def test_empty_keys_returns_empty_dict(self, mock_session):
        from galadriel.utils.jira import bulk_fetch_issues
        result = bulk_fetch_issues([])
        assert result == {}
        mock_session.request.assert_not_called()

    def test_connection_error_returns_empty_dict(self, mock_session):
        mock_session.request.side_effect = Exception("timeout")

        from galadriel.utils.jira import bulk_fetch_issues
        result = bulk_fetch_issues(["PROJ-1"])
        assert result == {}

    def test_malformed_json_returns_empty_dict(self, mock_session):
        mock_response = MagicMock()
        mock_response.text = "not json"
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import bulk_fetch_issues
        result = bulk_fetch_issues(["PROJ-1"])
        assert result == {}

    def test_sends_requested_fields(self, mock_session):
        mock_response = MagicMock()
        mock_response.text = json.dumps({"issues": []})
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import bulk_fetch_issues
        bulk_fetch_issues(["PROJ-1"], fields=["summary"])
        payload = json.loads(mock_session.request.call_args.kwargs.get("data", mock_session.request.call_args[0][2] if len(mock_session.request.call_args[0]) > 2 else "{}"))
        assert payload["fields"] == ["summary"]


class TestSessionReuse:
    def test_reuses_session_across_calls(self, mock_session):
        """Multiple calls should reuse the same session (connection keep-alive)."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({"key": "PROJ-1", "fields": {}})
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import get_issue
        get_issue("PROJ-1")
        get_issue("PROJ-2")
        assert mock_session.request.call_count == 2


class TestCreateIssueWithAdfNodes:
    def test_adf_nodes_passed_directly(self, mock_session):
        """ADF nodes passed via description_adf_nodes go straight into the payload."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-99"}
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import create_issue, paragraph, text_node
        nodes = [paragraph([text_node("hello")])]
        result = create_issue("title", description_adf_nodes=nodes)
        assert result == "PROJ-99"

        call_kwargs = mock_session.request.call_args.kwargs
        call_args = mock_session.request.call_args.args
        data = call_kwargs.get("data") or (call_args[2] if len(call_args) > 2 else None)
        payload = json.loads(data)
        assert payload["fields"]["description"]["content"] == nodes

    def test_no_description_uses_empty_paragraph(self, mock_session):
        """When no description is given, content should be a single empty paragraph."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "PROJ-1"}
        mock_session.request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        create_issue("title")

        call_kwargs = mock_session.request.call_args.kwargs
        call_args = mock_session.request.call_args.args
        data = call_kwargs.get("data") or (call_args[2] if len(call_args) > 2 else None)
        payload = json.loads(data)
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

    def test_br_inside_list_item(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<ul><li>line1<br>line2</li></ul>")
        li_content = nodes[0]["content"][0]["content"][0]["content"]
        assert any(n["type"] == "hardBreak" for n in li_content)

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

    def test_space_between_adjacent_inline_tags(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<b>one</b> <i>two</i>")
        texts = [n["text"] for n in nodes[0]["content"] if n.get("type") == "text"]
        combined = "".join(texts)
        assert " " in combined
        assert "one" in combined
        assert "two" in combined

    def test_no_extra_paragraphs_from_block_whitespace(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<p>first</p>\n<p>second</p>")
        assert len(nodes) == 2
        assert nodes[0]["content"][0]["text"] == "first"
        assert nodes[1]["content"][0]["text"] == "second"

    def test_inline_space_preserved_with_block_whitespace(self):
        from galadriel.utils.jira import html_to_adf_nodes
        nodes = html_to_adf_nodes("<p><b>one</b> <i>two</i></p>\n<p>three</p>")
        assert len(nodes) == 2
        texts = [n["text"] for n in nodes[0]["content"] if n.get("type") == "text"]
        assert " " in "".join(texts)


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
