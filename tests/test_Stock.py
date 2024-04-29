
import pytest
import os
from os.path import join as pjoin
from glob import glob
import re
import pandas as pd
from unittest.mock import patch, Mock
from src.Bartender.Utils.SampleRead import SampleRead
from src.Bartender.Utils.Stock import Stock


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


def test_update_raw_stock_table(raw_barcode_tables, mock_setup_manager, test_data_dir):
	"""
	pytest -sv tests/test_Stock.py::test_update_raw_stock_table
	"""
	with patch('os.path.exists') as mock_path_exists:

		with patch('pandas.read_csv') as mock_read_csv:

			with patch('src.Bartender.Utils.Stock.glob') as mock_glob:

				mock_path_exists.return_value = False

				mock_read_csv.side_effect = raw_barcode_tables

				mock_glob.return_value = ['1_barcode.csv','2_barcode.csv','3_barcode.csv','4_barcode.csv']

				stock = Stock(setup_manager = mock_setup_manager, barcode_length = 35)

				df_raw_stock = stock._update_raw_stock_table()

	df_reference_raw_stock = pd.read_csv(pjoin(test_data_dir, 'stock', 'stock_barcodes_raw.csv'))

	df_barcode_order = pd.DataFrame({'barcode': df_reference_raw_stock['barcode'].tolist(), 'order': [e for e, i in enumerate(df_reference_raw_stock['barcode'].tolist())]})

	df_reference_raw_stock = df_reference_raw_stock.merge(df_barcode_order, on = 'barcode')
	df_reference_raw_stock.sort_values('order', inplace = True)
	df_reference_raw_stock.drop('order', inplace = True, axis = 1)
	df_reference_raw_stock.fillna(0, inplace = True)

	df_raw_stock = df_raw_stock.merge(df_barcode_order, on = 'barcode')
	df_raw_stock.sort_values('order', inplace = True)
	df_raw_stock.drop('order', inplace = True, axis = 1)
	df_raw_stock.fillna(0, inplace = True)

	df_raw_stock = df_raw_stock[list(df_reference_raw_stock.columns)]

	for col in list(df_raw_stock.columns):
		assert df_raw_stock[col].tolist() == df_reference_raw_stock[col].tolist()


def test_make_filtered_stock_table(raw_barcode_tables, mock_setup_manager, test_data_dir):
	"""
	pytest -sv tests/test_Stock.py::test_make_filtered_stock_table

	Proportion gets rounded due to run to run variability in decimal points in the millionths position.
	"""
	df_reference_raw = pd.read_csv(pjoin(test_data_dir, 'stock', 'stock_barcodes_raw.csv'))

	with patch('pandas.read_csv') as mock_read_csv:

		mock_read_csv.return_value = df_reference_raw

		stock = Stock(setup_manager = mock_setup_manager, barcode_length = 35) 

		with patch.object(stock, '_get_unique_biological_groups', return_value = ['CD4_derived_TF']):

			with patch.object(stock, '_get_mean_template_value', return_value = 50000):

				df_filtered_stock = stock.make_filtered_stock_table()

	df_reference_filtered = pd.read_csv(pjoin(test_data_dir, 'stock', 'stock_barcodes_filtered.csv'))		

	for col in list(df_filtered_stock.columns):
		if col == 'proportion_barcode':
			proportion_experimental = [round(i, 2) for i in df_filtered_stock[col].tolist()]
			proportion_reference = [round(i, 2) for i in df_reference_filtered[col].tolist()]

			assert proportion_experimental == proportion_reference
		else:
			assert df_filtered_stock[col].tolist() == df_reference_filtered[col].tolist()
	

				
