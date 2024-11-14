import os
import json

from pathlib import Path

from dotfiles import check_convert_json

def set_current_dir_to_test_root():
    os.chdir(Path(__file__).parent.parent)

def load_json(path):
    with open(path, "r") as f:
        json_data = json.load(f)
    return json_data

def load_conf_list(pack_path_list,  home_dir):
    conf_list = []
    for pack_path in pack_path_list:
        json = load_json(pack_path / "path.json")
        conf_list.extend(check_convert_json(json, pack_path, home_dir))
    return conf_list
