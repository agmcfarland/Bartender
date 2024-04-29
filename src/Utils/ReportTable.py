
from os.path import join as pjoin
import os
import pandas as pd
from glob import glob
from Utils.SetupManager import SetupManager

class ReportTable:

	def __init__(self, setup_manager):
		self.setup_manager = setup_manager
		self.experimental_table = pd.DataFrame()

	def _load_standard_barcode_names(self):
		"""
		"""
		return pd.read_csv(pjoin(self.setup_manager.run_paths.output, 'standard_barcode_names.csv'))

	def _read_in_experimental_samples(self):
		"""
		"""
		for f in glob(pjoin(self.setup_manager.run_paths.experimental, '*_processed.csv')):
			df = pd.read_csv(f)
			df['file_tag'] = os.path.basename(f).replace('_processed.csv', '')
			self.experimental_table = pd.concat([self.experimental_table, df])

	def _map_standard_barcode_names_to_barcodes(self):
		self.experimental_table = self.experimental_table.merge(self._load_standard_barcode_names(), on = 'barcode', how = 'left', indicator = True)


	def _biological_group_to_table_type_1_counts(self, df):


		pass


	def _make_condensed_experiemntal_record(self, biological_group):
		"""
		Remove all replicates and get the mean input_template
		"""
		df_bg_record = self.setup_manager.record.experimental.copy(deep = True)

		df_bg_record = df_bg_record[df_bg_record['biological_group'] == biological_group]

		condensed_df = df_bg_record.groupby('standard_sample_name').agg({'input_template': 'mean'}).reset_index()

		df_bg_record = pd.merge(condensed_df, df_bg_record[['biological_group', 'cell_type', 'time_point', 'organ', 'genetic_source', 'standard_sample_name']], 
                 on='standard_sample_name', how='left')

		df_bg_record = df_bg_record.drop_duplicates()

		return df_bg_record


	def make_report_table_type_1(self):

		self._read_in_experimental_samples()

		self._map_standard_barcode_names_to_barcodes()

		self.type_1_experiment_table = []

		for biological_group_ in self.setup_manager.record.experimental['biological_group'].unique().tolist():

			df_bg = self.experimental_table.copy(deep = True)

			df_bg = df_bg[df_bg['file_tag'].isin(self.setup_manager.record.experimental['standard_sample_name'].tolist())]

			df_bg = df_bg[df_bg['trusted_proportion'] > 0]

			df_bg_record = self._make_condensed_experiemntal_record(biological_group = biological_group_)

			df_bg_record = df_bg_record.sort_values(['time_point', 'cell_type', 'organ', 'genetic_source'], ascending = [True, False, False, False])


			self.counts = pd.DataFrame(columns = ['barcode', 'standard_barcode_name'])

			for _, sample in df_bg_record.iterrows():

				df_sample = df_bg[df_bg['file_tag'] == sample.standard_sample_name]

				if len(df_sample) > 0:

					df_sample[sample.standard_sample_name] = df_sample['total']

					df_sample = df_sample[['standard_barcode_name', 'barcode', sample.standard_sample_name]]

					self.counts  = self.counts.merge(df_sample, on = ['barcode', 'standard_barcode_name'], how = 'outer')


			self.experimental_details = pd.DataFrame()

			for _, sample in df_bg_record.iterrows():

				df_sample = df_bg[df_bg['file_tag'] == sample.standard_sample_name]

				if len(df_sample) > 0:

					self.experimental_details = pd.concat([
						self.experimental_details,
						pd.DataFrame([{
						'standard_sample_name': sample.standard_sample_name,
						'cell_type': sample.cell_type, 
						'organ': sample.organ, 
						'genetic_source': sample.genetic_source, 
						'time_point': sample.time_point, 
						'template': sample.input_template, 
						'sequences': df_sample['total'].sum(), 
						'unique': len(df_sample)}])
					])


			self.experimental_details = self.experimental_details.T

			self.experimental_details.insert(0, 'attributes', self.experimental_details.index)

			self.experimental_details = self.experimental_details.reset_index(drop = True)

			self.experimental_details.insert(0, 'other', [biological_group_, '', '', '', '', '', '', ''])

			self.experimental_details.columns = self.counts.columns

			faux_columns = pd.DataFrame(self.counts.columns.tolist())

			faux_columns = faux_columns.T

			faux_columns.columns = self.counts.columns.tolist()

			self.counts['total'] = self.counts.select_dtypes(include = 'number').mean(axis = 1)

			self.counts = self.counts.sort_values('total', ascending = False)

			self.counts.drop(columns = 'total', inplace = True)

			self.counts = self.counts.fillna(0)

			self.combined_details_counts = pd.concat([self.experimental_details, faux_columns], axis = 0, ignore_index = True)

			self.combined_details_counts = pd.concat([self.combined_details_counts, self.counts], axis = 0, ignore_index = True)

			self.type_1_experiment_table.append(self.combined_details_counts)


	def write_report_table_type_1_to_excel(self):

		try:
			os.remove(pjoin(self.setup_manager.run_paths.output, 'barcode_report_table_type_1.xlsx'))
		except:
			pass

		with pd.ExcelWriter(pjoin(self.setup_manager.run_paths.output, 'barcode_report_table_type_1.xlsx')) as writer:

			for table in self.type_1_experiment_table:
				biological_group = table.iloc[0, 0]

				table.to_excel(writer, sheet_name = biological_group, index = False, header = False)


