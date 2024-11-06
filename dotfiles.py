import json
import sys
import logging

from argparse import ArgumentParser
from functools import wraps
from inspect import signature
from pathlib import Path
from dataclasses import dataclass

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
json_type = json_scalar | list["json_obj"] | dict[str, "json_obj"]

@recording(LOGGER)
def check_convert_json(
        src_base: Path,
        home_dir: Path,
        json_obj: json_type,
) -> list[PathConfig]:
    if isinstance(json_obj, json_scalar):
        LOGGER.error("path.json must be JSON object or array of objects. But got %s.", json_obj)
        raise RuntimeError("%s is invalid." % json_obj)

    if isinstance(json_obj, dict):
        json_obj = [json_obj]

    path_list: list[PathConfig] = []
    for conf in json_obj:
        is_home = conf.get("is_home", True)
        if not isinstance(is_home, bool):
            LOGGER.error('value of key "is_home" must be boolean. But got %s.', is_home)
            raise RuntimeError("%s is invalid." % is_home)

        try:
            src = src_base / Path(conf["src"])
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

        path_conf = PathConfig(src, dst)
        LOGGER.debug("Converted: %s -> %s", conf, path_conf)
        path_list.append(path_conf)

    return path_list

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
    for pack in package_base.iterdir():
        if not pack.is_dir():
            continue

        setting_path = pack / "path.json"
        with open(setting_path) as f:
            LOGGER.debug("Opened %s.", setting_path)
            path_obj = json.load(f)
            LOGGER.debug("Loaded %s.", path_obj)

        path_config_list.extend(check_convert_json(
            src_base=pack,
            home_dir=home_dir,
            json_obj=path_obj,
        ))
    LOGGER.debug("path configs: %s", path_config_list)
    LOGGER.info("...done.")


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

    main(
        package_base=Path.cwd(),
        home_dir=Path.home(),
        is_restore=args.restore,
        is_dry_run=args.dry_run,
    )
