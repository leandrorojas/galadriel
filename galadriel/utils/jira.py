from rxconfig import config

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import json
from typing import List
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
            response = requests.request(type, url, headers=headers, auth=auth)
        else:
            debug.log(f"JIRA Payload: {payload}")
            response = requests.request(type, url, data=payload, headers=headers, auth=auth)
    except Exception as err:
        print(f"Error [create_issue]: {err}")
        response = None

    debug.log(f"JIRA response: {response}")
    return response

def __get_issue_api_url(issue_key) -> str:
    return API_ISSUE + API_ISSUE_STATUS.format(issueIdOrKey=issue_key)

def create_issue(summary:str, description:str) -> str:

    payload = json.dumps(
        {
        "fields": {
            "project": {"key": config.jira_project},
            "summary": summary,
            "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                "type": "paragraph",
                "content": [
                    {
                    "type": "text",
                    "text": description
                    }
                ]
                }
            ]
            },
            "issuetype": {"name": config.jira_issue_type}
        }
        }
    )

    response = __jira_hit(REQUEST_POST, API_ISSUE, payload)

    if response is not None:
        if (response.status_code != 201):
            raise HTTPError(f"Error: {response.status_code} - {response.text}")
        else:
            issue_key = response.json()["key"]
    else:
        issue_key = ""

    return issue_key

def get_issue_url(issue_key) -> str:
    return f"{config.jira_url}/browse/{issue_key}"

def get_issue(issue_key):
    raw_response = __jira_hit(REQUEST_GET, __get_issue_api_url(issue_key))
    return json.loads(raw_response.text)
    #return str(json.dumps(json.loads(raw_response.text), sort_keys=True, indent=4, separators=(",", ": ")))

#TODO: Add get_issue_status by bulk --> /rest/api/3/issue/bulkfetch --> https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-bulkfetch-post