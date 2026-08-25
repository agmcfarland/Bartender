import sys
import argparse
import os
from os.path import join as pjoin
from Utils.ReportTable import ReportTable
from Utils.StandardBarcodeName import StandardBarcodeName
from Utils.SetupManager import SetupManager


def parse_arguments():
    parser = argparse.ArgumentParser(prog="BartenderReport")
    parser.add_argument(
        "--run_dir", type=str, default="", help="Path to run directory [None]"
    )
    parser.add_argument(
        "--experimental_summary_table",
        action="store_true",
        default=False,
        help="Make experimental summary table [False]",
    )
    parser.add_argument(
        "--experimental_report",
        action="store_true",
        default=False,
        help="Make experimental report [False]",
    )
    parser.add_argument(
        "--stock_report",
        action="store_true",
        default=False,
        help="Make stock report [False]",
    )
    parser.add_argument(
        "--report_table_type_1",
        action="store_true",
        default=False,
        help="Make report table with counts [False]",
    )
    parser.add_argument(
        "--experimental_trend_width", type=int, default=15, help="Width [15]"
    )
    parser.add_argument(
        "--experimental_trend_height", type=int, default=15, help="Height [15]"
    )
    parser.add_argument(
        "--per_experimental_group_width", type=int, default=15, help="Width [15]"
    )
    parser.add_argument(
        "--per_experimental_group_height", type=int, default=15, help="Height [15]"
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        default=False,
        help="Print arguments and exit program [False]",
    )
    parser.add_argument(
        "--Rscript_path",
        type=str,
        default="/usr/bin/",
        help="Path to Rscript [/usr/bin/]",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.dry:
        print(args)
        sys.exit()

    if not os.path.exists(args.run_dir):
        raise ValueError(f"run_dir {args.run_dir} does not exist")

    build_report_dir = pjoin(os.path.dirname(os.path.realpath(__file__)), "Reports")

    print(build_report_dir)

    if args.experimental_report:
        experimental_report_path = pjoin(build_report_dir, "experimental.Rmd")

        experimental_report_output_path = pjoin(
            args.run_dir, "output", "experimental.html"
        )

        os.system(
            f"{args.Rscript_path}Rscript -e \"rmarkdown::render('{experimental_report_path}', params = list(run_dir = '{args.run_dir}', experimental_trend_width = '{args.experimental_trend_width}', experimental_trend_height = '{args.experimental_trend_height}', per_experimental_group_width = '{args.per_experimental_group_width}', per_experimental_group_height = '{args.per_experimental_group_height}'), output_file='{experimental_report_output_path}')\""
        )

    if args.stock_report:
        stock_report_path = pjoin(build_report_dir, "stock.Rmd")

        stock_report_output_path = pjoin(args.run_dir, "output", "stock.html")

        os.system(
            f"{args.Rscript_path}Rscript -e \"rmarkdown::render('{stock_report_path}', params = list(run_dir = '{args.run_dir}'), output_file='{stock_report_output_path}')\""
        )

    if args.report_table_type_1:
        standard_barcode_names = StandardBarcodeName(
            setup_manager=SetupManager(work_dir=args.run_dir)
        )

        standard_barcode_names.assign_standard_barcode_names()

        standard_barcode_names.write_to_file()

        report_table = ReportTable(setup_manager=SetupManager(work_dir=args.run_dir))

        report_table.make_report_table_type_1_counts()

        report_table.write_report_table_type_1_to_excel("count")

        report_table.transform_table_type_1_to_proportions()

        report_table.write_report_table_type_1_to_excel("proportion")

    if args.experimental_summary_table:
        report_table = ReportTable(setup_manager=SetupManager(work_dir=args.run_dir))

        report_table.proportion_and_count_summary()

        report_table.write_proportion_and_count_summary()


if __name__ == "__main__":
    sys.exit(main())
