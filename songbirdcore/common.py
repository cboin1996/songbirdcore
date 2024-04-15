from typing import List
import logging
import glob
import os, sys
import tomllib

from typing import Optional
import logging
from pydantic import BaseModel

from .models import itunes_api, modes
from .version import version

logger = logging.getLogger(__name__)


def load_version(toml_path: str):
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
    return data


def set_logger_config_globally(log_level=logging.INFO) -> None:
    """Sets the python logging module settings for output
    to stdout and to file.
    Args:
        timestamp (str): the timestamp to name the log file.
    """
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def name_plate(entries: List[str]):
    """
    Produces the application nameplate.
    Args: two command line argumates, debug mode on or off, operating system
    Returns: operating system
    """
    # load project version from file
    print("===============================")
    print("=----Welcome to songbird🐦----=")
    print("===============================")
    print(f"--songbirdcore {version}")
    for entry in entries:
        print(entry)
    print("===============================")
    print(
        "Message to users: Currently yt-dlp version is held back and producing errors."
    )
    print("These errors will be fixed once the upstream dependencies match yt-dlps.")
    print(
        f"At the main menu, type one of {[mode.value for mode in modes.Modes]} to switch modes!"
    )


def fname_duper(fname: str, limit: int, count: int, dup_key: str):
    """Generates a duplicate filename for when a filename already exists

    Args:
        fname (str): filename
        limit (int): a limit of dups before quitting the attempt
        count (int): recursive count tracker
        dup_key (str): the key to use as the duplicate addon

    Returns:
        Optional[str]: the modified filename, or None if the limit has been reached.
    """
    fname_split = os.path.splitext(fname)
    fname_noext = fname_split[0]
    ext = fname_split[1]
    if count == limit:
        logger.error(
            f"Max retry limit {limit} reached for fname {fname}. Please try changing some filenames and try again later."
        )
        return None
    if os.path.exists(fname):
        fname = fname_duper(fname_noext + dup_key + ext, limit, count + 1, dup_key)

    return fname


def remove_illegal_characters(filename):
    """
    Used for stripping file names of illegal characters used for saving
    Args:
        filename(str): the file's name to strip
    Returns: stipped file name
    """
    return (
        filename.replace("\\", "")
        .replace('"', "")
        .replace("/", "")
        .replace("*", "")
        .replace("?", "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
        .replace("'", "")
        .replace(":", "")
    )


def find_file(path: str, filename: str) -> List[str]:
    """Simple glob search for a file

    Args:
        path (str): the path to the root folder to search within
        filename (str): the filename (supports glob patterns)

    Returns:
        List[str]: list of paths found that match
    """
    paths = glob.glob(os.path.join(path, filename))
    return paths


def pretty_list_of_basemodel_printer(list_of_dicts: List[BaseModel], ignore_keys=None):
    """
    prints list from top down so its more user friendly, items are pretty big
    params:
        list_of_dicts: list of dictionaries to print
        ignore_keys: any keys not to print
    """
    i = len(list_of_dicts) - 1
    logger.info("------------------------")
    for element in reversed(list_of_dicts):
        logger.info(i)
        for k, v in element.dict().items():
            if ignore_keys is not None:
                if (
                    k not in ignore_keys
                ):  # print the key and value if not in ignore_keys or special_dict
                    print("\t%s - %s" % (k, v))

            else:  # (default case) print the key and value
                print("\t%s - %s" % (k, v))
        i -= 1
        print("------------------------")


def pretty_lst_printer(lyst: List):
    for idx, item in enumerate(lyst):
        logger.info(f"\t [{idx}] - {item}")
