import unittest
import shutil
from filecmp import dircmp

from pathlib import Path

from dotfiles import backup_dst, load_check_convert_json
from util import set_current_dir_to_test_root

class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        self.home_dir = Path("home")
        self.backup_dir = self.home_dir / ".dotbackup"
        self.package_base = Path("package_bases/normal")
        self.backup_dir.mkdir(exist_ok=True)

        self.other_dst = Path("extra_dst")
        self.temp_dir = Path("dst_templates")
        shutil.copytree(
            self.temp_dir / "home",
            self.home_dir,
            dirs_exist_ok=True,
            symlinks=True,
        )
        shutil.copytree(
            self.temp_dir / "other_dst",
            self.other_dst,
            dirs_exist_ok=True,
            symlinks=True,
        )


    def test_normal_home(self):
        packs = [self.package_base / f"pack{i}" for i in range(1, 8)]
        for pack in packs:
            conf_list = load_check_convert_json(pack, self.home_dir,)
            for conf in conf_list:
                dst = conf.dst
                expected = self.backup_dir / dst.name
                with self.subTest(src=conf.src.name):
                    backup_dst(
                        dst=dst,
                        backup_dir=self.backup_dir,
                        dry_run=False,
                    )
                    self.assertTrue(expected.exists())
                    if conf.dst.is_dir():
                        cmp = dircmp(conf.dst, expected)
                        self.assertFalse(list(cmp.diff_files))


    def tearDown(self):
        shutil.rmtree(self.home_dir)
        shutil.rmtree(self.other_dst)
        self.home_dir.mkdir(exist_ok=True)
        (self.home_dir / ".gitkeep").touch()
        self.other_dst.mkdir(exist_ok=True)
        (self.other_dst / ".gitkeep").touch()

if __name__ == '__main__':
    unittest.main()
