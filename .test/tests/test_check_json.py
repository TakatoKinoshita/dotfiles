import unittest

from pathlib import Path

from dotfiles import check_json, cache_load_json
from util import set_current_dir_to_test_root

class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()

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
            json = cache_load_json(dotfile / pack / "path.json")
            with self.subTest(package=pack, error=e), self.assertRaises(e):
                check_json(json)


if __name__ == '__main__':
    unittest.main()
