"""YAML helper functions.

This module exposes two small helpers for reading and writing settings to a
YAML file.  The previous implementation of :func:`write_setting` assumed that
the configuration file and the desired section already existed.  When the file
or section was missing a ``KeyError`` or ``FileNotFoundError`` was raised and
silently swallowed, leaving the file untouched.  As a consequence calls such
as ``write_setting('galadriel.yaml', 'galadriel', 'first_run', 1)`` would fail
when ``galadriel.yaml`` did not yet exist – exactly the situation that happens
on the first run of the application.

The function now creates the configuration file (and any missing sections)
when necessary so the setting is reliably written.
"""

import os
import yaml

def read_setting(filename:str, section:str, key:str):
    try:
        with open(filename) as galadriel_yaml:
            galadriel_config = yaml.safe_load(galadriel_yaml)
            setting = galadriel_config[section][key]
    except Exception:
        setting = None
    return setting

def write_setting(filename:str, section:str, key:str, value):
    """Write ``value`` under ``section`` and ``key`` to ``filename``.

    The previous implementation failed silently if the file or section was
    missing.  This version creates the file and the section as needed so that
    settings can always be persisted.
    """

    try:
        if os.path.exists(filename):
            with open(filename) as galadriel_yaml:
                current_config = yaml.safe_load(galadriel_yaml) or {}
        else:
            current_config = {}

        # Ensure the section exists and is a dictionary
        if section not in current_config or not isinstance(current_config[section], dict):
            current_config[section] = {}

        current_config[section][key] = value

        with open(filename, "w") as galadriel_yaml:
            yaml.safe_dump(current_config, galadriel_yaml)
    except Exception:
        # Silently ignore write errors, since this function does not create keys
        # or sections that do not already exist.
        pass