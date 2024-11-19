import unittest
from pathlib import Path

from dotfiles import list_json_to_config, PathConfig, cache_load_json, normalize_json
from util import set_current_dir_to_test_root, set_basic_atts


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        set_basic_atts(self)

    def test_normal(self):
        package_base = Path("package_bases/normal")
        packs = [f"pack{i}" for i in [1, 3, 8, 9]]
        expected = [
            [
                PathConfig(
                    package_base / "pack1" / "file1_1",
                    self.home_dir / "file1_1",
                ),
            ],
            [
                PathConfig(
                    package_base / "pack3" / "file3_1",
                    self.home_dir / "file3_1",
                ),
                PathConfig(
                    package_base / "pack3" / "dir3_1",
                    self.home_dir / "dir3_1",
                ),
            ],
            [
                PathConfig(
                    package_base / "pack8" / "file8_1",
                    self.other_dir / "file8_1",
                ),
            ],
            [
                PathConfig(
                    package_base / "pack9" / "file9_1",
                    self.home_dir / "file9_1",
                ),
            ],
        ]
        for pack, ex in zip(packs, expected):
            package_path = package_base / pack
            json_list = cache_load_json(package_base / pack / "path.json")
            json_list = normalize_json(json_list)

            with self.subTest(package=pack):
                conf_list = list_json_to_config(json_list, self.home_dir, package_path)
                self.assertListEqual(ex, conf_list)


if __name__ == '__main__':
    unittest.main()
