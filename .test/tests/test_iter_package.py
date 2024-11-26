import unittest
from pathlib import Path

from dotfiles import iter_package
from util import TestUtil


class MyTestCase(TestUtil.BaseTest):
    def setUp(self):
        self.set_current_dir_to_test_root()

    def test_normal(self):
        package_dir = Path("package_bases/for_iter")
        res = list(iter_package(package_dir))
        self.assertEqual(len(res), 2)
        [self.assertIsInstance(e, Path) for e in res]
        self.assertIn(package_dir / "pack1", res)
        self.assertIn(package_dir / "pack2", res)


if __name__ == '__main__':
    unittest.main()
