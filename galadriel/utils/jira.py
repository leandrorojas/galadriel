from rxconfig import config

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import json

REQUEST_POST = "POST"
URL_CREATE_ISSUE = "/rest/api/3/issue"

def __jira_hit(type:str, url:str, payload:str):
    url = config.jira_url + url
    auth = HTTPBasicAuth(config.jira_user, config.jira_token)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(type, url, data=payload, headers=headers, auth = auth)        
    except Exception as err:
        print(f"Error [create_issue]: {err}")
        response = None

    return response

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

    response = __jira_hit(REQUEST_POST, URL_CREATE_ISSUE, payload)

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

def get_issue_status(issue_key) -> str:
    jira = __connect_to_jira() #TODO: replace this with __jira_hit()

    if jira is not None:
        try:
            issue_status = jira.get_issue_status(issue_key)
        except Exception as err:
            print(f"[Error] get_issue_status: {err}")
            issue_status = ""

        return issue_status