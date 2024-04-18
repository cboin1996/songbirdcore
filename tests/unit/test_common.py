import pytest
import os, sys, shutil
from pydantic import BaseModel

from songbirdcore import common


@pytest.fixture
def create_test_folder():
    tests_data_folder = os.path.join(sys.path[0], "tests-output")
    if not os.path.exists(tests_data_folder):
        os.mkdir(tests_data_folder)
    yield tests_data_folder
    # test cleanup
    shutil.rmtree(tests_data_folder)


def test_load_data():
    toml_path = os.path.join(sys.path[0], "..", "..", "pyproject.toml")
    data = common.load_toml(toml_path)
    assert data is not None


def test_set_logger_config_globally():
    try:
        common.set_logger_config_globally()
    except Exception as e:
        pytest.fail(f"Unexpected exception {e}!")


def test_name_plate():
    try:
        common.name_plate(entries=["foo"])
    except Exception as e:
        pytest.fail(f"Unexpected exception {e}!")


@pytest.fixture()
def create_dummy_file(create_test_folder):
    fname = os.path.join(create_test_folder, "dummy.txt")

    with open(fname, "w") as f:
        f.write("hello")
    yield fname


def fname_duper(create_dummy_file):

    fname = common.fname_duper(fname=create_dummy_file, limit=2, count=1, dup_key="dup")

    assert fname is not None


def test_fname_duper_fails(create_dummy_file):
    fname = common.fname_duper(fname=create_dummy_file, limit=1, count=1, dup_key="dup")

    assert fname is None


def test_remove_illegal_characters():
    """test remove illegal character"""
    try:
        result = common.remove_illegal_characters("\\\"/*?<>|':")
    except Exception as e:
        pytest.fail(f"Unexpected exception {e}!")

    assert result == ""


def test_find_file(create_dummy_file):
    """test function for finding a file"""
    result = common.find_file(
        path=os.path.dirname(create_dummy_file),
        filename=os.path.basename(create_dummy_file),
    )

    assert len(result) > 0


def test_pretty_list_of_basemodel_printer(capsys):
    """test function runs without exception"""

    class Model(BaseModel):
        foo: str = "bar"

    try:
        common.pretty_list_of_basemodel_printer(list_of_models=[Model()])
    except Exception as e:
        pytest.fail(f"Unexpected exception {e}!")


def test_pretty_list_of_baseModel_printer(capsys):
    """test ignore_keys functionality"""

    class Model(BaseModel):
        foo: str = "bar"
        ignore_me: str = "ignore_me"

    try:
        common.pretty_list_of_basemodel_printer(
            list_of_models=[Model()], ignore_keys=["ignore_me"]
        )
    except Exception as e:
        pytest.fail(f"Unexpected exception {e}!")

    captured = capsys.readouterr()
    assert "ignore_me" not in captured.out


def tests_pretty_lst_printer():
    """test function runs without exception"""
    try:
        common.pretty_lst_printer(["hi", "there"])
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
