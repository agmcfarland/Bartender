import pytest
import pandas as pd
import re
import os
from unittest.mock import patch, call
from Utils.FilePaths import FilePaths
from Utils.Record import Record


@pytest.fixture
def mock_run_paths():
    return FilePaths(work_dir="/path/to/workdir")


def test_load_records_pass(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    pytest -sv tests/test_Record.py::test_load_records_pass
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_experimental = experimental_record.copy(deep=True)

            df_test_stock = stock_record.copy(deep=True)

            mock_path_exists.side_effect = [True, True]

            mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

            record.load_experimental_record()

            assert record.experimental.equals(df_test_experimental)

            record.load_stock_record()

            assert record.stock.equals(df_test_stock)

def test_unique_stock_biological_groups_pass(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    python -m slipcover -m pytest -sv tests/unit/test_Record.py::test_unique_stock_biological_groups_pass
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_stock = stock_record.copy(deep=True)

            mock_path_exists.side_effect = [True]

            mock_read_csv.side_effect = [df_test_stock]

            record.load_stock_record()

            assert record.unique_stock_biological_groups() == ['group1', 'group2', 'group3']


def test_update_records_pass(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    pytest -sv tests/test_Record.py::test_update_records_pass
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_experimental = experimental_record.copy(deep=True)

            df_test_stock = stock_record.copy(deep=True)

            mock_path_exists.side_effect = [True, True]

            mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

            record.load_experimental_record()

            record.update_experimental_record(table_to_add=expected_experimental_output)

            expected_experimental_df = pd.concat(
                [df_test_experimental, expected_experimental_output]
            )

            assert record.experimental.equals(expected_experimental_df)

            record.load_stock_record()

            record.update_stock_record(table_to_add=expected_stock_output)

            expected_stock_df = pd.concat([df_test_stock, expected_stock_output])

            assert record.stock.equals(expected_stock_df)


def test_update_records_fails_R1(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    pytest -sv tests/test_Record.py::test_update_records_fails_R1
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_experimental = experimental_record.copy(deep=True)

            df_test_experimental["R1"] = "/path/to/sample1_R1.fastq.gz"

            df_test_stock = stock_record.copy(deep=True)

            df_test_stock["R1"] = "/path/to/stock_R1.fastq.gz"

            mock_path_exists.side_effect = [True, True]

            mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

            record.load_experimental_record()

            with pytest.raises(ValueError, match="R1 must must be unique"):
                record.update_experimental_record(
                    table_to_add=expected_experimental_output
                )

            record.load_stock_record()

            with pytest.raises(ValueError, match="R1 must must be unique"):
                record.update_stock_record(table_to_add=expected_stock_output)


def test_update_records_fails_R2(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    pytest -sv tests/test_Record.py::test_update_records_fails_R2
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_experimental = experimental_record.copy(deep=True)

            df_test_experimental["R2"] = "/path/to/sample1_R2.fastq.gz"

            df_test_stock = stock_record.copy(deep=True)

            df_test_stock["R2"] = "/path/to/stock_R2.fastq.gz"

            mock_path_exists.side_effect = [True, True]

            mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

            record.load_experimental_record()

            with pytest.raises(ValueError, match="R2 must must be unique"):
                record.update_experimental_record(
                    table_to_add=expected_experimental_output
                )

            record.load_stock_record()

            with pytest.raises(ValueError, match="R2 must must be unique"):
                record.update_stock_record(table_to_add=expected_stock_output)


def test_update_records_fails_non_unique_sample(
    mock_run_paths,
    stock_record,
    experimental_record,
    expected_experimental_output,
    expected_stock_output,
):
    """
    pytest -sv tests/test_Record.py::test_update_records_fails_non_unique_sample
    """
    with patch("pandas.read_csv") as mock_read_csv:
        with patch("os.path.exists") as mock_path_exists:
            record = Record(run_paths=mock_run_paths)

            df_test_experimental = experimental_record.copy(deep=True)

            df_test_experimental["standard_sample_name"] = "all_the_same"

            df_test_experimental["sample_name"] = "all_the_same_"

            df_test_stock = stock_record.copy(deep=True)

            df_test_stock["standard_sample_name"] = "all_the_same"

            df_test_stock["sample_name"] = "all_the_same_"

            mock_path_exists.side_effect = [True, True]

            mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

            record.load_experimental_record()

            with pytest.raises(
                ValueError, match="sample_name_standard_sample_name must must be unique"
            ):
                record.update_experimental_record(
                    table_to_add=expected_experimental_output
                )

            record.load_stock_record()

            with pytest.raises(
                ValueError, match="sample_name_standard_sample_name must must be unique"
            ):
                record.update_stock_record(table_to_add=expected_stock_output)
