

import pytest
import pandas as pd
import re
import os
import glob
from unittest.mock import patch, call, Mock
from src.Bartender.Utils.SetupManager import SetupManager
from src.Bartender.Utils.FilePaths import FilePaths
from src.Bartender.Utils.Record import Record
from src.Bartender.Utils.StandardBarcodeName import StandardBarcodeName


@pytest.fixture
def raw_barcode_tables(test_data_dir):
	raw_barcode_tables_ = []
	for f in glob(pjoin(test_data_dir, 'stock', '*_barcode.csv')):
		raw_barcode_tables_.append(pd.read_csv(f))
	return raw_barcode_tables_

@pytest.fixture
def mock_setup_manager(test_data_dir):
	mock_setup_manager = Mock()
	mock_setup_manager.run_paths.stock_barcodes_raw = '/path/to/raw.csv'
	mock_setup_manager.run_paths.temp = '/path/to/temp'
	return mock_setup_manager


@pytest.fixture
def mock_stock_filtered():
	data = {
		'barcode': [
			'GCGGCCAGCACTAAGCGAGCGAGTAGGTGGCCGCA', 'GCGGCCAGCACTTTTATGCGCGGTAGGTGGCCGCA',
			'GCGGCCACCTACTGATGAGACCAGTGCTGGCCGCA', 'GCGGCCACCTACATTAGGCTCGAGTGCTGGCCGCA',
			'GCGGCCAGCACTTAACAGAGATGTAGGTGGCCGCA', 'GCGGCCAGCACTGTAACAATTGGTAGGTGGCCGCA',
			'GCGGCCACCTACATGTGATCAGAGTGCTGGCCGCA', 'GCGGCCACCTACCATCGGTAAAAGTGCTGGCCGCA',
			'GCGGCCACCTACCCTTAGTCGCAGTGCTGGCCGCA', 'GCGGCCAGCACTGAGGGCAAGTGTAGGTGGCCGCA',
			'GCGGCCAGCACTAAGCGAGCGAGTAGGTGGCCGCA', 'GCGGCCAGCACTTTTATGCGCGGTAGGTGGCCGCA',
			'GCGGCCACCTACCCGAAATTTAAGTGCTGGCCGCA', 'GCGGCCACCTACTCCACCATGTAGTGCTGGCCGCA',
			'GCGGCCAGCACTATAACTATCAGTAGGTGGCCGCA', 'GCGGCCAGCACTGTAGCGATGCGTAGGTGGCCGCA',
			'GCGGCCAGCACTTCGCGGTGACGTAGGTGGCCGCA', 'GCGGCCACCTACTAGAAGCCAAAGTGCTGGCCGCA',
			'GCGGCCACCTACTTCGGCTTATAGTGCTGGCCGCA', 'GCGGCCACCTACCCATATGTAAAGTGCTGGCCGCA'
		],
		'stocks_with_barcode': [10] * 20,
		'total_barcodes': [100 * (i + 1) for i in range(10)] * 2,
		'proportion_barcode': [1] * 20,
		'biological_group': ['CH505_V2'] * 10 + ['CH505_TF'] * 10
	}

	return pd.DataFrame(data)


@pytest.fixture
def mock_experimental_barcodes():

	mock_barcode_csv = []
	# one shared, one v2
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTAAGCGAGCGAGTAGGTGGCCGCA', 'GCGGCCACCTACTGATGAGACCAGTGCTGGCCGCA']}))

	# one shared one TF
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTAAGCGAGCGAGTAGGTGGCCGCA', 'GCGGCCACCTACTCCACCATGTAGTGCTGGCCGCA']}))

	# one TF one V2
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTATAACTATCAGTAGGTGGCCGCA', 'GCGGCCACCTACCCTTAGTCGCAGTGCTGGCCGCA']}))

	# One TF one unique (2 total in experimental)
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTATAACTATCAGTAGGTGGCCGCA', 'GCGGCCAGCACTGGACTTTCTAGTAGGTGGCCGCA']}))

	# One TF one unique (2 total in experimental)
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTATAACTATCAGTAGGTGGCCGCA', 'GCGGCCAGCACTGGACTTTCTAGTAGGTGGCCGCA']}))

	# One TF one unique (1 total in experimental)
	mock_barcode_csv.append(pd.DataFrame({'barcode': ['GCGGCCAGCACTATAACTATCAGTAGGTGGCCGCA', 'GCGGCCAGCACTGGACTTTCAAGTAGGTGGCCGCA']}))

	return mock_barcode_csv

def test_read_in_stock_barcode(test_data_dir, mock_setup_manager, mock_stock_filtered):
	"""
	pytest -sv tests/test_StandardBarcodeName.py::test_read_in_stock_barcode	
	"""
	mock_setup_manager = mock_setup_manager

	standard_barcode_name = StandardBarcodeName(setup_manager = mock_setup_manager)

	with patch.object(standard_barcode_name, '_read_in_stock_barcode', return_value = mock_stock_filtered):

		df = standard_barcode_name._read_in_stock_barcode()

		assert df.equals(mock_stock_filtered)

def test_assign_stock_barcode_names(test_data_dir, mock_setup_manager, mock_stock_filtered):
	"""
	pytest -sv tests/test_StandardBarcodeName.py::test_assign_stock_barcode_names	
	"""
	mock_setup_manager = mock_setup_manager

	standard_barcode_name = StandardBarcodeName(setup_manager = mock_setup_manager)

	with patch.object(standard_barcode_name, '_read_in_stock_barcode', return_value = mock_stock_filtered):

		df = standard_barcode_name._assign_stock_barcode_names()

		assert df.shape == (18, 2)


def test_read_in_experimental_barcodes(mock_setup_manager, mock_experimental_barcodes):
	"""
	pytest -sv tests/test_StandardBarcodeName.py::test_read_in_experimental_barcodes	
	"""
	
	standard_barcode_name = StandardBarcodeName(setup_manager = mock_setup_manager)

	with patch.object(mock_setup_manager.run_paths, 'experimental', new = '/path/to/experimental'):
		with patch('src.Bartender.Utils.StandardBarcodeName.glob') as mock_glob:
			with patch('src.Bartender.Utils.StandardBarcodeName.pd.read_csv') as mock_csv:
				with patch('src.Bartender.Utils.StandardBarcodeName.os.path.basename') as mock_basename:

					mock_basename.side_effect = ['file1_processed.csv', 'file2_processed.csv', 'file3_processed.csv', 'file4_processed.csv', 'file5_processed.csv', 'file6_processed.csv']
					mock_glob.return_value = ['file1_processed.csv', 'file2_processed.csv', 'file3_processed.csv', 'file4_processed.csv', 'file5_processed.csv', 'file6_processed.csv']  # Mock glob result
					mock_csv.side_effect = mock_experimental_barcodes

					result = standard_barcode_name._read_in_experimental_barcodes()

					assert result.shape == (12,2)


def test_assign_standard_barcode_names(mock_setup_manager, mock_experimental_barcodes, mock_stock_filtered):
	"""
	pytest -sv tests/test_StandardBarcodeName.py::test_assign_standard_barcode_names	
	"""
	standard_barcode_name = StandardBarcodeName(setup_manager = mock_setup_manager)

	with patch.object(standard_barcode_name, '_read_in_stock_barcode', return_value = mock_stock_filtered):
		with patch.object(mock_setup_manager.run_paths, 'experimental', new = '/path/to/experimental'):
			with patch('src.Bartender.Utils.StandardBarcodeName.glob') as mock_glob:
				with patch('src.Bartender.Utils.StandardBarcodeName.pd.read_csv') as mock_csv:
					with patch('src.Bartender.Utils.StandardBarcodeName.os.path.basename') as mock_basename:

						mock_basename.side_effect = ['file1_processed.csv', 'file2_processed.csv', 'file3_processed.csv', 'file4_processed.csv', 'file5_processed.csv', 'file6_processed.csv']
						mock_glob.return_value = ['file1_processed.csv', 'file2_processed.csv', 'file3_processed.csv', 'file4_processed.csv', 'file5_processed.csv', 'file6_processed.csv']  # Mock glob result
						mock_csv.side_effect = mock_experimental_barcodes

						standard_barcode_name.assign_standard_barcode_names()

						assert standard_barcode_name.names.shape == (20, 2)


def test_write_to_file(mock_setup_manager):
	"""
	pytest -sv tests/test_StandardBarcodeName.py::test_write_to_file	
	"""
	standard_barcode_name = StandardBarcodeName(setup_manager = mock_setup_manager)

	with patch.object(mock_setup_manager.run_paths, 'output', new = '/path/to/output'):

		with patch('pandas.DataFrame.to_csv') as mock_to_csv:

			standard_barcode_name.names = pd.DataFrame()

			standard_barcode_name.write_to_file()

			mock_to_csv.assert_called_once_with('/path/to/output/standard_barcode_names.csv', index=None)
















