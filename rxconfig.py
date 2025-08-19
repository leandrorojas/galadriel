import reflex as rx
import yaml

GALADRIEL_YAML_PATH = "galadriel.yaml"
YAML_JIRA_SECTION = "jira"

def read_setting(section:str, key:str):
    try:
        with open(GALADRIEL_YAML_PATH) as galadriel_yaml:
            galadriel_config = yaml.safe_load(galadriel_yaml)
            setting = galadriel_config[section][key]
    except:
        setting = None
    return setting
    
def write_setting(section:str, key:str, value):
    try:
        with open(GALADRIEL_YAML_PATH) as galadriel_yaml:
            current_config = yaml.safe_load(galadriel_yaml)
        current_config[section][key] = value
        with open(GALADRIEL_YAML_PATH, "w") as galadriel_yaml:
            yaml.safe_dump(current_config, galadriel_yaml)
    except:
        pass

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