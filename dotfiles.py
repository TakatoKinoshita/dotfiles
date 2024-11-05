import json
import sys
import logging

from argparse import ArgumentParser
from pathlib import Path

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def main(
        is_restore: bool = False,
        is_dry_run: bool = False,
):
    if is_dry_run:
        handle = logging.StreamHandler(sys.stdout)
        handle.setLevel(logging.INFO)
        handle.setFormatter(logging.Formatter("DRY-RUN: %(message)s"))
        LOGGER.addHandler(handle)




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
