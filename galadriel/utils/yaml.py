import yaml

def read_setting(filename:str, section:str, key:str):
    try:
        with open(filename) as galadriel_yaml:
            galadriel_config = yaml.safe_load(galadriel_yaml)
            setting = galadriel_config[section][key]
    except:
        setting = None
    return setting

def write_setting(filename:str, section:str, key:str, value):
    try:
        with open(filename) as galadriel_yaml:
            current_config = yaml.safe_load(galadriel_yaml)
        current_config[section][key] = value
        with open(filename, "w") as galadriel_yaml:
            yaml.safe_dump(current_config, galadriel_yaml)
    except:
        pass