import pytest
import pandas as pd
import re
import os
from os.path import join as pjoin
from unittest.mock import patch, call
from Utils.SetupManager import SetupManager
from Utils.FilePaths import FilePaths
from Utils.Record import Record

@pytest.fixture(scope = 'session', autouse = True)
def test_data_dir():
	return pjoin(os.getcwd(), 'tests', 'data')

@pytest.fixture(scope = 'session', autouse = True)
def correct_experimental_input():
	return pd.DataFrame({
		'sample_name': ['sample1', 'sample2', 'sample3'],
		'biological_group': ['group1', 'group2', 'group3'],
		'cell_type' : ['plasma', 'plasma', 'plasma'],
		'time_point' : [0, 1, 2],
		'time_point_description': ['dpi', 'dpi', 'dpi'],
		'organ': ['blood', 'blood', 'blood'],
		'input_template': [1000, 1000, 1000],
		'genetic_source': ['dna', 'dna', 'dna'],
		'R1': ['path/to/sample1_R1.fastq.gz', 'path/to/sample2_R1.fastq.gz', 'path/to/sample3_R1.fastq.gz'],
		'R2': ['path/to/sample1_R2.fastq.gz', 'path/to/sample2_R2.fastq.gz', 'path/to/sample3_R2.fastq.gz']
		})

@pytest.fixture(scope = 'session', autouse = True)
def expected_experimental_output():
	return pd.DataFrame({
		'sample_name': ['sample1', 'sample2', 'sample3'],
		'biological_group': ['group1', 'group2', 'group3'],
		'cell_type' : ['plasma', 'plasma', 'plasma'],
		'time_point' : [0, 1, 2],
		'time_point_description': ['dpi', 'dpi', 'dpi'],
		'organ': ['blood', 'blood', 'blood'],
		'input_template': [1000, 1000, 1000],
		'genetic_source': ['dna', 'dna', 'dna'],
		'R1': ['path/to/sample1_R1.fastq.gz', 'path/to/sample2_R1.fastq.gz', 'path/to/sample3_R1.fastq.gz'],
		'R2': ['path/to/sample1_R2.fastq.gz', 'path/to/sample2_R2.fastq.gz', 'path/to/sample3_R2.fastq.gz'],
		'standard_sample_name': ['group1_plasma_0_blood_dna', 'group2_plasma_1_blood_dna', 'group3_plasma_2_blood_dna']
		})

@pytest.fixture(scope = 'session', autouse = True)
def correct_stock_input():
	return pd.DataFrame({
		'sample_name': ['stock1', 'stock2', 'stock3'],
		'biological_group': ['group1', 'group2', 'group3'],
		'input_template': [1000, 1000, 1000],
		'R1': ['path/to/stock1_R1.fastq.gz', 'path/to/stock2_R1.fastq.gz', 'path/to/stock3_R1.fastq.gz'],
		'R2': ['path/to/stock1_R2.fastq.gz', 'path/to/stock2_R2.fastq.gz', 'path/to/stock3_R2.fastq.gz']
		})

@pytest.fixture(scope = 'session', autouse = True)
def expected_stock_output():
	return pd.DataFrame({
		'sample_name': ['stock1', 'stock2', 'stock3'],
		'biological_group': ['group1', 'group2', 'group3'],
		'input_template': [1000, 1000, 1000],
		'R1': ['path/to/stock1_R1.fastq.gz', 'path/to/stock2_R1.fastq.gz', 'path/to/stock3_R1.fastq.gz'],
		'R2': ['path/to/stock1_R2.fastq.gz', 'path/to/stock2_R2.fastq.gz', 'path/to/stock3_R2.fastq.gz'],
		'standard_sample_name': ['group1_stock1', 'group2_stock2', 'group3_stock3']
		})

@pytest.fixture(scope = 'session', autouse = True)
def stock_record():
	return pd.DataFrame({
		'sample_name': ['stock4', 'stock5', 'stock6'],
		'biological_group': ['group1', 'group2', 'group3'],
		'input_template': [1000, 1000, 1000],
		'R1': ['path/to/stock4_R1.fastq.gz', 'path/to/stock5_R1.fastq.gz', 'path/to/stock6_R1.fastq.gz'],
		'R2': ['path/to/stock4_R2.fastq.gz', 'path/to/stock5_R2.fastq.gz', 'path/to/stock6_R2.fastq.gz'],
		'standard_sample_name': ['group1_stock4', 'group2_stock5', 'group3_stock6']
		})

@pytest.fixture(scope = 'session', autouse = True)
def experimental_record():
	return pd.DataFrame({
		'sample_name': ['sample4', 'sample5', 'sample6'],
		'biological_group': ['group1', 'group2', 'group3'],
		'cell_type' : ['plasma', 'plasma', 'plasma'],
		'time_point' : [0, 3, 4],
		'time_point_description': ['dpi', 'dpi', 'dpi'],
		'organ': ['blood', 'blood', 'blood'],
		'input_template': [1000, 1000, 1000],
		'genetic_source': ['dna', 'dna', 'dna'],
		'R1': ['path/to/sample4_R1.fastq.gz', 'path/to/sample5_R1.fastq.gz', 'path/to/sample6_R1.fastq.gz'],
		'R2': ['path/to/sample4_R2.fastq.gz', 'path/to/sample5_R2.fastq.gz', 'path/to/sample6_R2.fastq.gz'],
		'standard_sample_name': ['group1_plasma_0_blood_dna', 'group2_plasma_3_blood_dna', 'group3_plasma_4_blood_dna']
		})





