import pytest
import pandas as pd
import re
import os
import glob
from unittest.mock import patch, call, Mock
from Utils.SetupManager import SetupManager
from Utils.FilePaths import FilePaths
from Utils.Record import Record
from Utils.ReportTable import ReportTable


@pytest.fixture
def experimental_barcodes():

	data = []
	# Define the data as lists of dictionaries
	data.append(pd.DataFrame([
		{"barcode": "GGGGGGGG", "total": 3763, "best_match_sequence": "GCGGCCAGCACTAGCAGACGCTGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 391, "pcr_error_check": "pass", "total_stock": 74, "proportion": 0.008662443, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.009280084},
		{"barcode": "GGGGGGGA", "total": 3133, "best_match_sequence": "GCGGCCAGCACTGACGGAAACTGTAGCTGGCCGCA", "best_match_distance": 1, "best_match_count": 28, "pcr_error_check": "pass", "total_stock": 4726, "proportion": 0.00721218, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.007726416},
		{"barcode": "GGGGGGGC", "total": 2366, "best_match_sequence": "GCGGCCAGCACTCCGTCAGCGAGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 421, "pcr_error_check": "pass", "total_stock": 143, "proportion": 0.005446543, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005834887},
		{"barcode": "GGGGGGGT", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758}
	]))

	data.append(pd.DataFrame([
		{"barcode": "GGGGGGGG", "total": 3763, "best_match_sequence": "GCGGCCAGCACTAGCAGACGCTGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 391, "pcr_error_check": "pass", "total_stock": 74, "proportion": 0.008662443, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.009280084},
		{"barcode": "GGGGGGGA", "total": 3133, "best_match_sequence": "GCGGCCAGCACTGACGGAAACTGTAGCTGGCCGCA", "best_match_distance": 1, "best_match_count": 28, "pcr_error_check": "pass", "total_stock": 4726, "proportion": 0.00721218, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.007726416},
		{"barcode": "GGGGGGGC", "total": 2366, "best_match_sequence": "GCGGCCAGCACTCCGTCAGCGAGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 421, "pcr_error_check": "pass", "total_stock": 143, "proportion": 0.005446543, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005834887},
		{"barcode": "GGGGGGGT", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758}
	]))

	data.append(pd.DataFrame([
		{"barcode": "GGGGGGGG", "total": 3763, "best_match_sequence": "GCGGCCAGCACTAGCAGACGCTGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 391, "pcr_error_check": "pass", "total_stock": 74, "proportion": 0.008662443, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.009280084},
		{"barcode": "GGGGGGGA", "total": 3133, "best_match_sequence": "GCGGCCAGCACTGACGGAAACTGTAGCTGGCCGCA", "best_match_distance": 1, "best_match_count": 28, "pcr_error_check": "pass", "total_stock": 4726, "proportion": 0.00721218, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.007726416},
		{"barcode": "GGGGGGGC", "total": 2366, "best_match_sequence": "GCGGCCAGCACTCCGTCAGCGAGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 421, "pcr_error_check": "pass", "total_stock": 143, "proportion": 0.005446543, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005834887},
		{"barcode": "GGGGGGTT", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758},
		{"barcode": "GGGGGGTA", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758}
	]))

	data.append(pd.DataFrame([
		{"barcode": "GGGGGGGG", "total": 3763, "best_match_sequence": "GCGGCCAGCACTAGCAGACGCTGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 391, "pcr_error_check": "pass", "total_stock": 74, "proportion": 0.008662443, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.009280084},
		{"barcode": "GGGGGGGA", "total": 3133, "best_match_sequence": "GCGGCCAGCACTGACGGAAACTGTAGCTGGCCGCA", "best_match_distance": 1, "best_match_count": 28, "pcr_error_check": "pass", "total_stock": 4726, "proportion": 0.00721218, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.007726416},
		{"barcode": "GGGGGGGC", "total": 2366, "best_match_sequence": "GCGGCCAGCACTCCGTCAGCGAGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 421, "pcr_error_check": "pass", "total_stock": 143, "proportion": 0.005446543, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005834887},
		{"barcode": "GGGGGGTT", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758},
		{"barcode": "GGGGGGTA", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758}
	]))

	data.append(pd.DataFrame([
		{"barcode": "AAAAAAAA", "total": 3763, "best_match_sequence": "GCGGCCAGCACTAGCAGACGCTGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 391, "pcr_error_check": "pass", "total_stock": 74, "proportion": 0.008662443, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.009280084},
		{"barcode": "AAAAAAAT", "total": 3133, "best_match_sequence": "GCGGCCAGCACTGACGGAAACTGTAGCTGGCCGCA", "best_match_distance": 1, "best_match_count": 28, "pcr_error_check": "pass", "total_stock": 4726, "proportion": 0.00721218, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.007726416},
		{"barcode": "AAAAAAAG", "total": 2366, "best_match_sequence": "GCGGCCAGCACTCCGTCAGCGAGTAGGTGGCCGCA", "best_match_distance": 3, "best_match_count": 421, "pcr_error_check": "pass", "total_stock": 143, "proportion": 0.005446543, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005834887},
		{"barcode": "AAAAAAAC", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0.005188758},
		{"barcode": "AAAAAATT", "total": 2104, "best_match_sequence": "GCGGCCACCTACACGAGACTCCAGTGCTGGCCGCA", "best_match_distance": 2, "best_match_count": 532, "pcr_error_check": "pass", "total_stock": 1122, "proportion": 0.004843418, "instock_threshold_check": "pass", "unique_barcode_threshold_check": "not_applicable", "trusted_barcode_check": "pass", "trusted_proportion": 0}
	]))

	return data


@pytest.fixture
def experimental_record():

	df = pd.DataFrame([{'sample_name': 'sample1', 'biological_group': 'bg1', 'cell_type':	'plasma',	'time_point': 7,		'organ': 'not_specified',		'genetic_source': 'cdna',		'input_template': 1000},
		{'sample_name': 'sample2', 'biological_group': 'bg1', 'cell_type':	'plasma',	'time_point': 10,		'organ': 'blood',		'genetic_source': 'vRNA',		'input_template': 1000},
		{'sample_name': 'sample3', 'biological_group': 'bg1', 'cell_type':	'cd4',	'time_point': 100,		'organ': 'spleen',		'genetic_source': 'cdna',		'input_template': 10000},
		{'sample_name': 'sample4', 'biological_group': 'bg1', 'cell_type':	'cd4',	'time_point': 100,		'organ': 'spleen',		'genetic_source': 'cdna',		'input_template': 1000},					
		{'sample_name': 'sample5', 'biological_group': 'bg2', 'cell_type':	'plasma',	'time_point': 0,		'organ': 'not_specified',		'genetic_source': 'cdna',		'input_template': 1000},		
		{'sample_name': 'sample6', 'biological_group': 'bg2', 'cell_type':	'cd4',	'time_point': 0,		'organ': 'not_specified',		'genetic_source': 'not_specified',		'input_template': 10000},
		{'sample_name': 'sample7', 'biological_group': 'bg2', 'cell_type':	'cd4',	'time_point': 100,		'organ': 'not_specified',		'genetic_source': 'not_specified',		'input_template': 10000}]) # failed so no experimental record

	df['standard_sample_name'] = df.apply(lambda x: x['biological_group'] + '_' +  x['cell_type'] + '_' + str(int(x['time_point'])) + '_' + x['organ'] + '_' + x['genetic_source'], axis = 1)

	return df


@pytest.fixture
def standard_barcode_name_table():
	data = [
	("GGGGGGGG", "CH505_V2_0"),
	("GGGGGGGA", "CH505_TF_1"),
	("GGGGGGGC", "CH505_TF_2"),
	("GGGGGGGT", "stock_2_3"),
	("GGGGGGGG", "CH505_V2_0"),
	("GGGGGGGA", "CH505_TF_1"),
	("GGGGGGGC", "CH505_TF_2"),
	("GGGGGGGT", "stock_2_3"),
	("GGGGGGGG", "CH505_V2_0"),
	("GGGGGGGA", "CH505_TF_1"),
	("GGGGGGGC", "CH505_TF_2"),
	("GGGGGGTT", "stock_2_3"),
	("GGGGGGTA", "stock_1_4"),
	("GGGGGGGG", "CH505_V2_0"),
	("GGGGGGGA", "CH505_TF_1"),
	("GGGGGGGC", "CH505_TF_2"),
	("GGGGGTTA", "experimental_1_8"),
	("AAAAAAAA", "CH505_TF_5"),
	("AAAAAAAT", "CH505_TF_6"),
	("AAAAAAAG", "CH505_TF_7"),
	("AAAAAAAC", "experimental_1_9")
	]

	df = pd.DataFrame(data, columns = ['barcode', 'standard_barcode_name'])

	df = df.drop_duplicates()

	return df

@pytest.fixture
def mock_setup_manager(test_data_dir):
	mock_setup_manager = Mock()
	mock_setup_manager.run_paths.stock_barcodes_raw = '/path/to/raw.csv'
	mock_setup_manager.run_paths.temp = '/path/to/temp'
	return mock_setup_manager


def test_pass(experimental_barcodes, experimental_record, standard_barcode_name_table):
	"""
	pytest -sv tests/test_ReportTable.py::test_pass
	"""
	print(experimental_barcodes)

	print(experimental_record)

	print(standard_barcode_name_table)

	pass



def test_read_in_experimental_samples(mock_setup_manager, experimental_barcodes, experimental_record, standard_barcode_name_table):
	"""
	pytest -sv tests/test_ReportTable.py::test_read_in_experimental_samples	
	"""
	report_table = ReportTable(setup_manager = mock_setup_manager)

	with patch.object(report_table, '_load_standard_barcode_names', return_value = standard_barcode_name_table):
		with patch.object(mock_setup_manager.run_paths, 'experimental', new = '/path/to/experimental'):

			with patch('Utils.ReportTable.glob') as mock_glob:
				with patch('Utils.ReportTable.pd.read_csv') as mock_csv:
					with patch('Utils.ReportTable.os.path.basename') as mock_basename:

						mock_glob.return_value = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_basename.side_effect = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_csv.side_effect = experimental_barcodes

						report_table._read_in_experimental_samples()

						assert report_table.experimental_table.shape == (23, 13)


def test_map_standard_barcode_names_to_barcodes(mock_setup_manager, experimental_barcodes, experimental_record, standard_barcode_name_table):
	"""
	pytest -sv tests/test_ReportTable.py::test_map_standard_barcode_names_to_barcodes
	"""
	report_table = ReportTable(setup_manager = mock_setup_manager)

	with patch.object(report_table, '_load_standard_barcode_names', return_value = standard_barcode_name_table):
		with patch.object(mock_setup_manager.run_paths, 'experimental', new = '/path/to/experimental'):

			with patch('Utils.ReportTable.glob') as mock_glob:
				with patch('Utils.ReportTable.pd.read_csv') as mock_csv:
					with patch('Utils.ReportTable.os.path.basename') as mock_basename:

						mock_glob.return_value = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_basename.side_effect = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_csv.side_effect = experimental_barcodes

						report_table._read_in_experimental_samples()

						report_table._map_standard_barcode_names_to_barcodes()

						assert report_table.experimental_table.shape == (23, 15)



def test_make_report_table_type_1(mock_setup_manager, experimental_barcodes, experimental_record, standard_barcode_name_table):
	"""
	pytest -sv tests/test_ReportTable.py::test_make_report_table_type_1
	"""
	report_table = ReportTable(setup_manager = mock_setup_manager)

	with patch.object(report_table, '_load_standard_barcode_names', return_value = standard_barcode_name_table):
		with patch.object(mock_setup_manager.run_paths, 'experimental', new = '/path/to/experimental'):
			report_table.setup_manager.record.experimental = experimental_record

			with patch('Utils.ReportTable.glob') as mock_glob:
				with patch('Utils.ReportTable.pd.read_csv') as mock_csv:
					with patch('Utils.ReportTable.os.path.basename') as mock_basename:

						mock_glob.return_value = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_basename.side_effect = ['bg1_plasma_7_not_specified_cdna_processed.csv', 'bg1_plasma_10_blood_vRNA_processed.csv', 'bg1_cd4_100_spleen_cdna_processed.csv', 'bg2_plasma_0_not_specified_cdna_processed.csv', 'bg2_cd4_0_not_specified_not_specified_processed.csv']

						mock_csv.side_effect = experimental_barcodes

						report_table.make_report_table_type_1()

						assert len(report_table.type_1_experiment_table) == 2

						assert report_table.type_1_experiment_table[0].shape == (15, 5)

						assert report_table.type_1_experiment_table[1].shape == (18, 4)












