import os
import json
import shutil

from pathlib import Path


def set_current_dir_to_test_root():
    os.chdir(Path(__file__).parent.parent)

def reset_dsts(home_dir, extra_dst):
    shutil.rmtree(home_dir)
    shutil.rmtree(extra_dst)
    home_dir.mkdir(exist_ok=True)
    (home_dir / ".gitkeep").touch()
    extra_dst.mkdir(exist_ok=True)
    (extra_dst / ".gitkeep").touch()
