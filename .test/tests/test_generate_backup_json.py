import unittest
from pathlib import Path

from dotfiles import generate_backup_json, load_check_convert_json, backup_dst
from util import set_current_dir_to_test_root, reset_dsts, copy_templates, set_basic_atts


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        set_basic_atts(self)
        self.package_base = Path("package_bases/normal")
        self.backup_dir.mkdir(exist_ok=True)

    def test_normal_not_empty(self):
        copy_templates(Path("dst_templates"), self.home_dir, self.other_dst)
        expected = [
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack1" / "file1_1",
                    "dst": self.home_dir / "file1_1",
                }
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack2" / "dir2_1",
                    "dst": self.home_dir / "dir2_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack3" / "file3_1",
                    "dst": self.home_dir / "file3_1",
                },
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack3" / "dir3_1",
                    "dst": self.home_dir / "dir3_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack4" / "file4_1_1",
                    "dst": self.home_dir / "file4_1_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack5" / "dir5_1_1",
                    "dst": self.home_dir / "dir5_1_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack6" / "file",
                    "dst": self.home_dir / "file",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack7" / "file7_1",
                    "dst": self.home_dir / "dir/file7_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack8" / "file8_1",
                    "dst": self.other_dst / "file8_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": self.backup_dir / "pack9" / "file9_1",
                    "dst": self.home_dir / "file9_1",
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
        reset_dsts(self.home_dir, self.other_dst)


if __name__ == '__main__':
    unittest.main()
