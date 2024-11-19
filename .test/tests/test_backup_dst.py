import shutil
import unittest
from filecmp import dircmp
from pathlib import Path

from dotfiles import backup_dst, load_check_convert_json
from util import set_current_dir_to_test_root, reset_dsts, copy_templates, set_basic_atts


class MyTestCase(unittest.TestCase):
    def setUp(self):
        set_current_dir_to_test_root()
        set_basic_atts(self)
        self.package_base = Path("package_bases/normal")
        self.backup_dir.mkdir(exist_ok=True)
        copy_templates(Path("dst_templates"), self.home_dir, self.other_dst)

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

    def tearDown(self):
        reset_dsts(self.home_dir, self.other_dst)


if __name__ == '__main__':
    unittest.main()
