from rxconfig import config

from atlassian import Jira

def __connect_to_jira():
    return  Jira(url=config.jira_url, username=config.jira_user, password=config.jira_token, cloud=True)

def create_issue() -> str:
    jira = __connect_to_jira()
    new_issue = jira.issue_create(fields=dict(summary="testing", project = dict(key=config.jira_project), issuetype = dict(name=config.jira_issue_type)))

    return new_issue["key"]

def get_issue_url(issue_key) -> str:
    # Cloud
    # https://<instance>.atlassian.net/browse/<issue_key-number>

    return f"{config.jira_url}/browse/{issue_key}"