import json
import sys

from argparse import ArgumentParser
from pathlib import Path
from logging import getLogger, basicConfig, INFO

LOGGER = getLogger(__name__)


def main(
        is_restore: bool = False,
        is_dry_run: bool = False,
):
    ...


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
