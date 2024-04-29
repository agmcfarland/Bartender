conda activate bbmap_env

input_dir=/data/bar_lab/small_scale_barcode_analyses/tests/data/ete1

output_dir=/data/bar_lab/small_scale_barcode_analyses/tests/data/ete1/downsampled

mkdir $output_dir

mkdir $input_dir"/full"

for R1_file in ${input_dir}/*R1*.fastq.gz; do
	# echo $R1_file
	R2_file="${R1_file/R1_001.trimmed.fastq.gz/R2_001.trimmed.fastq.gz}"
	# echo $R2_file
	R1_file_out=$output_dir/$(basename "$R1_file")
	R2_file_out=$output_dir/$(basename "$R2_file")
	reformat.sh in="$R1_file" in2="$R2_file" out="$R1_file_out" out2="$R2_file_out" reads=500 ow=t
done

mv *.fastq.gz ./full

mv $output_dir/*.fastq.gz ./full

rm -R $output_dir