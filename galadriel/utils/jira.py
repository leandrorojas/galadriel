from rxconfig import config

from atlassian import Jira

from datetime import datetime

def __connect_to_jira():
    try:
        jira_cnn = Jira(url=config.jira_url, username=config.jira_user, password=config.jira_token, cloud=True)
    except Exception as err:
        print(err)
        jira_cnn = None

    return jira_cnn


def create_issue(summary:str, description:str) -> str:
    jira = __connect_to_jira()

    if jira is not None:
        try:
            new_issue = jira.issue_create(fields=dict(summary=summary, description=description, project = dict(key=config.jira_project), issuetype = dict(name=config.jira_issue_type)))
            issue_key = new_issue["key"]
        except Exception as err:
            print(err)
            issue_key = ""
    else:
        issue_key = ""

    return issue_key

def get_issue_url(issue_key) -> str:
    return f"{config.jira_url}/browse/{issue_key}"

def get_issue_status(issue_key) -> str:
    jira = __connect_to_jira()

    if jira is not None:
        try:
            issue_status = jira.get_issue_status(issue_key)
        except Exception as err:
            print(err)
            issue_status = ""

        return issue_status