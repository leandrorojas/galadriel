import reflex as rx 
from galadriel.utils import yaml as yaml


GALADRIEL_YAML_PATH = "galadriel.yaml"
YAML_JIRA_SECTION = "jira"

config = rx.Config(
    app_name="galadriel",
    db_url="sqlite:///galadriel.db",
    img_src="/galadriel.320x320.jpg",
    tailwind=None,
    jira_url= yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "url"),
    jira_user=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "user"),
    jira_token=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "token"),
    jira_project=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "project"),
    jira_issue_type=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "issue_type"),
    jira_done_status=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "done_status")
)