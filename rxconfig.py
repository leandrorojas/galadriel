import os
import reflex as rx
from galadriel.utils import yaml as yaml


def _load_env(path: str = ".env"):
    """Load key=value pairs from a .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

_load_env()

GALADRIEL_YAML_PATH = "galadriel.yaml"
YAML_JIRA_SECTION = "jira"

config = rx.Config(
    app_name="galadriel",
    plugins=[rx.plugins.SitemapPlugin()],
    db_url="sqlite:///galadriel.db",
    img_src="/galadriel.320x320.jpg",
    tailwind=None,
    jira_url= yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "url"),
    jira_user=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "user"),
    jira_token=os.environ.get("GALADRIEL_JIRA_TOKEN", ""),
    jira_project=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "project"),
    jira_issue_type=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "issue_type"),
    jira_done_status=yaml.read_setting(GALADRIEL_YAML_PATH, YAML_JIRA_SECTION, "done_status")
)