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
        log_level (str): the log level

    """
    logging.basicConfig(
        level=log_level,
        format="[%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def name_plate(entries: List[str]) -> None:
    """renders the songbird entrypoint name plate

    Args:
        entries (List[str]): add additional entries to the nameplate via this list
    """
    # load project version from file
    print("===============================")
    print("=----Welcome to songbird🐦----=")
    print("===============================")
    print(f"--songbirdcore {version}")
    for entry in entries:
        print(entry)
    print("===============================")
    print("Message from developer:")
    print(
        "\t- dependencies have been upgraded, make sure you have run 'playwright install'."
    )
    print(
        "\t- If you encounter errors, please create an issue here https://github.com/cboin1996/songbirdcore/issues/"
    )
    print(
        f"At the main menu, type one of {[mode.value for mode in modes.Modes]} to switch modes!"
    )


def fname_duper(fname: str, limit: int, count: int, dup_key: str) -> Optional[str]:
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


def remove_illegal_characters(filename) -> str:
    """
    Used for stripping file names of illegal characters used for saving

    Args:
        filename (str): the file's name to strip illegal characters from

    Returns:
        str: stripped file name
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


def pretty_list_of_basemodel_printer(
    list_of_dicts: List[BaseModel], ignore_keys: Optional[List[str]] = None
):
    """
    renders a list to stdio given a list of pydantic BaseModel objects

    Args:
        list_of_dicts (List[BaseModel]): list of dictionaries to print
        ignore_keys (Optional[List[str]], optional): any keys/fields in BaseModel not to print
    """
    i = len(list_of_dicts) - 1
    logger.info("------------------------")
    for element in reversed(list_of_dicts):
        logger.info(i)
        for k, v in element.model_dump().items():
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
    """print a list to stdio

    Args:
        lyst (List): the list to print
    """
    for idx, item in enumerate(lyst):
        logger.info(f"\t [{idx}] - {item}")
