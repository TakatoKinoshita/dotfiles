import unittest
from filecmp import dircmp
from pathlib import Path

from dotfiles import backup_dst, load_check_convert_json
from util import TestUtil


class MyTestCase(TestUtil.BaseTest):
    def setUp(self):
        self.set_current_dir_to_test_root()
        self.package_base = Path("package_bases/normal")
        self.backup_dir.mkdir(exist_ok=True)
        self.copy_templates()

    def test_normal_home(self):
        packs = [self.package_base / f"pack{i}" for i in range(1, 8)]
        for pack in packs:
            conf_list = load_check_convert_json(pack, self.home_dir, )
            for conf in conf_list:
                dst = conf.dst
                pack_path = self.backup_dir / pack.name
                expected = pack_path / dst.name
                with self.subTest(src=conf.src.name):
                    backup_dst(dst=dst, backup_dir=pack_path, dry_run=False, )
                    self.assertTrue(expected.exists())
                    if conf.dst.is_dir():
                        cmp = dircmp(conf.dst, expected)
                        self.assertFalse(list(cmp.diff_files))

    def test_normal_extra_dst(self):
        pack = self.package_base / "pack8"
        conf_list = load_check_convert_json(pack, self.home_dir)
        for conf in conf_list:
            dst = conf.dst
            pack_path = self.backup_dir / pack.name
            expected = pack_path / dst.name
            backup_dst(dst=dst, backup_dir=pack_path, dry_run=False, )
            self.assertTrue(expected.exists())

    def test_normal_symlink(self):
        pack = self.package_base / "pack10"
        conf_list = load_check_convert_json(pack, self.home_dir)
        for conf in conf_list:
            dst = conf.dst
            pack_path = self.backup_dir / pack.name
            expected = pack_path / dst.name
            backup_dst(dst=dst, backup_dir=pack_path, dry_run=False, )
            self.assertFalse(expected.exists())

    def test_normal_not_exist(self):
        dst = self.home_dir / "not_exist"
        pack_path = self.backup_dir / "packX"
        expected = pack_path / "not_exist"
        backup_dst(dst=dst, backup_dir=pack_path, dry_run=False, )
        self.assertFalse(expected.exists())

    def tearDown(self):
        self.reset_dsts()


if __name__ == '__main__':
    unittest.main()
