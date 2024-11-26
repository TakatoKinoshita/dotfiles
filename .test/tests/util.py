import os
import shutil
import unittest

from pathlib import Path


class TestUtil:
    class BaseTest(unittest.TestCase):
        home_dir = Path("home")
        extra_dst = Path("extra_dst")
        backup_dir = Path("home/.dotbackup")
        temp_dir = Path("dst_templates")

        @classmethod
        def set_current_dir_to_test_root(cls):
            os.chdir(Path(__file__).parent.parent)

        @classmethod
        def reset_dsts(cls):
            shutil.rmtree(cls.home_dir)
            shutil.rmtree(cls.extra_dst)
            cls.home_dir.mkdir(exist_ok=True)
            (cls.home_dir / ".gitkeep").touch()
            cls.extra_dst.mkdir(exist_ok=True)
            (cls.extra_dst / ".gitkeep").touch()

        @classmethod
        def copy_templates(cls):
            shutil.copytree(cls.temp_dir / "home", cls.home_dir, dirs_exist_ok=True, symlinks=True, )
            shutil.copytree(cls.temp_dir / "extra_dst", cls.extra_dst, dirs_exist_ok=True, symlinks=True, )
