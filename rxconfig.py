import reflex as rx
import yaml

YAML_JIRA_SECTION = "jira"

def read_yaml_setting(section:str, key:str):
    with open("galadriel.yaml") as galadriel_yaml:
        galadriel_config = yaml.safe_load(galadriel_yaml)

        return galadriel_config[section][key]

config = rx.Config(
    app_name="galadriel",
    db_url="sqlite:///galadriel.db",
    jira_url=read_yaml_setting(YAML_JIRA_SECTION, "url"),
    jira_user=read_yaml_setting(YAML_JIRA_SECTION, "user"),
    jira_token=read_yaml_setting(YAML_JIRA_SECTION, "token"),
    jira_project=read_yaml_setting(YAML_JIRA_SECTION, "project"),
    jira_issue_type=read_yaml_setting(YAML_JIRA_SECTION, "issue_type")
)