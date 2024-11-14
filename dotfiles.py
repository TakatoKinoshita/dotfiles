#! /usr/bin/env python3

import json
import logging
import shutil
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import wraps
from inspect import signature
from pathlib import Path

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def recording(log: logging.Logger):
    def _decorator(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            name = func.__name__
            bn = signature(func).bind(*args, **kwargs)
            bn.apply_defaults()

            log.debug("----------start---------- [%s]", name)
            log.debug("args: %s", bn.arguments)

            try:
                result = func(*args, **kwargs)
            except:
                log.error("%s failed", name)
                log.error("args: %s", bn.arguments)
                raise

            log.debug("returns: %s", result)
            log.debug("-----------end----------- [%s]", name)

            return result

        return _wrapper

    return _decorator


@dataclass(frozen=True)
class PathConfig:
    src: Path
    src_relative: Path
    dst: Path


json_scalar = bool | int | float | str
json_type = json_scalar | list["json_obj"] | dict[str, "json_obj"]


def iter_package(package_base: Path):
    for p in package_base.iterdir():
        if not p.is_dir():
            continue
        if p.name.startswith("."):
            continue
        yield p


@recording(LOGGER)
def check_convert_json(
        json_obj: json_type,
        pack_path: Path,
        home_dir: Path,
) -> list[PathConfig]:
    if isinstance(json_obj, json_scalar):
        LOGGER.error("path.json must be JSON object or array of objects. But got %s.", json_obj)
        raise TypeError("%s is invalid." % json_obj)

    if isinstance(json_obj, dict):
        json_obj = [json_obj]

    path_list: list[PathConfig] = []
    for conf in json_obj:
        is_home = conf.get("is_home", True)
        if not isinstance(is_home, bool):
            LOGGER.error('value of key "is_home" must be boolean. But got %s.', is_home)
            raise TypeError("%s is invalid." % is_home)

        try:
            src = Path(conf["src"])
            dst = home_dir / Path(conf["dst"]) if is_home else Path(conf["dst"])
        except KeyError:
            LOGGER.error('key "src" or "dst" not found in "%s".', conf)
            raise
        except TypeError:
            LOGGER.error('key "src" and "dst" must be valid path. But got "%s".', conf)
            raise
        except:
            LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
            raise


#@recording(LOGGER)
#def check_convert_json(
#        json_obj: json_type,
#        pack_path: Path,
#        home_dir: Path,
#) -> list[PathConfig]:
#
#        path_conf = PathConfig(pack_path / src, pack_path.name / src, dst)
#        LOGGER.debug("Converted: %s -> %s", conf, path_conf)
#        path_list.append(path_conf)
#
#    return path_list


@recording(LOGGER)
def copy_json(backup_dir: Path, pack_dir: Path, dry_run: bool):
    setting_path = pack_dir / "path.json"
    copy_to = backup_dir / pack_dir.name / "path.json"
    if not dry_run:
        shutil.copy2(setting_path, copy_to)
    LOGGER.info("Copied: %s -> %s", setting_path, copy_to)


@recording(LOGGER)
def backup_dst(path_conf: PathConfig, backup_dir: Path, dry_run: bool):
    dst_path = path_conf.dst
    if not dst_path.exists():
        LOGGER.debug("%s is not found.", dst_path)
        return

    backup_path = backup_dir / path_conf.src_relative
    backup_path_dir = backup_path.parent
    if not backup_path_dir.exists():
        LOGGER.debug("%s is not found.", backup_path)
        if not dry_run:
            backup_path_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Create: %s", backup_path_dir)

    if dst_path.is_symlink():
        return

    if dst_path.is_file():
        if not dry_run:
            shutil.copy2(dst_path, backup_path)
        LOGGER.info("Copied: %s -> %s", dst_path, backup_path)
        return

    if dst_path.is_dir():
        if not dry_run:
            shutil.copytree(dst_path, backup_path, dirs_exist_ok=True)
        LOGGER.info("Copied: %s -> %s", dst_path, backup_path)
        return

    LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
    raise RuntimeError("%s is invalid." % path_conf)


@recording(LOGGER)
def cleanup_dst(path_conf: PathConfig, dry_run: bool):
    dst_path = path_conf.dst
    if not dst_path.exists():
        LOGGER.debug("%s is not found.", dst_path)
        return

    if dst_path.is_file():
        if not dry_run:
            dst_path.unlink()
        LOGGER.info("Deleted: %s", dst_path)
        return

    if dst_path.is_dir():
        if not dry_run:
            shutil.rmtree(dst_path)
        LOGGER.info("Deleted: %s", dst_path)
        return

    LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
    raise RuntimeError("%s is invalid." % path_conf)


@recording(LOGGER)
def link_dst_to_src(path_conf: PathConfig, dry_run: bool):
    src_path = path_conf.src
    dst_path = path_conf.dst

    if not src_path.exists():
        LOGGER.warning("%s is not found. Broken link will be created.", src_path)

    if src_path.is_dir():
        if not dry_run:
            dst_path.symlink_to(src_path, target_is_directory=True)
        LOGGER.info("Linked: %s <- %s", src_path, dst_path)
        return

    if not dry_run:
        dst_path.symlink_to(src_path)
    LOGGER.info("Linked: %s <- %s", src_path, dst_path)
    return


@recording(LOGGER)
def main(
        package_base: Path,
        home_dir: Path,
        is_restore: bool = False,
        is_dry_run: bool = False,
):
    if is_dry_run:
        handle = logging.StreamHandler(sys.stdout)
        handle.setLevel(logging.INFO)
        handle.setFormatter(logging.Formatter("DRY-RUN: %(message)s"))
        LOGGER.addHandler(handle)

    LOGGER.info("Reading each path.json...")
    path_config_list: list[PathConfig] = []
    for pack in iter_package(package_base):
        setting_path = pack / "path.json"
        with setting_path.open() as f:
            LOGGER.debug("Opened %s.", setting_path)
            path_obj = json.load(f)
            LOGGER.debug("Loaded %s.", path_obj)

        path_config_list.extend(check_convert_json(json_obj=path_obj, pack_path=pack, home_dir=home_dir))
    LOGGER.debug("path configs: %s", path_config_list)
    LOGGER.info("...done.")

    LOGGER.info("Set upping backup...")
    backup_dir = home_dir / ".dotbackup"
    for pack in iter_package(package_base):
        backup_pack = backup_dir / pack.name
        if not backup_pack.exists():
            if not is_dry_run:
                backup_pack.mkdir(parents=True, exist_ok=True)
            LOGGER.info("Created: %s", backup_pack)
        copy_json(backup_dir=backup_dir, pack_dir=pack, dry_run=is_dry_run)
    LOGGER.info("...done.")

    LOGGER.info("Back upping old dotfiles...")
    for path_conf in path_config_list:
        backup_dst(path_conf=path_conf, backup_dir=backup_dir, dry_run=is_dry_run)
    LOGGER.info("...done.")


#    LOGGER.info("Reading each path.json...")
#    path_config_list: list[PathConfig] = []
#    for pack in iter_package(package_base):
#        setting_path = pack / "path.json"
#
#    #    path_config_list.extend(check_convert_json(json_obj=json_obj, pack_path=pack, home_dir=home_dir))
#    LOGGER.debug("path configs: %s", path_config_list)
#    LOGGER.info("...done.")
#
#    LOGGER.info("Set upping backup...")
#    backup_dir = home_dir / ".dotbackup"
#    for pack in iter_package(package_base):
#        backup_pack = backup_dir / pack.name
#        if not backup_pack.exists():
#            if not is_dry_run:
#                backup_pack.mkdir(parents=True, exist_ok=True)
#            LOGGER.info("Created: %s", backup_pack)
#        copy_json(backup_dir=backup_dir, pack_dir=pack, dry_run=is_dry_run)
#    LOGGER.info("...done.")
#
#    LOGGER.info("Back upping old dotfiles...")
#    for path_conf in path_config_list:
#        backup_dst(path_conf=path_conf, backup_dir=backup_dir, dry_run=is_dry_run)
#    LOGGER.info("...done.")
#
#    LOGGER.info("Cleaning upping old dotfiles...")
#    for path_conf in path_config_list:
#        cleanup_dst(path_conf=path_conf, dry_run=is_dry_run)
#    LOGGER.info("...done.")
#
#    LOGGER.info("Linking to new dotfiles...")
#    for path_conf in path_config_list:
#        link_dst_to_src(path_conf=path_conf, dry_run=is_dry_run)
#    LOGGER.info("...done.")


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

    handle = logging.FileHandler(Path(__file__).parent / 'dotfiles.log')
    handle.setLevel(logging.DEBUG)
    handle.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-8s]: %(message)s"))
    LOGGER.addHandler(handle)

    main(
        package_base=Path.cwd(),
        home_dir=Path.home(),
        is_restore=args.restore,
        is_dry_run=args.dry_run,
    )
