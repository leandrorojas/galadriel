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
        result = create_issue("Bug title", "Bug description")
        assert result == "PROJ-123"

    @patch("galadriel.utils.jira.requests.request")
    def test_non_201_raises(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response

        from galadriel.utils.jira import create_issue
        with pytest.raises(HTTPError):
            create_issue("title", "desc")

    @patch("galadriel.utils.jira.requests.request")
    def test_connection_error_returns_empty(self, mock_request):
        mock_request.side_effect = Exception("connection refused")

        from galadriel.utils.jira import create_issue
        result = create_issue("title", "desc")
        assert result == ""


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


class TestGetIssueUrl:
    def test_formats_url(self):
        from galadriel.utils.jira import get_issue_url
        result = get_issue_url("PROJ-42")
        assert result == "https://jira.example.com/browse/PROJ-42"
