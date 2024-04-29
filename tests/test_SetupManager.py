

import pytest
import pandas as pd
import re
import os
from unittest.mock import patch, call
from Utils.SetupManager import SetupManager
from Utils.FilePaths import FilePaths
from Utils.Record import Record

@pytest.fixture
def mock_os_makedirs():
	with patch('Utils.FilePaths.os.makedirs') as mocked_makedirs:
		mocked_makedirs.side_effect = ['/path/to/workdir', '/path/to/workdir/record', '/path/to/workdir/stock', '/path/to/workdir/experimental', '/path/to/workdir/output']
		yield mocked_makedirs

def test_correct_inputs_pass(mock_os_makedirs, correct_experimental_input, correct_stock_input, expected_experimental_output, expected_stock_output):
	"""
	pytest -sv tests/test_SetupManager.py::test_correct_inputs_pass
	"""
	with patch('pandas.read_csv') as mock_read_csv:
		
		with patch('os.path.exists') as mock_path_exists:

			mock_path_exists.side_effect = [False, False, True, True, True, True, True, True, True, True, True, True, True, True]

			df_test_experimental = correct_experimental_input.copy(deep = True)

			df_test_stock = correct_stock_input.copy(deep = True)

			mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

			bartender_setup = SetupManager(
				work_dir = 'path/to/workdir',
				experimental_file = 'path/to/experimental.csv',
				stock_file = 'path/to/stock.csv'
				)

			assert bartender_setup.experimental.equals(expected_experimental_output)

			assert bartender_setup.stock.equals(expected_stock_output)


def test_incorrect_columns(mock_os_makedirs, correct_experimental_input, correct_stock_input):
	"""
	pytest -sv tests/test_SetupManager.py::test_incorrect_columns
	"""
	with patch('pandas.read_csv') as mock_read_csv:
		
		with patch('os.path.exists') as mock_path_exists:

			mock_path_exists.side_effect = [False, False, True, True, True, True, True, True, True, True, True, True, True, True]

			df_test_experimental = correct_experimental_input.copy(deep = True)

			df_test_experimental.rename({'biological_group': 'animal_id'}, inplace = True, axis = 1)

			df_test_stock = correct_stock_input.copy(deep = True)

			mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

			with pytest.raises(ValueError, match = 'experimental: animal_id not in columns'):
				bartender_setup = SetupManager(
						work_dir = 'path/to/workdir',
						experimental_file = 'path/to/experimental.csv',
						stock_file = 'path/to/stock.csv'
						)


def test_wrong_number_of_columns(mock_os_makedirs, correct_experimental_input, correct_stock_input):
	"""
	pytest -sv tests/test_SetupManager.py::test_wrong_number_of_columns
	"""
	with patch('pandas.read_csv') as mock_read_csv:
		
		with patch('os.path.exists') as mock_path_exists:

			mock_path_exists.side_effect = [False, False, True, True, True, True, True, True, True, True, True, True, True, True]

			df_test_experimental = correct_experimental_input.copy(deep = True)

			df_test_experimental.drop(columns = ['biological_group'], inplace = True)

			df_test_stock = correct_stock_input.copy(deep = True)

			mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

			with pytest.raises(ValueError, match = re.escape('experimental: Input length (9) does not equal expected length (10)')):
				bartender_setup = SetupManager(
						work_dir = 'path/to/workdir',
						experimental_file = 'path/to/experimental.csv',
						stock_file = 'path/to/stock.csv'
						)

def test_R1_path_does_not_exist(mock_os_makedirs, correct_experimental_input, correct_stock_input):

	with patch('pandas.read_csv') as mock_read_csv:
		
		with patch('os.path.exists') as mock_path_exists:
			
			mock_path_exists.side_effect = [False, False, False, True, True, True, True, True, True, True, True, True, True, True]

			df_test_experimental = correct_experimental_input.copy(deep = True)
			
			df_test_stock = correct_stock_input.copy(deep = True)

			mock_read_csv.side_effect = [df_test_experimental, df_test_stock]

			with pytest.raises(ValueError, match = 'experimental: path/to/sample1_R1.fastq.gz does not exist'):

				bartender_setup = SetupManager(
					work_dir = 'path/to/workdir',
					experimental_file = 'path/to/experimental.csv',
					stock_file = 'path/to/stock.csv'
					)







