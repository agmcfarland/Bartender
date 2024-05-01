# Bartender

<!-- Badges start -->
[![Tests](https://github.com/agmcfarland/Bartender/actions/workflows/python-app.yml/badge.svg)](https://github.com/agmcfarland/Bartender/actions/workflows/python-app.yml)

[![TestsConda](https://github.com/agmcfarland/Bartender/actions/workflows/conda-deployment.yml/badge.svg)](https://github.com/agmcfarland/Bartender/actions/workflows/conda-deployment.yml)

[![Lint](https://github.com/agmcfarland/Bartender/actions/workflows/black.yml/badge.svg)](https://github.com/agmcfarland/Bartender/actions/workflows/black.yml)

[![codecov](https://codecov.io/gh/agmcfarland/Bartender/graph/badge.svg?token=447XKVI3NG)](https://codecov.io/gh/agmcfarland/Bartender)
<!-- Badges end -->

# Usage

## Bartender

```md
usage: Bartender [-h] [--output_dir OUTPUT_DIR] [--run_name RUN_NAME] [--experimental_file EXPERIMENTAL_FILE] [--stock_file STOCK_FILE] [--upstream_nucleotide_match UPSTREAM_NUCLEOTIDE_MATCH]
                 [--downstream_nucleotide_match DOWNSTREAM_NUCLEOTIDE_MATCH] [--barcode_length BARCODE_LENGTH] [--hamming_distance HAMMING_DISTANCE] [--no_copy] [--dry]

options:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR
                        Path to output directory
  --run_name RUN_NAME   Name of the run
  --experimental_file EXPERIMENTAL_FILE
                        Path to experimental input csv file [None]
  --stock_file STOCK_FILE
                        Path to stock input csv file [None]
  --upstream_nucleotide_match UPSTREAM_NUCLEOTIDE_MATCH
                        Upstream nucleotide sequence to match [TAGCATAA]
  --downstream_nucleotide_match DOWNSTREAM_NUCLEOTIDE_MATCH
                        Downstream nucleotide sequence to match [ATGGAAGAA]
  --barcode_length BARCODE_LENGTH
                        Length of barcode to capture [35]
  --hamming_distance HAMMING_DISTANCE
                        Hamming distance to find closest potential barcode [3]
  --no_copy             Don't make a copy of the work folder prior to a run [False]
  --dry                 Print arguments and exit program [False]
```

## Bartender reports

```md
usage: BuildReport [-h] [--run_dir RUN_DIR] [--experimental_report] [--stock_report] [--report_table_type_1] [--experimental_trend_width EXPERIMENTAL_TREND_WIDTH] [--experimental_trend_height EXPERIMENTAL_TREND_HEIGHT]
                   [--per_experimental_group_width PER_EXPERIMENTAL_GROUP_WIDTH] [--per_experimental_group_height PER_EXPERIMENTAL_GROUP_HEIGHT] [--dry] [--Rscript_path RSCRIPT_PATH]

options:
  -h, --help            show this help message and exit
  --run_dir RUN_DIR     Path to run directory [None]
  --experimental_report
                        Make experimental report [False]
  --stock_report        Make stock report [False]
  --report_table_type_1
                        Make report table with counts [False]
  --experimental_trend_width EXPERIMENTAL_TREND_WIDTH
                        Width [15]
  --experimental_trend_height EXPERIMENTAL_TREND_HEIGHT
                        Height [15]
  --per_experimental_group_width PER_EXPERIMENTAL_GROUP_WIDTH
                        Width [15]
  --per_experimental_group_height PER_EXPERIMENTAL_GROUP_HEIGHT
                        Height [15]
  --dry                 Print arguments and exit program [False]
  --Rscript_path RSCRIPT_PATH
                        Path to Rscript [/usr/bin/]
```


# Example input tables

## Stock

```md
| sample_name | biological_group | input_template | R1                                               | R2                                               |
| ----------- | ---------------- | -------------- | ------------------------------------------------ | ------------------------------------------------ |
| stock_1     | CD4_derived_TF   | 50000          | /path/to/stock_1_S1_L001_R1_001.trimmed.fastq.gz | /path/to/stock_1_S1_L001_R2_001.trimmed.fastq.gz |
| stock_2     | CD4_derived_TF   | 50000          | /path/to/stock_2_S2_L001_R1_001.trimmed.fastq.gz | /path/to/stock_2_S2_L001_R2_001.trimmed.fastq.gz |
| stock_3     | CD4_derived_TF   | 50000          | /path/to/stock_3_S3_L001_R1_001.trimmed.fastq.gz | /path/to/stock_3_S3_L001_R2_001.trimmed.fastq.gz |
| stock_4     | CD4_derived_TF   | 50000          | /path/to/stock_4_S4_L001_R1_001.trimmed.fastq.gz | /path/to/stock_4_S4_L001_R2_001.trimmed.fastq.gz |
| stock_5     | CD4_derived_TF   | 50000          | /path/to/stock_5_S5_L001_R1_001.trimmed.fastq.gz | /path/to/stock_5_S5_L001_R2_001.trimmed.fastq.gz |
```

## Experimental


```md
| sample_name            | biological_group | cell_type | time_point | time_point_description | organ  | input_template | genetic_source | R1                                                           | R2                                                           |
| ---------------------- | ---------------- | --------- | ---------- | ---------------------- | ------ | -------------- | -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| sample1_d27_PLASMA_S12 | animal1          | unknown   | 27         | unknown                | plasma | 10000          | dna            | /path/to/sample1_d27_PLASMA_S12_L001_R1_001.trimmed.fastq.gz | /path/to/sample1_d27_PLASMA_S12_L001_R2_001.trimmed.fastq.gz |
| sample2_d27_PLASMA_S20 | animal1          | unknown   | 27         | unknown                | plasma | 10000          | dna            | /path/to/sample2_d27_PLASMA_S20_L001_R1_001.trimmed.fastq.gz | /path/to/sample2_d27_PLASMA_S20_L001_R2_001.trimmed.fastq.gz |
| sample3_d27_PLASMA_S21 | animal2          | unknown   | 27         | unknown                | plasma | 10000          | dna            | /path/to/sample3_d27_PLASMA_S21_L001_R1_001.trimmed.fastq.gz | /path/to/sample3_d27_PLASMA_S21_L001_R2_001.trimmed.fastq.gz |
| sample4_d27_PLASMA_S22 | animal1          | unknown   | 27         | unknown                | plasma | 10000          | dna            | /path/to/sample4_d27_PLASMA_S22_L001_R1_001.trimmed.fastq.gz | /path/to/sample4_d27_PLASMA_S22_L001_R2_001.trimmed.fastq.gz |
| sample5_d27_PLASMA_S22 | animal3          | unknown   | 27         | unknown                | plasma | 10000          | dna            | /path/to/sample5_d27_PLASMA_S5_L001_R1_001.trimmed.fastq.gz  | /path/to/sample5_d27_PLASMA_S5_L001_R2_001.trimmed.fastq.gz  |
```
