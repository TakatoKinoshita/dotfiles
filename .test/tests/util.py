import os
import json

from pathlib import Path

def set_current_dir_to_test_root():
    os.chdir(Path(__file__).parent.parent)

def load_json(path):
    with open(path, "r") as f:
        json_data = json.load(f)
    return json_data
