import os
from os.path import join as pjoin
import shutil
from glob import glob
import multiprocessing as mp
import subprocess
from glob import glob
import re
from Utils.SampleRead import SampleRead
from Utils.Stock import Stock
from Utils.Experimental import Experimental


class BarcodeProcessor:
    def __init__(
        self,
        setup_manager,
        barcode_length,
        upstream_nucleotide_match="TAGCATAA",
        downstream_nucleotide_match="ATGGAAGAA",
        cutoff=1,
    ):
        self.setup_manager = setup_manager
        self.upstream_nucleotide_match = upstream_nucleotide_match
        self.downstream_nucleotide_match = downstream_nucleotide_match
        self.barcode_length = barcode_length
        self.cutoff = cutoff

    def delete_temp_processing_dir(self):
        if os.path.exists(self.setup_manager.run_paths.temp):
            shutil.rmtree(self.setup_manager.run_paths.temp)

    def build_temp_processing_dir(self):
        """ """
        self.delete_temp_processing_dir()

        os.makedirs(self.setup_manager.run_paths.temp)

    def _gather_samples_to_process(self, sample_type):
        processing_sheets = {
            "experimental": self.setup_manager.experimental,
            "stock": self.setup_manager.stock,
        }

        samples_to_process = []

        for _, sample_row in processing_sheets[sample_type].iterrows():
            samples_to_process.append(
                SampleRead.build_from_table_series(
                    table_row=sample_row,
                    setup_manager=self.setup_manager,
                    upstream_nucleotide_match=self.upstream_nucleotide_match,
                    downstream_nucleotide_match=self.downstream_nucleotide_match,
                    barcode_length=self.barcode_length,
                )
            )

        return samples_to_process

    def process_experimental_samples(self):
        """
        extract barcodes from new samples
        """
        stock = Stock(
            setup_manager=self.setup_manager, barcode_length=self.barcode_length
        )

        if self.setup_manager.experimental_file is not None:
            self.build_temp_processing_dir()

            with mp.Pool(processes=os.cpu_count()) as p:
                p.map(
                    SampleRead.find_barcodes_in_sample,
                    self._gather_samples_to_process(sample_type="experimental"),
                )
            experimental = Experimental(
                setup_manager=self.setup_manager,
                barcode_length=self.barcode_length,
                stock=stock,
            )

            experimental.process_new_samples()

        if self.setup_manager.record.experimental is not None:
            experimental = Experimental(
                setup_manager=self.setup_manager,
                barcode_length=self.barcode_length,
                stock=stock,
                cutoff=self.cutoff,
            )

            experimental.make_filtered_barcodes()

    def process_stock_samples(self):
        if self.setup_manager.stock_file is not None:
            self.build_temp_processing_dir()

            with mp.Pool(processes=os.cpu_count()) as p:
                p.map(
                    SampleRead.find_barcodes_in_sample,
                    self._gather_samples_to_process(sample_type="stock"),
                )

            stock = Stock(
                setup_manager=self.setup_manager, barcode_length=self.barcode_length
            )

            df_raw_stock = stock._update_raw_stock_table()

            df_raw_stock.to_csv(
                pjoin(self.setup_manager.run_paths.stock_barcodes_raw), index=None
            )

            df_filtered_stock = stock.make_filtered_stock_table()

            df_filtered_stock.to_csv(
                pjoin(self.setup_manager.run_paths.stock_barcodes_filtered), index=None
            )
