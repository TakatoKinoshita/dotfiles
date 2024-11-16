#! /usr/bin/env python3

import json
import logging
import shutil
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import wraps, lru_cache
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
    dst: Path


json_scalar = bool | int | float | str
json_type = json_scalar | list["json_type"] | dict[str, "json_type"]


def iter_package(package_base: Path):
    for p in package_base.iterdir():
        if not p.is_dir():
            continue
        if p.name.startswith("."):
            continue
        if p.name.startswith("_"):
            continue
        yield p


@recording(LOGGER)
@lru_cache
def cache_load_json(path: Path) -> json_type:
    with path.open() as f:
        LOGGER.debug("Opened %s.", path)
        json_obj = json.load(f)
        LOGGER.debug("Loaded %s.", json_obj)
    return json_obj


@recording(LOGGER)
def check_json(json_obj: json_type):
    if isinstance(json_obj, json_scalar):
        LOGGER.error("path.json must be JSON object or array of objects. But got %s.", json_obj)
        raise TypeError("%s is invalid." % json_obj)

    json_obj = normalize_json(json_obj)
    for entry in json_obj:
        is_home = entry["is_home"]
        if not isinstance(is_home, bool):
            LOGGER.error('value of key "is_home" must be boolean. But got %s.', is_home)
            raise TypeError("%s is invalid." % is_home)

        try:
            Path(entry["src"])
            Path(entry["dst"])
        except KeyError:
            LOGGER.error('key "src" or "dst" not found in "%s".', entry)
            raise
        except TypeError:
            LOGGER.error('key "src" and "dst" must be valid path. But got "%s".', entry)
            raise
        except:
            LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
            raise


@recording(LOGGER)
def normalize_json(json_obj: json_type) -> list[json_type]:
    if isinstance(json_obj, dict):
        json_obj = [json_obj]
    for entry in json_obj:
        entry["is_home"] = entry.get("is_home", True)
    return json_obj


@recording(LOGGER)
def list_json_to_config(json_obj: list[json_type], home_dir: Path, ) -> list[PathConfig]:
    res = []
    for entry in json_obj:
        dst = home_dir / entry["dst"] if entry["is_home"] else entry["dst"]
        res.append(PathConfig(src=entry["src"], dst=dst))
    return res


@recording(LOGGER)
def backup_dst(dst: Path, backup_dir: Path, dry_run: bool):
    if not dst.exists():
        LOGGER.debug("%s is not found.", dst)
        return

    if dst.is_symlink():
        LOGGER.debug("%s is a symbolic link.", dst)
        return

    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    copy_to = backup_dir / dst.name
    if dst.is_file():
        LOGGER.debug("%s is a file.", dst)
        if not dry_run:
            shutil.copy2(dst, copy_to)
        LOGGER.info("Copied: %s -> %s", dst, copy_to)
        return
    if dst.is_dir():
        LOGGER.debug("%s is a directory.", dst)
        if not dry_run:
            shutil.copytree(dst, copy_to, dirs_exist_ok=True)
        LOGGER.info("Copied: %s -> %s", dst, copy_to)
        return

    LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
    raise RuntimeError("%s is invalid." % dst)


@recording(LOGGER)
def generate_backup_json(configs: list[PathConfig], backup_dir: Path,) -> list[json_type] | None:
    res = []
    for config in configs:
        dst = config.dst
        copy_to = backup_dir / dst.name
        if copy_to.exists():
            res.append({"is_home": False, "src": copy_to, "dst": dst})
    return res if res else None


@recording(LOGGER)
def write_backup_json(json_bk: list[json_type] | None, backup_dir: Path, dry_run: bool) -> None:
    if json_bk is None:
        return
    if dry_run:
        return

    save_to = backup_dir / "path.json"
    save_to.write_text(json.dumps(json_bk))
    LOGGER.info("Created: %s", save_to)


@recording(LOGGER)
def cleanup_dst(dst: Path, dry_run: bool):
    if not dst.exists():
        LOGGER.debug("%s is not found.", dst)
        return

    if dst.is_file():
        if not dry_run:
            dst.unlink()
        LOGGER.info("Deleted: %s", dst)
        return

    if dst.is_dir():
        if not dry_run:
            shutil.rmtree(dst)
        LOGGER.info("Deleted: %s", dst)
        return

    LOGGER.error("Unexpected error: %s", sys.exc_info()[0])
    raise RuntimeError("%s is invalid." % dst)


@recording(LOGGER)
def link_dst_to_src(path_conf: PathConfig, dry_run: bool):
    src = path_conf.src
    dst = path_conf.dst

    if not src.exists():
        LOGGER.warning("%s is not found. Broken link will be created.", src)

    if src.is_dir():
        if not dry_run:
            dst.symlink_to(src, target_is_directory=True)
        LOGGER.info("Linked: %s <- %s", src, dst)
        return

    if not dry_run:
        dst.symlink_to(src)
    LOGGER.info("Linked: %s <- %s", src, dst)
    return


@recording(LOGGER)
def main(package_base: Path, home_dir: Path, is_restore: bool = False, is_dry_run: bool = False, ):
    if is_dry_run:
        handle = logging.StreamHandler(sys.stdout)
        handle.setLevel(logging.INFO)
        handle.setFormatter(logging.Formatter("DRY-RUN: %(message)s"))
        LOGGER.addHandler(handle)

    LOGGER.info("Checking each path.json...")
    for path in iter_package(package_base):
        json_path = path / "path.json"
        json_obj = cache_load_json(json_path)
        check_json(json_obj)
    LOGGER.info("...done")

    if is_dry_run:
        LOGGER.warning("Notice that generation of path.json will skipped in dry run.")
        LOGGER.warning("In other words, the operation will be informed even if path.json will actually be created.")
    for path in iter_package(package_base):
        LOGGER.info("Start process for %s", path.name)

        LOGGER.info("Loading path.json...")
        json_path = path / "path.json"
        json_obj = cache_load_json(json_path)
        json_obj = normalize_json(json_obj)
        confs = list_json_to_config(json_obj, home_dir)
        LOGGER.info("...done")

        LOGGER.info("Back upping old dotfiles...")
        backup_dir = home_dir / ".dotbackup" / path.name
        for conf in confs:
            backup_dst(dst=conf.dst, backup_dir=backup_dir, dry_run=is_dry_run)
        LOGGER.info("...done")

        LOGGER.info("Generating backup json.path...")
        json_bk = generate_backup_json(confs, backup_dir)
        write_backup_json(json_bk=json_bk, backup_dir=backup_dir, dry_run=is_dry_run)
        LOGGER.info("...done")

        LOGGER.info("Cleaning up old dotfiles...")
        for conf in confs:
            cleanup_dst(dst=conf.dst, dry_run=is_dry_run)
        LOGGER.info("...done")

        LOGGER.info("Linking to new dotfiles...")
        for conf in confs:
            link_dst_to_src(path_conf=conf, dry_run=is_dry_run)
        LOGGER.info("...done.")

        LOGGER.info("End process for %s", path.name)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--restore", action="store_true", help="Restore dotfiles from backup.")
    parser.add_argument("--dry-run", action="store_true", help="Test run without actual file operations.")
    args = parser.parse_args()

    handle = logging.FileHandler(Path(__file__).parent / 'dotfiles.log')
    handle.setLevel(logging.DEBUG)
    handle.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-8s]: %(message)s"))
    LOGGER.addHandler(handle)

    main(package_base=Path.cwd(), home_dir=Path.home(), is_restore=args.restore, is_dry_run=args.dry_run, )
