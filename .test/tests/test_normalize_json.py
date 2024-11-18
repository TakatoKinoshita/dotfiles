import unittest

from pathlib import Path

from dotfiles import normalize_json, cache_load_json
from util import set_current_dir_to_test_root


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()

    def test_normal(self):
        dotfile = Path("package_bases/normal")
        packs = [f"pack{i}" for i in [1, 3, 8, 9]]
        expected = [
            [
                {
                    "is_home": True,
                    "src": "file1_1",
                    "dst": "file1_1",
                },
            ],
            [
                {
                    "is_home": True,
                    "src": "file3_1",
                    "dst": "file3_1",
                },
                {
                    "is_home": True,
                    "src": "dir3_1",
                    "dst": "dir3_1",
                },
            ],
            [
                {
                    "is_home": False,
                    "src": "file8_1",
                    "dst": "extra_dst/file8_1",
                },
            ],
            [
                {
                    "is_home": True,
                    "src": "file9_1",
                    "dst": "file9_1",
                },
            ],
        ]

        for pack, ex in zip(packs, expected):
            json = cache_load_json(dotfile / pack / "path.json")
            with self.subTest(package=pack):
                self.assertListEqual(normalize_json(json), ex)

if __name__ == '__main__':
    unittest.main()
