
import os
import pandas as pd
from os.path import join as pjoin
from Utils.FilePaths import FilePaths
from Utils.Record import Record

class SetupManager:

	def __init__(self, work_dir, experimental_file = None, stock_file = None):

		self.run_paths = FilePaths(work_dir = work_dir)
		self.run_paths.make_work_dir_tree()

		self.record = Record(run_paths = self.run_paths)
		self.record.load_stock_record()
		self.record.load_experimental_record()

		self.experimental_file = experimental_file
		self.stock_file = stock_file

		self.experimental = None
		self.stock = None

		if self.experimental_file is not None:
			self.experimental = self._read_input_experimental(experimental_file)
			self._assign_standardized_sample_names_experimental()
			self.record.update_experimental_record(table_to_add = self.experimental)

		if self.stock_file is not None:
			self.stock = self._read_input_stock(stock_file)
			self._assign_standardized_sample_names_stock()
			self.record.update_stock_record(table_to_add = self.stock)


	def _allowed_experimental_columns(self):
		return ['sample_name', 'biological_group', 'cell_type', 'time_point', 'time_point_description', 'organ', 'input_template', 'genetic_source', 'R1', 'R2']

	def _allowed_stock_columns(self):
		return ['sample_name', 'biological_group', 'input_template', 'R1', 'R2']

	def _verify_bartender_table_inputs(self, df, allowed_columns: list, table_type: str):
		for i in list(df.columns):
			if i not in allowed_columns:
				raise ValueError(f'{table_type}: {i} not in columns')

		if len(df.columns) != len(allowed_columns):
			raise ValueError(f'{table_type}: Input length ({len(df.columns)}) does not equal expected length ({len(allowed_columns)})')

		for read1 in df['R1'].tolist():
			if not os.path.exists(read1):
				raise ValueError(f'{table_type}: {read1} does not exist')

		for read2 in df['R2'].tolist():
			if not os.path.exists(read2):
				raise ValueError(f'{table_type}: {read2} does not exist')	

		return df	

	def _read_input_experimental(self, experimental_file):
		return self._verify_bartender_table_inputs(df = pd.read_csv(pjoin(experimental_file)), allowed_columns = self._allowed_experimental_columns(), table_type = 'experimental')

	def _read_input_stock(self, stock_file):
		return self._verify_bartender_table_inputs(df = pd.read_csv(pjoin(stock_file)), allowed_columns = self._allowed_stock_columns(), table_type = 'stock')

	def _assign_standardized_sample_names_stock(self):
		self.stock['standard_sample_name'] = self.stock.apply(lambda x: x['biological_group'] + '_' + x['sample_name'], axis = 1)

	def _assign_standardized_sample_names_experimental(self):
		self.experimental['standard_sample_name'] = self.experimental.apply(lambda x: x['biological_group'] + '_' + x['cell_type'] + '_' + str(int(round(x['time_point']))) + '_' + x['organ'] + '_' + x['genetic_source'], axis = 1)





