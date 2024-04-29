import argparse
import sys
import os
import pandas as pd
import re
import shutil
from os.path import join as pjoin
from glob import glob
from Utils.SetupManager import SetupManager
from Utils.BarcodeProcessor import BarcodeProcessor
from Utils.StandardBarcodeName import StandardBarcodeName
import time


def parse_arguments():
    parser = argparse.ArgumentParser(prog="Bartender")
    parser.add_argument("--output_dir", type=str, help="Path to output directory")
    parser.add_argument("--run_name", type=str, default="work", help="Name of the run")
    parser.add_argument(
        "--experimental_file",
        type=str,
        default=None,
        help="Path to experimental input csv file [None]",
    )
    parser.add_argument(
        "--stock_file",
        type=str,
        default=None,
        help="Path to stock input csv file [None]",
    )
    parser.add_argument(
        "--upstream_nucleotide_match",
        type=str,
        default="TAGCATAA",
        help="Upstream nucleotide sequence to match [TAGCATAA]",
    )
    parser.add_argument(
        "--downstream_nucleotide_match",
        type=str,
        default="ATGGAAGAA",
        help="Downstream nucleotide sequence to match [ATGGAAGAA]",
    )
    parser.add_argument(
        "--barcode_length",
        type=int,
        default=35,
        help="Length of barcode to capture [35]",
    )
    parser.add_argument(
        "--hamming_distance",
        type=int,
        default=3,
        help="Hamming distance to find closest potential barcode [3]",
    )
    parser.add_argument(
        "--no_copy",
        action="store_true",
        default=False,
        help="Don't make a copy of the work folder prior to a run [False]",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        default=False,
        help="Print arguments and exit program [False]",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.dry:
        print(args)
        sys.exit()

    if args.no_copy is False:
        prior_run_dir = pjoin(args.output_dir, args.run_name)
        if os.path.exists(prior_run_dir):
            print("Making copy of previous results")
            shutil.copytree(
                src=prior_run_dir, dst=pjoin(args.output_dir, args.run_name + "_prior")
            )

    bartender_setup = SetupManager(
        work_dir=pjoin(args.output_dir, args.run_name),
        experimental_file=args.experimental_file,
        stock_file=args.stock_file,
    )

    # Identify barcodes
    samples = BarcodeProcessor(
        setup_manager=bartender_setup,
        barcode_length=args.barcode_length,
        cutoff=args.hamming_distance,
    )

    start = time.time()
    samples.process_stock_samples()
    print(time.time() - start)

    start = time.time()
    samples.process_experimental_samples()
    print(time.time() - start)

    # Standardized barcode names
    standard_barcode_names = StandardBarcodeName(setup_manager=bartender_setup)

    standard_barcode_names.assign_standard_barcode_names()

    standard_barcode_names.write_to_file()

    # Record run data and clean up
    if args.stock_file is not None:
        bartender_setup.record.write_record(record_type="stock")

    try:
        bartender_setup.record.write_record(record_type="experimental")
    except:
        print("Did not write experimental record")

    samples.delete_temp_processing_dir()


if __name__ == "__main__":
    sys.exit(main())
