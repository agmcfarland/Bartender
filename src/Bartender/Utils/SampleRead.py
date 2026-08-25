import pandas as pd
import gzip
import re
import subprocess
import os
from os.path import join as pjoin
from Bio import SeqIO


class SampleRead:
    def __init__(
        self,
        sample_name,
        biological_group,
        standard_sample_name,
        R1,
        R2,
        setup_manager,
        upstream_nucleotide_match,
        downstream_nucleotide_match,
        barcode_length,
    ):
        self.sample_name = sample_name
        self.biological_group = biological_group
        self.standard_sample_name = standard_sample_name
        self.R1 = R1
        self.R2 = R2
        self.setup_manager = setup_manager
        self.upstream_nucleotide_match = upstream_nucleotide_match
        self.downstream_nucleotide_match = downstream_nucleotide_match
        self.barcode_length = barcode_length
        self.fastp_filename = pjoin(
            self.setup_manager.run_paths.temp,
            self.sample_name,
            self.standard_sample_name,
        )
        os.makedirs(pjoin(self.setup_manager.run_paths.temp, self.sample_name))

    @classmethod
    def build_from_table_series(
        cls,
        table_row: pd.Series,
        setup_manager,
        upstream_nucleotide_match,
        downstream_nucleotide_match,
        barcode_length,
    ):
        """
        Construct class from a single row (type pandas.Series) of sample sheet (type pandas.dataframe)
        """
        return cls(
            sample_name=table_row["sample_name"],
            biological_group=table_row["biological_group"],
            R1=table_row["R1"],
            R2=table_row["R2"],
            standard_sample_name=table_row["standard_sample_name"],
            setup_manager=setup_manager,
            upstream_nucleotide_match=upstream_nucleotide_match,
            downstream_nucleotide_match=downstream_nucleotide_match,
            barcode_length=barcode_length,
        )

    def merge_paired_reads(self):
        subprocess.call(
            [
                "fastp",
                "-i",
                self.R1,
                "-I",
                self.R2,
                "-j",
                self.fastp_filename + ".json",
                "-h",
                self.fastp_filename + ".html",
                "--merge",
                "--merged_out",
                self.fastp_filename + "_merged.fastq.gz",
                "--disable_adapter_trimming",
                "--thread",
                "1",
            ]
        )

    def find_barcodes_in_sample(self):
        self.merge_paired_reads()

        barcodes = self.extract_barcode()

        df_barcodes = self.barcodes_to_table(barcodes)

        self.write_raw_barcodes_to_table(df_barcodes=df_barcodes)

    def extract_barcode(self):
        barcodes = []

        with gzip.open(
            pjoin(self.fastp_filename + "_merged.fastq.gz"), "rt"
        ) as input_handle:
            for record in SeqIO.parse(input_handle, "fastq"):
                barcode = re.findall(
                    rf"(?<={self.upstream_nucleotide_match}).*?(?={self.downstream_nucleotide_match})",
                    str(record.seq),
                )

                if len(barcode) != 1:
                    barcode = re.findall(
                        rf"(?<={self.downstream_nucleotide_match}).*?(?={self.upstream_nucleotide_match})",
                        str(record.seq),
                    )

                if len(barcode) == 1:
                    if (
                        len(barcode[0]) == 0
                    ):  # no barcode between upstream and downstream
                        continue
                    barcodes.append(barcode[0])

        return barcodes

    def barcodes_to_table(self, barcodes):
        df_barcodes = pd.DataFrame(data={"barcode": barcodes})

        df_barcodes = (
            df_barcodes.groupby("barcode")
            .size()
            .reset_index(name=self.standard_sample_name)
            .sort_values([self.standard_sample_name], ascending=False)
        )

        return df_barcodes

    def write_raw_barcodes_to_table(self, df_barcodes):
        df_barcodes.to_csv(pjoin(self.fastp_filename + "_barcode.csv"), index=False)
