import pytest
import pandas as pd
import shutil
from os.path import join as pjoin
import os
from unittest.mock import patch
from src.Bartender.Utils.SetupManager import SetupManager
from src.Bartender.Utils.BarcodeProcessor import BarcodeProcessor
import time


@pytest.fixture
def test_path():
    return pjoin(os.getcwd(), "tests", "data", "ete1")


@pytest.fixture
def test_workdir(test_path):
    return pjoin(test_path, "work")


@pytest.fixture
def make_workdir(test_workdir):
    if os.path.exists(test_workdir):
        shutil.rmtree(test_workdir)
    os.makedirs(test_workdir)


@pytest.fixture
def make_small_input_1(test_path):
    df_stock = pd.read_csv(pjoin(test_path, "stock_samples.csv"))

    df_stock = df_stock.iloc[:4]

    df_stock.to_csv(pjoin(test_path, "stock_samples_small_input_1.csv"), index=None)

    df_experimental = pd.read_csv(pjoin(test_path, "experimental_samples.csv"))

    df_experimental = df_experimental.iloc[:4]

    df_experimental.to_csv(
        pjoin(test_path, "experimental_samples_small_input_1.csv"), index=None
    )


@pytest.fixture
def make_small_input_2(test_path):
    df_stock = pd.read_csv(pjoin(test_path, "stock_samples.csv"))

    df_stock = df_stock.iloc[7:9]

    df_stock.to_csv(pjoin(test_path, "stock_samples_small_input_2.csv"), index=None)

    df_experimental = pd.read_csv(pjoin(test_path, "experimental_samples.csv"))

    df_experimental = df_experimental.iloc[7:9]

    df_experimental.to_csv(
        pjoin(test_path, "experimental_samples_small_input_2.csv"), index=None
    )


def test_ete_first_run(
    test_path, make_workdir, test_workdir, make_small_input_1, make_small_input_2
):
    """
    pytest -sv tests/end_to_end/test_simple.py::test_ete_first_run
    """
    make_small_input_1
    make_workdir

    bartender_setup = SetupManager(
        work_dir=test_workdir,
        experimental_file=pjoin(test_path, "experimental_samples_small_input_1.csv"),
        stock_file=pjoin(test_path, "stock_samples_small_input_1.csv"),
    )

    samples = BarcodeProcessor(setup_manager=bartender_setup, barcode_length=35)

    start = time.time()
    samples.process_stock_samples()
    print(time.time() - start)


def test_ete_with_stock_record(
    test_path, make_workdir, test_workdir, make_small_input_1, make_small_input_2
):
    make_small_input_1
    make_small_input_2
    make_workdir

    bartender_setup = SetupManager(
        work_dir=test_workdir,
        experimental_file=pjoin(test_path, "experimental_samples_small_input_1.csv"),
        stock_file=pjoin(test_path, "stock_samples_small_input_1.csv"),
    )

    samples = BarcodeProcessor(setup_manager=bartender_setup, barcode_length=35)

    start = time.time()
    samples.process_stock_samples()
    print(time.time() - start)

    # temp write record
    bartender_setup.record.stock.to_csv(
        pjoin(test_workdir, "record", "stock.csv"), index=None
    )

    print("next")

    bartender_setup = SetupManager(
        work_dir=test_workdir,
        experimental_file=pjoin(test_path, "experimental_samples_small_input_2.csv"),
        stock_file=pjoin(test_path, "stock_samples_small_input_2.csv"),
    )

    samples = BarcodeProcessor(setup_manager=bartender_setup, barcode_length=35)

    start = time.time()
    samples.process_stock_samples()
    print(time.time() - start)


def test_ete_experimental(
    test_path, make_workdir, test_workdir, make_small_input_1, make_small_input_2
):
    """
    pytest -sv tests/end_to_end/test_simple.py::test_ete_experimental
    """
    make_small_input_1
    make_workdir

    bartender_setup = SetupManager(
        work_dir=test_workdir,
        experimental_file=pjoin(test_path, "experimental_samples_small_input_1.csv"),
        stock_file=pjoin(test_path, "stock_samples_small_input_1.csv"),
    )

    samples = BarcodeProcessor(setup_manager=bartender_setup, barcode_length=35)

    start = time.time()
    samples.process_stock_samples()
    print(time.time() - start)

    start = time.time()
    samples.process_experimental_samples()
    print(time.time() - start)
