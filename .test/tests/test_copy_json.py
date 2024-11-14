import unittest
import shutil
from pathlib import Path

from dotfiles import copy_json, iter_package
from util import set_current_dir_to_test_root


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        home_dir = Path("home")
        self.backup_dir = home_dir / ".dotbackup"
        self.dotfile_dir = Path("package_bases/normal")

        self.backup_dir.mkdir(exist_ok=True)
        for p in iter_package(self.dotfile_dir):
            (self.backup_dir / p.name).mkdir(exist_ok=True)

    def test_dry_run(self):
        for p in iter_package(self.dotfile_dir):
            backup_pack = self.backup_dir / p.name
            with self.subTest(package=p.name):
                copy_json(
                    backup_dir=self.backup_dir,
                    pack_dir=p,
                    dry_run=True,
                )
                self.assertTrue(backup_pack.exists())
                self.assertFalse(list(backup_pack.iterdir()))


    def test_normal(self):
        for p in iter_package(self.dotfile_dir):
            backup_pack = self.backup_dir / p.name
            with self.subTest(package=p.name):
                copy_json(
                    backup_dir=self.backup_dir,
                    pack_dir=p,
                    dry_run=False,
                )
                self.assertTrue((backup_pack / "path.json").exists())
                self.assertEqual(len(list(backup_pack.iterdir())), 1)

    def tearDown(self):
        shutil.rmtree(self.backup_dir)


if __name__ == '__main__':
    unittest.main()
