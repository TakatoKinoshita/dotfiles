import unittest
from pathlib import Path

from dotfiles import generate_backup_json, load_check_convert_json, backup_dst
from util import TestUtil


class MyTestCase(TestUtil.BaseTest):
    def setUp(self):
        self.set_current_dir_to_test_root()
        self.package_base = Path("package_bases/normal")
        self.backup_dir.mkdir(exist_ok=True)

    def test_normal_not_empty(self):
        self.copy_templates()
        expected = [
            [
                {
                    "is_home": False,
                    "src": "file1_1",
                    "dst": str((self.home_dir / "file1_1").resolve()),
                }
            ],
            [
                {
                    "is_home": False,
                    "src": "dir2_1",
                    "dst": str((self.home_dir / "dir2_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file3_1",
                    "dst": str((self.home_dir / "file3_1").resolve()),
                },
                {
                    "is_home": False,
                    "src": "dir3_1",
                    "dst": str((self.home_dir / "dir3_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file4_1_1",
                    "dst": str((self.home_dir / "file4_1_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "dir5_1_1",
                    "dst": str((self.home_dir / "dir5_1_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file",
                    "dst": str((self.home_dir / "file").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file7_1",
                    "dst": str((self.home_dir / "dir/file7_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file8_1",
                    "dst": str((self.extra_dst / "file8_1").resolve()),
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file9_1",
                    "dst": str((self.home_dir / "file9_1").resolve()),
                },
            ],
        ]
        for pack, ex in zip([f"pack{i}" for i in range(1, 10)], expected):
            pack_path = self.package_base / pack
            confs = load_check_convert_json(pack_path, self.home_dir)
            backup_path = self.backup_dir / pack
            for conf in confs:
                backup_dst(dst=conf.dst, backup_dir=backup_path, dry_run=False, )
            with self.subTest(pack=pack):
                json_bk = generate_backup_json(confs, backup_path)
                self.assertListEqual(ex, json_bk)

    def test_normal_empty(self):
        pack_path = self.package_base / "pack10"
        confs = load_check_convert_json(pack_path, self.home_dir)
        backup_path = self.backup_dir / "pack10"
        for conf in confs:
            backup_dst(dst=conf.dst, backup_dir=backup_path, dry_run=False, )
            json_bk = generate_backup_json(confs, backup_path)
            self.assertIsNone(json_bk)

    def tearDown(self):
        self.reset_dsts()


if __name__ == '__main__':
    unittest.main()
