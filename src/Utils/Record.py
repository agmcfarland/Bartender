import os
import pandas as pd
from os.path import join as pjoin
from Utils.FilePaths import FilePaths


class Record:
    def __init__(self, run_paths):
        """ """
        self.run_paths = run_paths
        self.stock = None
        self.experimental = None

    def load_stock_record(self):
        if os.path.exists(self.run_paths.record_stock):
            self.stock = pd.read_csv(pjoin(self.run_paths.record_stock))

    def load_experimental_record(self):
        if os.path.exists(self.run_paths.record_experimental):
            self.experimental = pd.read_csv(pjoin(self.run_paths.record_experimental))

    def update_stock_record(self, table_to_add):
        if self.stock is not None:
            self.stock = pd.concat([self.stock, table_to_add])
        else:
            self.stock = table_to_add

        self._run_record_through_checks(table=self.stock)

    def update_experimental_record(self, table_to_add):
        if self.experimental is not None:
            self.experimental = pd.concat([self.experimental, table_to_add])
        else:
            self.experimental = table_to_add

        self._run_record_through_checks(table=self.experimental)

    def unique_stock_biological_groups(self):
        return list(self.stock['biological_group'].unique())

    def _run_record_through_checks(self, table):
        df_check_record = table.copy(deep=True)

        self._check_all_R1_unique(table=df_check_record)
        self._check_all_R2_unique(table=df_check_record)
        self._check_unique_names(table=df_check_record)

    def _check_unique_values_in_column(self, table, column_name):
        return len(table[column_name].unique().tolist()) == len(
            table[column_name].tolist()
        )

    def _check_all_R1_unique(self, table):
        if (
            self._check_unique_values_in_column(table=table, column_name="R1")
            is not True
        ):
            raise ValueError("R1 must must be unique")

    def _check_all_R2_unique(self, table):
        if (
            self._check_unique_values_in_column(table=table, column_name="R2")
            is not True
        ):
            raise ValueError("R2 must must be unique")

    def _check_unique_names(self, table):
        table["unique_name"] = table.apply(
            lambda x: x["sample_name"] + "_" + x["standard_sample_name"], axis=1
        )

        if (
            self._check_unique_values_in_column(table=table, column_name="unique_name")
            is not True
        ):
            raise ValueError("sample_name_standard_sample_name must must be unique")

    def write_record(self, record_type):
        records = {"experimental": self.experimental, "stock": self.stock}
        record_paths = {
            "experimental": self.run_paths.record_experimental,
            "stock": self.run_paths.record_stock,
        }

        records[record_type].to_csv(record_paths[record_type], index=None)
