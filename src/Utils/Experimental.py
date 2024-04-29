
import glob
import os
from os.path import join as pjoin
import pandas as pd
import random
import time
from math import isnan
from Utils.Common import hamming_distance_preset_length, hamming_distance_array

class Experimental:

	def __init__(self, setup_manager, stock, barcode_length, cutoff = 1):
		self.setup_manager = setup_manager
		self.stock = stock
		self.barcode_length = barcode_length
		self.cutoff = cutoff

	def _create_alphanumeric_id(self):
		return ''.join(random.choice('0123456789ABCDEF') for i in range(16))

	def _samples_to_process(self):
		self.incoming_samples = {i: {'path': [], 'barcode': pd.DataFrame()} for i in self.setup_manager.experimental['standard_sample_name'].tolist()}

		for _, row in self.setup_manager.experimental.iterrows():
			self.incoming_samples[row['standard_sample_name']]['path'].append(pjoin(self.setup_manager.run_paths.temp, row['sample_name'], row['standard_sample_name'] + '_barcode.csv'))

	def _get_counts_of_incoming_samples(self):

		for standard_sample_name, data in self.incoming_samples.items():

			for filename in data['path']:

				standard_sample_name_alphanumeric_id = standard_sample_name + '_' + self._create_alphanumeric_id()

				df = pd.read_csv(filename)

				df.rename({standard_sample_name: standard_sample_name_alphanumeric_id}, inplace = True, axis = 1)

				if data['barcode'].shape == (0, 0):
					data['barcode'] = df

				else:
					data['barcode'] = data['barcode'].merge(df, on = 'barcode', how = 'outer')

	def _merge_incoming_samples_with_existing_samples(self):

		for standard_sample_name, data in self.incoming_samples.items():

			if os.path.exists(pjoin(self.setup_manager.run_paths.experimental, standard_sample_name + '_barcode.csv')):

				df = pd.read_csv(pjoin(self.setup_manager.run_paths.experimental, standard_sample_name + '_barcode.csv'))

				data['barcode'] = data['barcode'].merge(df, on = 'barcode', how = 'outer')

	def _write_incoming_samples_to_file(self):
		
		for standard_sample_name, data in self.incoming_samples.items():
			data['barcode'].to_csv(pjoin(self.setup_manager.run_paths.experimental, standard_sample_name + '_barcode.csv'), index = None)

	def process_new_samples(self):
		self._samples_to_process()

		self._get_counts_of_incoming_samples()

		self._merge_incoming_samples_with_existing_samples()

		self._write_incoming_samples_to_file()


	def _get_mean_template_value(self, standard_sample_name):
		return self.setup_manager.record.experimental[self.setup_manager.record.experimental['standard_sample_name'] == standard_sample_name]['input_template'].mean()

	def _get_proportion_filter(self, standard_sample_name):
		return float(1/self._get_mean_template_value(standard_sample_name = standard_sample_name))

	def _get_minimum_passing_stock_proportion(self, df, standard_sample_name):
		df = df[df['instock_threshold_check'] == 'pass']
		if len(df) != 0:
			return df['proportion'].min()
		else:
			return self._get_proportion_filter(standard_sample_name = standard_sample_name)

	def _sum_of_trusted_barcodes(self, df):	
		"""
		calculate the trusted proportion for each barcode
		"""
		return df[df['trusted_barcode_check'] == 'pass']['total'].sum()

	def _get_best_hamming_match(self, df_experimental, barcodes1_list, barcodes2_list):

		start = time.time()
		# calculate distance up until cutoff
		barcode_distances = hamming_distance_array(barcodes1_list = barcodes1_list, barcodes2_list = barcodes2_list, barcode_length = self.barcode_length, cutoff = self.cutoff)
		print(time.time() - start)
		
		# format column
		barcode_distances = pd.DataFrame(barcode_distances, columns = ['query','reference','distance'])
		barcode_distances = barcode_distances.merge(df_experimental[['barcode', 'total']], left_on = 'reference', right_on = 'barcode', how = 'inner')
		barcode_distances.rename({'total': 'reference_count'}, inplace = True, axis = 1)
		barcode_distances.drop(columns = ['barcode'], inplace = True)

		# keep hits above 0 and below or equal to cutoff
		barcode_distances = barcode_distances[(barcode_distances['distance'] > 0) & (barcode_distances['distance'] <= self.cutoff)]

		# get the index of the largest reference_count for each query and subset
		best_query_hit_id = barcode_distances.groupby('query')['reference_count'].idxmax()
		barcode_distances = barcode_distances.loc[best_query_hit_id]

		return barcode_distances

	def _get_max_stock_barcode(self, stock_barcodes):
		"""
		Returns the largest barcode for each unique barcode. Input requires stock barcode table
		with columns ['barcode', 'total_stock']
		"""
		stock_barcodes = stock_barcodes.groupby('barcode')['total_stock'].max().reset_index()
		stock_barcodes.columns = ['barcode', 'total_stock']
		return stock_barcodes

	def _adjust_filtered_stock_format(self, stock_barcodes):
		"""
		Adjust dataframe slightly so it is more easily used in _apply_barcode_filters()
		"""
		stock_barcodes = stock_barcodes[['barcode', 'total_barcodes']]
		stock_barcodes.rename({'total_barcodes': 'total_stock'}, axis = 1, inplace = True)
		stock_barcodes = self._get_max_stock_barcode(stock_barcodes = stock_barcodes)

		return stock_barcodes

	def _apply_barcode_filters(self, standard_sample_name, df, stock_barcodes):
		pd.options.mode.chained_assignment = None

		# calculate and filter on barcode length
		df['barcode_length'] = df['barcode'].apply(lambda x: len(x))
		df = df[df['barcode_length'] == self.barcode_length]
		df.drop(columns = 'barcode_length', inplace = True)

		# calculate total barcodes
		df = df.fillna(0) 
		df['total'] = df.iloc[:, 1:].sum(axis = 1)

		# remove sample replicates
		df = df[['barcode', 'total']]

		# remove singletons
		df = df[df['total'] > 1]

		if len(df) == 0:
			return df

		# get best hamming match for each experimental barcode
		barcode_distances = self._get_best_hamming_match(df_experimental = df, barcodes1_list = df['barcode'].tolist(), barcodes2_list = set(df['barcode'].tolist() + stock_barcodes['barcode'].tolist()))
		barcode_distances.rename({'reference': 'best_match_sequence', 'distance': 'best_match_distance', 'reference_count': 'best_match_count'}, inplace = True, axis = 1)

		# flag barcodes with a count lower than 5% of best match
		df = df.merge(barcode_distances, left_on = 'barcode', right_on = 'query', how = 'left')
		df['pcr_error_check'] = df.apply(lambda x: 'pass' if x['best_match_count'] * 0.05 < x['total'] else 'fail', axis = 1)
		df['pcr_error_check'] = df.apply(lambda x: 'not_applicable' if pd.isna(x['best_match_sequence']) else x['pcr_error_check'], axis = 1)

		# merge stock dataframe
		df = df.merge(stock_barcodes, on = 'barcode', how = 'left')
		df['proportion'] = df['total']/df['total'].sum()

		# flag barcodes that do not pass the stock proportion check (proportion less than 1/input_template)
		df['instock_threshold_check'] = df.apply(lambda x: 'pass' if (x['total_stock'] > 0) & (x['proportion'] > self._get_proportion_filter(standard_sample_name = standard_sample_name)) else 'fail', axis = 1)
		df['instock_threshold_check'] = df.apply(lambda x: 'not_applicable' if pd.isna(x['total_stock']) else x['instock_threshold_check'], axis = 1)

		# flag barcodes that were not found in stock but still have a proportion higher than the lowest proportion of a barcode found in stock
		df['unique_barcode_threshold_check'] = df.apply(lambda x: 'pass' if (pd.isna(x['total_stock'])) & (x['proportion'] > self._get_minimum_passing_stock_proportion(df = df, standard_sample_name = standard_sample_name)) else 'fail', axis = 1)
		df['unique_barcode_threshold_check'] = df.apply(lambda x: 'not_applicable' if x['total_stock'] > 0 else x['unique_barcode_threshold_check'], axis = 1)

		# flag trusted barcodes
		df['trusted_barcode_check'] = df.apply(lambda x: 'pass' if (x['pcr_error_check'] == 'pass' or x['pcr_error_check'] == 'not_applicable') & (x['instock_threshold_check'] == 'pass' or x['instock_threshold_check'] == 'not_applicable') & (x['unique_barcode_threshold_check'] == 'pass' or x['unique_barcode_threshold_check'] == 'not_applicable') else 'fail', axis = 1)

		sum_of_trusted_barcodes = self._sum_of_trusted_barcodes(df = df)

		# calculate trusted barcode proportion
		df['trusted_proportion'] = df.apply(lambda x: x['total']/sum_of_trusted_barcodes if x['trusted_barcode_check'] == 'pass' else float(0), axis = 1)

		# remove unused columns
		df.drop(columns = ['query'], inplace = True)

		return df

	def make_filtered_barcodes(self):
		pd.options.mode.chained_assignment = None

		stock_barcodes = self._adjust_filtered_stock_format(stock_barcodes = self.stock._read_filtered_stock_barcodes())

		for standard_sample_name in self.setup_manager.record.experimental['standard_sample_name'].unique().tolist():

			print(standard_sample_name)

			df = pd.read_csv(pjoin(self.setup_manager.run_paths.experimental, standard_sample_name + '_barcode.csv'))

			df = self._apply_barcode_filters(standard_sample_name, df, stock_barcodes)

			if len(df) > 0:

				df.to_csv(pjoin(self.setup_manager.run_paths.experimental, standard_sample_name + '_processed.csv'), index = None)







		