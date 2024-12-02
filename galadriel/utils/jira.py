from rxconfig import config

from atlassian import Jira

from datetime import datetime

def __connect_to_jira():
    try:
        jira_cnn = Jira(url=config.jira_url, username=config.jira_user, password=config.jira_token, cloud=True)
    except:
        jira_cnn = None

    return jira_cnn


def create_issue(summary:str, description:str) -> str:
    jira = __connect_to_jira()

    if jira is not None:
        try:
            new_issue = jira.issue_create(fields=dict(summary="testing", project = dict(key=config.jira_project), issuetype = dict(name=config.jira_issue_type)))
            issue_key = new_issue["key"]
        except:
            issue_key = ""
    else:
        issue_key = ""

    return issue_key

def get_issue_url(issue_key) -> str:
    # Cloud
    # https://<instance>.atlassian.net/browse/<issue_key-number>

    return f"{config.jira_url}/browse/{issue_key}"

def get_issue_status(issue_key) -> str:
    jira = __connect_to_jira()

    if jira is not None:
        try:
            issue_status = jira.get_issue_status(issue_key) #TODO in GAL-216 --> this is causing delays. Try to shift to requests library and manage Jira as a class (keep connection alive)
        except:
            issue_status = ""

        return issue_status