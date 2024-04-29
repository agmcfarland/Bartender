
from os.path import join as pjoin
import os
import pandas as pd
from glob import glob
from Utils.SetupManager import SetupManager

class StandardBarcodeName:

	def __init__(self, setup_manager):
		self.setup_manager = setup_manager

	def _read_in_stock_barcode(self):
		return pd.read_csv(pjoin(self.setup_manager.run_paths.stock, 'stock_barcodes_filtered.csv'))

	def _assign_stock_barcode_names(self):

		df = self._read_in_stock_barcode()

		barcode_observed = pd.DataFrame(df['barcode'].value_counts()).reset_index()

		barcode_observed.columns = ['barcode', 'observations']

		df = df.merge(barcode_observed, on = 'barcode')

		df['barcode_id_base'] = df.apply(lambda x: x['biological_group'] if x['observations'] == 1 else 'stock_' + str(x['observations']), axis = 1)

		df = df.sort_values('total_barcodes', ascending = False)

		df = df[['barcode', 'barcode_id_base']].drop_duplicates()

		df['barcode_order'] = [i for i in range(len(df))]

		df['standard_barcode_name'] = df['barcode_id_base'] + '_' + df['barcode_order'].astype(str)

		df = df[['barcode', 'standard_barcode_name']]

		return df

	def _read_in_experimental_barcodes(self):

		df_all = pd.DataFrame()
		for f in glob(pjoin(self.setup_manager.run_paths.experimental, '*_processed.csv')):
			df = pd.read_csv(f)
			df = df[['barcode']]
			df['file_tag'] = os.path.basename(f)
			df_all = pd.concat([df_all, df])

		return df_all

	def assign_standard_barcode_names(self):

		df_stock = self._assign_stock_barcode_names()

		df_experimental = self._read_in_experimental_barcodes()

		if len(df_experimental) != 0:

			df_experimental = df_experimental.merge(df_stock, on = 'barcode', how = 'outer', indicator = True)

			df_experimental = df_experimental[df_experimental['_merge'] == 'left_only']

			df_experimental = self._assign_unique_experimental_barcode_names(df = df_experimental)

			df_stock = pd.concat([df_stock, df_experimental])

		self.names = df_stock

	def _assign_unique_experimental_barcode_names(self, df):

		df = df[['barcode', 'file_tag']]

		barcode_observed = pd.DataFrame(df['barcode'].value_counts()).reset_index()

		barcode_observed.columns = ['barcode', 'observations']

		df = df.merge(barcode_observed, on = 'barcode')

		df = df[['barcode', 'observations']].drop_duplicates()

		df = df.sort_values('observations', ascending = False)

		df['barcode_order'] = [i for i in range(len(df))]

		df['standard_barcode_name'] = 'experimental_' + df['observations'].astype(str) + '_' + df['barcode_order'].astype(str)

		df = df[['barcode', 'standard_barcode_name']]

		return df

	def write_to_file(self):
		self.names.to_csv(pjoin(self.setup_manager.run_paths.output, 'standard_barcode_names.csv'), index = None)



