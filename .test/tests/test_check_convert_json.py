import unittest
from pathlib import Path

from dotfiles import check_convert_json, PathConfig
from util import set_current_dir_to_test_root, load_json


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        self.home_dir = Path("home")
        self.other_dir = Path("extra_dst")

    def test_normal(self):
        dotfile = Path("package_bases/normal")
        packs = [f"pack{i}" for i in [1, 3, 8, 9]]
        expected_confs = [
            [
                PathConfig(
                    dotfile / "pack1" / "file1_1",
                    self.home_dir / "file1_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack3" / "file3_1",
                    self.home_dir / "file3_1",
                ),
                PathConfig(
                    dotfile / "pack3" / "dir3_1",
                    self.home_dir / "dir3_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack8" / "file8_1",
                    self.other_dir / "file8_1",
                ),
            ],
            [
                PathConfig(
                    dotfile / "pack9" / "file9_1",
                    self.home_dir / "file9_1",
                ),
            ],
        ]
        for pack, ec in zip(packs, expected_confs):
            pack_dir = dotfile / pack
            json = load_json(pack_dir / "path.json")

            with self.subTest(package=pack):
                conf_list = check_convert_json(json, pack_dir, self.home_dir)
                self.assertListEqual(ec, conf_list)




if __name__ == '__main__':
    unittest.main()
