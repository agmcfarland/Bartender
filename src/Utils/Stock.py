
import os
import pandas as pd
from os.path import join as pjoin
from glob import glob


class Stock:

	def __init__(self, setup_manager, barcode_length):
		self.setup_manager = setup_manager
		self.barcode_length = barcode_length

	def _read_raw_stock_barcodes(self):
		return pd.read_csv(self.setup_manager.run_paths.stock_barcodes_raw)

	def _read_filtered_stock_barcodes(self):
		return  pd.read_csv(self.setup_manager.run_paths.stock_barcodes_filtered)

	def _update_raw_stock_table(self):

		if os.path.exists(self.setup_manager.run_paths.stock_barcodes_raw):
			df_stock = self._read_raw_stock_barcodes()
		else:
			df_stock = pd.DataFrame({'barcode': []})

		for sample_file in glob(pjoin(self.setup_manager.run_paths.temp, '*', '*_barcode.csv')):
			df_stock = df_stock.merge(pd.read_csv(sample_file), on = 'barcode', how = 'outer')

		return df_stock

	def _filter_barcodes_on_length(self, df):

		df['barcode_length'] = self._get_barcode_length(df = df)

		df = self._filter_on_barcode_length(df = df)

		df.drop(columns = 'barcode_length', inplace = True)

		return df

	def _get_unique_biological_groups(self, df_stock_raw):
		return self.setup_manager.record.stock['biological_group'].unique().tolist()

	def _select_biological_group(self, df, biological_group):
		"""
		THIS IS A BUG THIS IS A BUG THIS IS A BUG
		"""
		return df.filter(regex = f'{biological_group}|barcode')

	def _count_stocks_with_barcode(self, df):
		return (df.iloc[:, 1:] != 0).sum(axis = 1)

	def _get_total_barcode_reads(self, df):
		"""
		Counts total number of barcodes per row and ignores first column (barcode) and last column (stock_with_barcode)
		"""
		end_columns = df.shape[1]-1

		return df.iloc[:, 1:end_columns].sum(axis = 1)

	def _get_mean_template_value(self, biological_group):
		return self.setup_manager.record.stock[self.setup_manager.record.stock['biological_group'] == biological_group]['input_template'].mean()

	def _get_proportion_filter(self, biological_group):
		return float(1/self._get_mean_template_value(biological_group = biological_group))

	def _count_all_barcodes(self, df):
		return df['total_barcodes'].sum()

	def _get_barcode_proportion(self, df):
		return df['total_barcodes']/self._count_all_barcodes(df = df)

	def _filter_by_proportion(self, df, biological_group):
		return df[df['proportion_barcode'] >= self._get_proportion_filter(biological_group = biological_group)]

	def _get_barcode_length(self, df):
		return df['barcode'].apply(lambda x: len(x))

	def _filter_on_barcode_length(self, df):
		return df[df['barcode_length'] == self.barcode_length]

	def _filter_on_singletons(self, df, count_threshold = 1):
		return df[df['stocks_with_barcode'] > count_threshold]

	def make_filtered_stock_table(self):
		
		df_stock = self._filter_barcodes_on_length(df = self._read_raw_stock_barcodes())

		df_filtered = pd.DataFrame()

		for _biological_group in self._get_unique_biological_groups(df_stock):

			df_biological_group = df_stock.copy(deep = True)

			df_biological_group = df_biological_group.fillna(0)

			df_biological_group = self._select_biological_group(df = df_biological_group, biological_group = _biological_group) 

			df_biological_group['stocks_with_barcode'] = self._count_stocks_with_barcode(df = df_biological_group)

			df_biological_group = self._filter_on_singletons(df = df_biological_group, count_threshold = 1)

			df_biological_group['total_barcodes'] = self._get_total_barcode_reads(df = df_biological_group)

			df_biological_group['proportion_barcode'] = self._get_barcode_proportion(df = df_biological_group)

			df_biological_group = self._filter_by_proportion(df = df_biological_group, biological_group = _biological_group)

			df_biological_group['biological_group'] = _biological_group

			df_filtered = pd.concat([df_filtered, df_biological_group])

		df_filtered = df_filtered[['barcode', 'stocks_with_barcode', 'total_barcodes', 'proportion_barcode', 'biological_group']]

		return df_filtered




