import os
from os.path import join as pjoin


class FilePaths:
    def __init__(self, work_dir):
        self.work_dir = work_dir
        self.record = pjoin(self.work_dir, "record")
        self.stock = pjoin(self.work_dir, "stock")
        self.experimental = pjoin(self.work_dir, "experimental")
        self.output = pjoin(self.work_dir, "output")
        self.temp = pjoin(self.work_dir, "temp")
        self.stock_barcodes_filtered = pjoin(self.stock, "stock_barcodes_filtered.csv")
        self.stock_barcodes_raw = pjoin(self.stock, "stock_barcodes_raw.csv")
        self.record_stock = pjoin(self.record, "stock.csv")
        self.record_experimental = pjoin(self.record, "experimental.csv")

    def make_work_dir_tree(self):
        os.makedirs(self.work_dir, exist_ok=True)
        for folder_name in ["record", "stock", "experimental", "output"]:
            os.makedirs(pjoin(self.work_dir, folder_name), exist_ok=True)
