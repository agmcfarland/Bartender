from Utils.FilePaths import FilePaths
from unittest.mock import patch, call
import pytest


@pytest.fixture
def mock_os_makedirs():
    with patch("Utils.FilePaths.os.makedirs") as mocked_makedirs:
        yield mocked_makedirs


def test_make_work_dir_tree(mock_os_makedirs):
    work_dir = "/path/to/work/dir"
    file_paths = FilePaths(work_dir)

    file_paths.make_work_dir_tree()

    expected_calls = [
        call(work_dir, exist_ok=True),
        call(work_dir + "/record", exist_ok=True),
        call(work_dir + "/stock", exist_ok=True),
        call(work_dir + "/experimental", exist_ok=True),
        call(work_dir + "/output", exist_ok=True),
    ]

    assert mock_os_makedirs.call_args_list == expected_calls
