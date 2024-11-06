import json
import sys
import logging

from argparse import ArgumentParser
from pathlib import Path
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

@dataclass
class PathConfig:
    src: Path
    dst: Path

def main(
        is_restore: bool = False,
        is_dry_run: bool = False,
):
    if is_dry_run:
        handle = logging.StreamHandler(sys.stdout)
        handle.setLevel(logging.INFO)
        handle.setFormatter(logging.Formatter("DRY-RUN: %(message)s"))
        LOGGER.addHandler(handle)

    for pack in Path.cwd().iterdir():
        if not pack.is_dir():
            continue

        setting_path = pack / "path.json"
        with open(setting_path) as f:
            LOGGER.debug("Opened %s.", setting_path)
            path_dict = json.load(f)
        LOGGER.debug("Loaded %s.", setting_path)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "--restore", action="store_true",
        help="Restore dotfiles from backup."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Test run without actual file operations."
    )
    args = parser.parse_args()
    main(args.restore, args.dry_run)
