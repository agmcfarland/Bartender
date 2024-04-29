import pytest
import os
from os.path import join as pjoin
from glob import glob
import re
import pandas as pd
from unittest.mock import patch, Mock
from Utils.SampleRead import SampleRead
from Utils.Experimental import Experimental
from Utils.SetupManager import SetupManager
from Utils.Stock import Stock


@pytest.fixture
def unique_groups():
    df = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample2", "sample3"],
            "biological_group": ["group1", "group2", "group3"],
            "cell_type": ["plasma", "plasma", "plasma"],
            "time_point": [0, 1, 2],
            "time_point_description": ["dpi", "dpi", "dpi"],
            "organ": ["blood", "blood", "blood"],
            "input_template": [1000, 1000, 1000],
            "genetic_source": ["dna", "dna", "dna"],
            "R1": [
                "path/to/sample1_R1.fastq.gz",
                "path/to/sample2_R1.fastq.gz",
                "path/to/sample3_R1.fastq.gz",
            ],
            "R2": [
                "path/to/sample1_R2.fastq.gz",
                "path/to/sample2_R2.fastq.gz",
                "path/to/sample3_R2.fastq.gz",
            ],
        }
    )
    df["standard_sample_name"] = df.apply(
        lambda x: x["biological_group"]
        + "_"
        + x["cell_type"]
        + "_"
        + str(int(round(x["time_point"])))
        + "_"
        + x["organ"]
        + "_"
        + x["genetic_source"],
        axis=1,
    )

    return df


@pytest.fixture
def repeat_groups():
    df = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample2", "sample3"],
            "biological_group": ["group1", "group1", "group3"],
            "cell_type": ["plasma", "plasma", "plasma"],
            "time_point": [0, 0, 2],
            "time_point_description": ["dpi", "dpi", "dpi"],
            "organ": ["blood", "blood", "blood"],
            "input_template": [1000, 1000, 1000],
            "genetic_source": ["dna", "dna", "dna"],
            "R1": [
                "path/to/sample1_R1.fastq.gz",
                "path/to/sample2_R1.fastq.gz",
                "path/to/sample3_R1.fastq.gz",
            ],
            "R2": [
                "path/to/sample1_R2.fastq.gz",
                "path/to/sample2_R2.fastq.gz",
                "path/to/sample3_R2.fastq.gz",
            ],
        }
    )
    df["standard_sample_name"] = df.apply(
        lambda x: x["biological_group"]
        + "_"
        + x["cell_type"]
        + "_"
        + str(int(round(x["time_point"])))
        + "_"
        + x["organ"]
        + "_"
        + x["genetic_source"],
        axis=1,
    )

    return df


@pytest.fixture
def base_barcode_result():
    return pd.DataFrame(
        {
            "barcode": [
                "GCGGCCAGCACTTGAAGTTTTTGTAGGTGGCCGCA",
                "GCGGCCACCTACCCATGATAGCAGTGCTGGCCGCA",
                "GCGGCCACCTACTATCCTGACCAGTGCTGGCCGCA",
                "GCGGCCACCTACTAGACTCGTGAGTGCTGGCCGCA",
                "GCGGCCAGCACTGCTGTTGAACGTAGGTGGCCGCA",
                "GCGGCCAGCACTCTGAAACTTAGTAGGTGGCCGCA",
            ],
            "to_replace": [13, 6, 3, 3, 3, 2],
        }
    )


@pytest.fixture
def mock_stock():
    mock_stock = Mock()
    return mock_stock


@pytest.fixture
def mock_setup_manager():
    mock_setup_manager = Mock()
    mock_setup_manager.run_paths.stock_barcodes_raw = "/path/to/raw.csv"
    mock_setup_manager.run_paths.temp = "/path/to/temp"
    mock_setup_manager.run_paths.experimental = "/path/to/experimental"
    return mock_setup_manager


def test_pass(base_barcode_result, unique_groups):
    collect_df = []
    for _, row in unique_groups.iterrows():
        df = base_barcode_result.copy(deep=True)
        df.rename({"to_replace": row["standard_sample_name"]}, inplace=True, axis=1)
        collect_df.append(df)


def test_experimental_barcodes_to_process_repeat_samples(
    mock_setup_manager, repeat_groups
):
    """
    pytest -sv tests/test_Experimental.py::test_experimental_barcodes_to_process_repeat_samples
    """
    mock_setup_manager.experimental = repeat_groups

    experimental_samples = Experimental(
        setup_manager=mock_setup_manager, barcode_length=35, stock=mock_stock
    )

    experimental_samples._samples_to_process()

    assert experimental_samples.incoming_samples["group1_plasma_0_blood_dna"][
        "path"
    ] == [
        "/path/to/temp/sample1/group1_plasma_0_blood_dna_barcode.csv",
        "/path/to/temp/sample2/group1_plasma_0_blood_dna_barcode.csv",
    ]

    assert experimental_samples.incoming_samples["group3_plasma_2_blood_dna"][
        "path"
    ] == ["/path/to/temp/sample3/group3_plasma_2_blood_dna_barcode.csv"]


def test_experimental_barcodes_to_process_repeat_samples_merging(
    mock_setup_manager, repeat_groups, unique_groups, base_barcode_result
):
    """
    pytest -sv tests/test_Experimental.py::test_experimental_barcodes_to_process_repeat_samples_merging
    """
    mock_setup_manager.experimental = repeat_groups

    mock_setup_manager.record.experimental = unique_groups

    samples = [
        "group1_plasma_0_blood_dna",
        "group1_plasma_0_blood_dna",
        "group3_plasma_2_blood_dna",
    ]

    list_of_mock_csv = []
    z = 0
    for i in samples:
        df = base_barcode_result.copy(deep=True)

        df["to_replace"] = df["to_replace"] + z

        df.rename({"to_replace": i}, inplace=True, axis=1)

        list_of_mock_csv.append(df)

        z += 1

    experimental_samples = Experimental(
        setup_manager=mock_setup_manager, barcode_length=35, stock=mock_stock
    )

    with patch("pandas.read_csv") as mock_read_csv:
        mock_read_csv.side_effect = list_of_mock_csv

        experimental_samples._samples_to_process()

        experimental_samples._get_counts_of_incoming_samples()

        assert experimental_samples.incoming_samples["group1_plasma_0_blood_dna"][
            "barcode"
        ].shape == (6, 3)

        assert experimental_samples.incoming_samples["group3_plasma_2_blood_dna"][
            "barcode"
        ].shape == (6, 2)


def test_merge_incoming_samples_with_existing_samples(
    mock_setup_manager, repeat_groups, unique_groups, base_barcode_result
):
    """
    pytest -sv tests/test_Experimental.py::test_merge_incoming_samples_with_existing_samples
    """

    mock_setup_manager.experimental = repeat_groups

    mock_setup_manager.record.experimental = unique_groups

    samples = [
        "group1_plasma_0_blood_dna",
        "group1_plasma_0_blood_dna",
        "group3_plasma_2_blood_dna",
        "group1_plasma_0_blood_dna_AAAAAAAA00000000",
        "group3_plasma_2_blood_dna_AAAAAAAA00000000",
    ]

    list_of_mock_csv = []
    z = 0
    for i in samples:
        df = base_barcode_result.copy(deep=True)

        df.drop(index=z, inplace=True)

        df["to_replace"] = df["to_replace"] + z

        df.rename({"to_replace": i}, inplace=True, axis=1)

        list_of_mock_csv.append(df)

        z += 1

    with patch("pandas.read_csv") as mock_read_csv:
        with patch("Utils.Experimental.os.path.exists") as mock_path_exists:
            experimental_samples = Experimental(
                setup_manager=mock_setup_manager, barcode_length=35, stock=mock_stock
            )

            mock_path_exists.return_value = True

            mock_read_csv.side_effect = list_of_mock_csv

            with patch.object(
                mock_setup_manager.run_paths,
                "experimental",
                new="/path/to/experimental",
            ):
                experimental_samples._samples_to_process()

                experimental_samples._get_counts_of_incoming_samples()

                experimental_samples._merge_incoming_samples_with_existing_samples()

                assert experimental_samples.incoming_samples[
                    "group1_plasma_0_blood_dna"
                ]["barcode"].shape == (6, 4)

                assert experimental_samples.incoming_samples[
                    "group3_plasma_2_blood_dna"
                ]["barcode"].shape == (6, 3)


@pytest.fixture
def experimental_record_2():
    df = pd.DataFrame(
        {
            "sample_name": ["sample1", "sample2", "sample3"],
            "biological_group": ["group1", "group1", "group3"],
            "cell_type": ["plasma", "plasma", "plasma"],
            "time_point": [0, 0, 2],
            "time_point_description": ["dpi", "dpi", "dpi"],
            "organ": ["blood", "blood", "blood"],
            "input_template": [5000, 5000, 1000],
            "genetic_source": ["dna", "dna", "dna"],
            "R1": [
                "path/to/sample1_R1.fastq.gz",
                "path/to/sample2_R1.fastq.gz",
                "path/to/sample3_R1.fastq.gz",
            ],
            "R2": [
                "path/to/sample1_R2.fastq.gz",
                "path/to/sample2_R2.fastq.gz",
                "path/to/sample3_R2.fastq.gz",
            ],
        }
    )

    df2 = pd.DataFrame(
        {
            "sample_name": ["sample4", "sample5", "sample6"],
            "biological_group": ["group1", "group1", "group3"],
            "cell_type": ["plasma", "plasma", "plasma"],
            "time_point": [0, 0, 3],
            "time_point_description": ["dpi", "dpi", "dpi"],
            "organ": ["blood", "blood", "blood"],
            "input_template": [5000, 1000, 1000],
            "genetic_source": ["dna", "dna", "dna"],
            "R1": [
                "path/to/sample1_R1.fastq.gz",
                "path/to/sample2_R1.fastq.gz",
                "path/to/sample3_R1.fastq.gz",
            ],
            "R2": [
                "path/to/sample1_R2.fastq.gz",
                "path/to/sample2_R2.fastq.gz",
                "path/to/sample3_R2.fastq.gz",
            ],
        }
    )

    df = pd.concat([df, df2])

    df["standard_sample_name"] = df.apply(
        lambda x: x["biological_group"]
        + "_"
        + x["cell_type"]
        + "_"
        + str(int(round(x["time_point"])))
        + "_"
        + x["organ"]
        + "_"
        + x["genetic_source"],
        axis=1,
    )

    return df


@pytest.fixture
def example_filtered_stock(test_data_dir):
    return pd.read_csv(
        pjoin(test_data_dir, "experimental", "stock_barcodes_filtered.csv")
    )


@pytest.fixture
def raw_animal_barcode_1(test_data_dir):
    return pd.read_csv(
        pjoin(
            test_data_dir, "experimental", "animal1_unknown_27_plasma_dna_barcode.csv"
        )
    )


@pytest.fixture
def mock_setup_manager(test_data_dir):
    mock_setup_manager = Mock()
    mock_setup_manager.run_paths.stock_barcodes_raw = "/path/to/raw.csv"
    mock_setup_manager.run_paths.temp = "/path/to/temp"
    return mock_setup_manager


def test_apply_barcode_filters(
    example_filtered_stock, raw_animal_barcode_1, mock_stock, mock_setup_manager
):
    """
    pytest -sv tests/test_Experimental.py::test_apply_barcode_filters
    """
    mock_stock._read_filtered_stock_barcodes.return_value = example_filtered_stock

    experimental_samples = Experimental(
        setup_manager=mock_setup_manager, barcode_length=35, stock=mock_stock
    )

    assert experimental_samples._adjust_filtered_stock_format(
        example_filtered_stock
    ).shape == (4092, 2)

    with patch.object(
        experimental_samples, "_get_mean_template_value", return_value=5000
    ):
        df_result = experimental_samples._apply_barcode_filters(
            standard_sample_name="woop_woop",
            df=raw_animal_barcode_1.iloc[:500, :],
            stock_barcodes=experimental_samples._adjust_filtered_stock_format(
                example_filtered_stock
            ),
        )

        assert df_result.shape == (477, 12)

        assert df_result[df_result["trusted_barcode_check"] == "pass"].shape == (
            466,
            12,
        )

        assert df_result[df_result["trusted_barcode_check"] == "fail"].shape == (11, 12)
