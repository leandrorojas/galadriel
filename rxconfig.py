import reflex as rx

from galadriel.utils.yaml import read_setting

YAML_JIRA_SECTION = "jira"

config = rx.Config(
    app_name="galadriel",
    db_url="sqlite:///galadriel.db",
    img_src="/galadriel.320x320.jpg",
    tailwind=None,
    jira_url= read_setting(YAML_JIRA_SECTION, "url"),
    jira_user=read_setting(YAML_JIRA_SECTION, "user"),
    jira_token=read_setting(YAML_JIRA_SECTION, "token"),
    jira_project=read_setting(YAML_JIRA_SECTION, "project"),
    jira_issue_type=read_setting(YAML_JIRA_SECTION, "issue_type"),
    jira_done_status=read_setting(YAML_JIRA_SECTION, "done_status")
)