from os.path import join as pjoin
import os
import pandas as pd
import re
from glob import glob
from Utils.SetupManager import SetupManager
from Utils.Common import find_subtring_match


class ReportTable:
    def __init__(self, setup_manager):
        self.setup_manager = setup_manager
        self.experimental_table = pd.DataFrame()

    def _load_standard_barcode_names(self):
        """ """
        return pd.read_csv(
            pjoin(self.setup_manager.run_paths.output, "standard_barcode_names.csv")
        )

    def _read_in_experimental_samples(self):
        """ """
        for f in glob(
            pjoin(self.setup_manager.run_paths.experimental, "*_processed.csv")
        ):
            df = pd.read_csv(f)
            df["file_tag"] = os.path.basename(f).replace("_processed.csv", "")
            self.experimental_table = pd.concat([self.experimental_table, df])

    def _map_standard_barcode_names_to_barcodes(self):
        self.experimental_table = self.experimental_table.merge(
            self._load_standard_barcode_names(),
            on="barcode",
            how="left",
            indicator=True,
        )

    def proportion_and_count_summary(self):
        self._read_in_experimental_samples()

        self._map_standard_barcode_names_to_barcodes()

        unique_stock_ids = self.setup_manager.record.unique_stock_biological_groups()

        unique_stock_ids.append("stock")

        unique_stock_ids.append("experimental")

        unique_stock_ids_regex = [re.compile(stock_id) for stock_id in unique_stock_ids]

        self.experimental_table["stock_source"] = self.experimental_table[
            "standard_barcode_name"
        ].apply(lambda x: find_subtring_match(x, unique_stock_ids_regex))

        self.experimental_table = self.experimental_table[
            self.experimental_table["trusted_proportion"] > 0
        ]

        self.experimental_summary_table_counts = self._experimental_summary_table(
            proportion=False
        )

        self.experimental_summary_table_proportions = self._experimental_summary_table(
            proportion=True
        )

    def write_proportion_and_count_summary(self):
        self.experimental_summary_table_counts.to_csv(
            pjoin(
                self.setup_manager.run_paths.output, "experimental_summary_counts.csv"
            ),
            index=None,
        )
        self.experimental_summary_table_proportions.to_csv(
            pjoin(
                self.setup_manager.run_paths.output,
                "experimental_summary_proportion.csv",
            ),
            index=None,
        )

    def _experimental_summary_table(self, proportion: bool = False):
        """
        Create summary table at the level of each unique stock, experiment only, shared stock only, and total_sum
        """

        summary = (
            self.experimental_table.groupby(["file_tag", "stock_source"])["total"]
            .sum()
            .reset_index()
        )

        summary.rename(columns={"total": "total_sum"}, inplace=True)

        summary = summary.pivot(
            index="file_tag", columns="stock_source", values="total_sum"
        ).reset_index()

        # Fill any NaN values with 0 if needed
        summary.fillna(0, inplace=True)

        summary.columns.name = None

        stock_total = summary.loc[
            :, ~summary.columns.isin(["file_tag", "experimental"])
        ].sum(axis=1)

        summary["stock_total"] = stock_total

        all_total = summary.loc[
            :, summary.columns.isin(["stock_total", "experimental"])
        ].sum(axis=1)

        summary["all_total"] = all_total

        summary = summary.rename(
            columns={"stock": "shared_stock", "experimental": "experimental_only"}
        )

        if proportion:
            columns_to_normalize = summary.columns.difference(["file_tag"])

            summary[columns_to_normalize] = summary[columns_to_normalize].div(
                summary["all_total"], axis=0
            )

        df_metadata = self.setup_manager.record.experimental[
            [
                "standard_sample_name",
                "biological_group",
                "cell_type",
                "time_point",
                "organ",
                "genetic_source",
            ]
        ].drop_duplicates()

        summary = df_metadata.merge(
            summary, left_on="standard_sample_name", right_on="file_tag"
        )

        summary = summary.sort_values(
            ["biological_group", "time_point", "cell_type", "organ", "genetic_source"],
            ascending=[True, True, False, True, False],
        )

        summary = summary.drop(columns=["file_tag"])

        return summary

    def _make_condensed_experimental_record(self, biological_group):
        """
        Remove all replicates and get the mean input_template
        """
        df_bg_record = self.setup_manager.record.experimental.copy(deep=True)

        df_bg_record = df_bg_record[
            df_bg_record["biological_group"] == biological_group
        ]

        condensed_df = (
            df_bg_record.groupby("standard_sample_name")
            .agg({"input_template": "mean"})
            .reset_index()
        )

        df_bg_record = pd.merge(
            condensed_df,
            df_bg_record[
                [
                    "biological_group",
                    "cell_type",
                    "time_point",
                    "organ",
                    "genetic_source",
                    "standard_sample_name",
                ]
            ],
            on="standard_sample_name",
            how="left",
        )

        df_bg_record = df_bg_record.drop_duplicates()

        return df_bg_record

    def make_report_table_type_1(self):
        pd.options.mode.chained_assignment = None

        self._read_in_experimental_samples()

        self._map_standard_barcode_names_to_barcodes()

        self.type_1_experiment_table = []

        for biological_group_ in (
            self.setup_manager.record.experimental["biological_group"].unique().tolist()
        ):
            df_bg = self.experimental_table.copy(deep=True)

            df_bg = df_bg[
                df_bg["file_tag"].isin(
                    self.setup_manager.record.experimental[
                        "standard_sample_name"
                    ].tolist()
                )
            ]

            df_bg = df_bg[df_bg["trusted_proportion"] > 0]

            df_bg_record = self._make_condensed_experimental_record(
                biological_group=biological_group_
            )

            df_bg_record = df_bg_record.sort_values(
                ["time_point", "cell_type", "organ", "genetic_source"],
                ascending=[True, False, True, False],
            )

            self.counts = pd.DataFrame(columns=["barcode", "standard_barcode_name"])

            for _, sample in df_bg_record.iterrows():
                df_sample = df_bg[df_bg["file_tag"] == sample.standard_sample_name]

                if len(df_sample) > 0:
                    df_sample[sample.standard_sample_name] = df_sample["total"]

                    df_sample = df_sample[
                        [
                            "standard_barcode_name",
                            "barcode",
                            sample.standard_sample_name,
                        ]
                    ]

                    self.counts = self.counts.merge(
                        df_sample, on=["barcode", "standard_barcode_name"], how="outer"
                    )

            self.experimental_details = pd.DataFrame()

            for _, sample in df_bg_record.iterrows():
                df_sample = df_bg[df_bg["file_tag"] == sample.standard_sample_name]

                if len(df_sample) > 0:
                    self.experimental_details = pd.concat(
                        [
                            self.experimental_details,
                            pd.DataFrame(
                                [
                                    {
                                        "standard_sample_name": sample.standard_sample_name,
                                        "cell_type": sample.cell_type,
                                        "organ": sample.organ,
                                        "genetic_source": sample.genetic_source,
                                        "time_point": sample.time_point,
                                        "template": sample.input_template,
                                        "sequences": df_sample["total"].sum(),
                                        "unique": len(df_sample),
                                    }
                                ]
                            ),
                        ]
                    )

            self.experimental_details = self.experimental_details.T

            self.experimental_details.insert(
                0, "attributes", self.experimental_details.index
            )

            self.experimental_details = self.experimental_details.reset_index(drop=True)

            self.experimental_details.insert(
                0, "other", [biological_group_, "", "", "", "", "", "", ""]
            )

            self.experimental_details.columns = self.counts.columns

            faux_columns = pd.DataFrame(self.counts.columns.tolist())

            faux_columns = faux_columns.T

            faux_columns.columns = self.counts.columns.tolist()

            self.counts["total"] = self.counts.select_dtypes(include="number").mean(
                axis=1
            )

            self.counts = self.counts.sort_values("total", ascending=False)

            self.counts.drop(columns="total", inplace=True)

            self.counts = self.counts.fillna(0)

            self.combined_details_counts = pd.concat(
                [self.experimental_details, faux_columns], axis=0, ignore_index=True
            )

            self.combined_details_counts = pd.concat(
                [self.combined_details_counts, self.counts], axis=0, ignore_index=True
            )

            self.type_1_experiment_table.append(self.combined_details_counts)

    def write_report_table_type_1_to_excel(self):
        try:
            os.remove(
                pjoin(
                    self.setup_manager.run_paths.output,
                    "barcode_report_table_type_1.xlsx",
                )
            )
        except:
            pass

        with pd.ExcelWriter(
            pjoin(
                self.setup_manager.run_paths.output, "barcode_report_table_type_1.xlsx"
            )
        ) as writer:
            for table in self.type_1_experiment_table:
                biological_group = table.iloc[0, 0]

                table.to_excel(
                    writer, sheet_name=biological_group, index=False, header=False
                )
