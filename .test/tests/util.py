import os
import json

from pathlib import Path


def set_current_dir_to_test_root():
    os.chdir(Path(__file__).parent.parent)
