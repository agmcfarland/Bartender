
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
	return pjoin(os.getcwd(), 'tests', 'data', 'ete2')

@pytest.fixture
def test_workdir(test_path):
	return pjoin(test_path, 'work')

@pytest.fixture
def make_workdir(test_workdir):
	if os.path.exists(test_workdir):
		shutil.rmtree(test_workdir)
	os.makedirs(test_workdir)

@pytest.fixture
def make_run1_inputs(test_path):
	df_stock = pd.read_csv(pjoin(test_path, 'stock_samplesheet.csv'))

	print(df_stock)

	df_stock = df_stock[df_stock['run_group'] == 'run1']

	df_stock.drop(['run_group'], axis = 1, inplace = True)

	df_stock.to_csv(pjoin(test_path, 'stock_samplesheet_run1.csv'), index = None)

	df_experimental = pd.read_csv(pjoin(test_path, 'experimental_samplesheet.csv'))

	df_experimental = df_experimental[df_experimental['run_group'] == 'run1']

	df_experimental.drop(['run_group'], axis = 1, inplace = True)

	df_experimental.to_csv(pjoin(test_path, 'experimental_samplesheet_run1.csv'), index = None)

@pytest.fixture
def make_run2_inputs(test_path):
	df_stock = pd.read_csv(pjoin(test_path, 'stock_samplesheet.csv'))

	print(df_stock)

	df_stock = df_stock[df_stock['run_group'] == 'run2']

	df_stock.drop(['run_group'], axis = 1, inplace = True)

	df_stock.to_csv(pjoin(test_path, 'stock_samplesheet_run2.csv'), index = None)

	df_experimental = pd.read_csv(pjoin(test_path, 'experimental_samplesheet.csv'))

	df_experimental = df_experimental[df_experimental['run_group'] == 'run2']

	df_experimental.drop(['run_group'], axis = 1, inplace = True)

	df_experimental.to_csv(pjoin(test_path, 'experimental_samplesheet_run2.csv'), index = None)

@pytest.fixture
def make_run3_inputs(test_path):
	df_experimental = pd.read_csv(pjoin(test_path, 'experimental_samplesheet.csv'))

	df_experimental = df_experimental[df_experimental['run_group'] == 'run3']

	df_experimental.drop(['run_group'], axis = 1, inplace = True)

	df_experimental.to_csv(pjoin(test_path, 'experimental_samplesheet_run3.csv'), index = None)

@pytest.fixture
def make_run4_inputs(test_path):
	df_stock = pd.read_csv(pjoin(test_path, 'stock_samplesheet.csv'))

	print(df_stock)

	df_stock = df_stock[df_stock['run_group'] == 'run4']

	df_stock.drop(['run_group'], axis = 1, inplace = True)

	df_stock.to_csv(pjoin(test_path, 'stock_samplesheet_run4.csv'), index = None)


def test_run1(test_path, test_workdir, make_workdir, make_run1_inputs, make_run2_inputs):
	"""
	python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1
	"""
	make_run1_inputs
	make_workdir

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run1.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run1.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_processed.csv')).shape == (1188, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_processed.csv')).shape == (399, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_barcode.csv')).shape == (2439, 3)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_barcode.csv')).shape == (930, 2)



def test_run1_and_run2(test_path, test_workdir, make_workdir, make_run1_inputs, make_run2_inputs):
	"""
	python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2
	"""
	make_run1_inputs
	make_run2_inputs
	make_workdir

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run1.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run1.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_processed.csv')).shape == (1188, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_processed.csv')).shape == (399, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_barcode.csv')).shape == (2439, 3)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_barcode.csv')).shape == (930, 2)


	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run2.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run2.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_processed.csv')).shape == (1785, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_processed.csv')).shape == (399, 12)



def test_run1_and_run2_run3(test_path, test_workdir, make_workdir, make_run1_inputs, make_run2_inputs, make_run3_inputs):
	"""
	python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3
	"""
	make_run1_inputs
	make_run2_inputs
	make_run3_inputs
	make_workdir

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run1.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run1.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')


### RUN 2

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run2.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run2.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_processed.csv')).shape == (1785, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_processed.csv')).shape == (399, 12)

### RUN 3

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run3.csv'),
		stock_file = None
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	assert os.path.exists(pjoin(test_path, 'work', 'experimental', 'animal3_unknown_27_plasma_dna_processed.csv'))


	bartender_setup.record.write_record(record_type = 'experimental')


def test_run1_and_run2_run3_run4(test_path, test_workdir, make_workdir, make_run1_inputs, make_run2_inputs, make_run3_inputs, make_run4_inputs):
	"""
	python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_run1_and_run2_run3_run4
	"""
	make_run1_inputs
	make_run2_inputs
	make_run3_inputs
	make_run4_inputs
	make_workdir

	### RUN 1

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run1.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run1.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')


	### RUN 2

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run2.csv'),
		stock_file = pjoin(test_path, 'stock_samplesheet_run2.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal1_unknown_27_plasma_dna_processed.csv')).shape == (1785, 12)

	assert pd.read_csv(pjoin(test_path, 'work', 'experimental', 'animal2_unknown_27_plasma_dna_processed.csv')).shape == (399, 12)


	bartender_setup.record.write_record(record_type = 'stock')

	bartender_setup.record.write_record(record_type = 'experimental')

	### RUN 3

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = pjoin(test_path, 'experimental_samplesheet_run3.csv'),
		stock_file = None
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	assert os.path.exists(pjoin(test_path, 'work', 'experimental', 'animal3_unknown_27_plasma_dna_processed.csv'))


	bartender_setup.record.write_record(record_type = 'experimental')

	### RUN 4

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = None,
		stock_file = pjoin(test_path, 'stock_samplesheet_run4.csv')
		)

	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	bartender_setup.record.write_record(record_type = 'stock')

	assert pd.read_csv(pjoin(test_path, 'work', 'stock', 'stock_barcodes_raw.csv')).shape == (10430, 6)

	assert pd.read_csv(pjoin(test_path, 'work', 'stock', 'stock_barcodes_filtered.csv')).shape == (5485, 5)


def test_stock_alone(test_path, test_workdir, make_workdir, make_run1_inputs):
	"""
	python -m slipcover -m pytest -sv  tests/end_to_end/test_ete2.py::test_stock_alone
	"""
	make_run4_inputs
	make_workdir

	bartender_setup = SetupManager(
		work_dir = test_workdir,
		experimental_file = None,
		stock_file = pjoin(test_path, 'stock_samplesheet_run1.csv')
		)


	samples = BarcodeProcessor(setup_manager = bartender_setup, barcode_length = 35)

	start = time.time()
	samples.process_stock_samples()
	print(time.time() - start)

	start = time.time()
	samples.process_experimental_samples()
	print(time.time() - start)

	assert os.path.exists(pjoin(test_path, 'work', 'stock', 'stock_barcodes_raw.csv'))

	bartender_setup.record.write_record(record_type = 'stock')









