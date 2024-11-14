import unittest
from pathlib import Path

from dotfiles import check_convert_json, PathConfig
from util import set_current_dir_to_test_root, load_json


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        self.home_dir = Path("home")
        self.other_dir = Path("other_dst")

    def test_normal(self):
        dotfile = Path("package_bases/normal")
        packs = [f"pack{i}" for i in [1, 3, 8, 9]]
        pack_len = [1, 2, 1, 1]
        expected_confs = [
            [
                PathConfig(
                    dotfile / "pack1" / "file1_1",
                    Path("pack1/file1_1"),
                    self.home_dir / "file1_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack3" / "file3_1",
                    Path("pack3/file3_1"),
                    self.home_dir / "file3_1",
                ),
                PathConfig(
                    dotfile / "pack3" / "dir3_1",
                    Path("pack3/dir3_1"),
                    self.home_dir / "dir3_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack8" / "file8_1",
                    Path("pack8/file8_1"),
                    self.other_dir / "file8_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack9" / "file9_1",
                    Path("pack9/file9_1"),
                    self.home_dir / "file9_1",
                ),
            ],
        ]
        for pack, pl, ec in zip(packs, pack_len, expected_confs):
            pack_dir = dotfile / pack
            json = load_json(pack_dir / "path.json")

            with self.subTest(package=pack):
                conf_list = check_convert_json(json, pack_dir, self.home_dir)

                self.assertIsInstance(conf_list, list)
                [self.assertIsInstance(c, PathConfig) for c in conf_list]
                self.assertEqual(pl, len(conf_list))
                self.assertListEqual(ec, conf_list)

    def test_error(self):
        dotfile = Path("package_bases/negative")
        packs = [f"pack{i}" for i in range(1, 5)]
        expected_errors = [
            TypeError,
            KeyError,
            KeyError,
            TypeError,
        ]
        for pack, e in zip(packs, expected_errors):
            pack_dir = dotfile / pack
            json = load_json(pack_dir / "path.json")
            with self.subTest(package=pack, error=e), self.assertRaises(e):
                check_convert_json(json, pack_dir, self.home_dir)


if __name__ == '__main__':
    unittest.main()