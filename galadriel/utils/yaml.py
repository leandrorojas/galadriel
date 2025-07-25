import yaml

GALADRIEL_YAML_PATH = "galadriel.yaml"

def read_setting(section:str, key:str):
    with open(GALADRIEL_YAML_PATH) as galadriel_yaml:
        galadriel_config = yaml.safe_load(galadriel_yaml)

        return galadriel_config[section][key]
    
def write_setting(section:str, key:str, value):
    with open(GALADRIEL_YAML_PATH) as galadriel_yaml:
        current_config = yaml.safe_load(galadriel_yaml)

    current_config[section][key] = value

    with open(GALADRIEL_YAML_PATH, "w") as galadriel_yaml:
        yaml.safe_dump(current_config, galadriel_yaml)