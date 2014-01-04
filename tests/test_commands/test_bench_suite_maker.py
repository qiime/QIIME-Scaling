#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main
from pyqi.core.exception import CommandError
from scaling.commands.bench_suite_maker import BenchSuiteMaker

class BenchSuiteMakerTests(TestCase):
	def setUp(self):
		"""Set up data for use in unit tests"""
		self.cmd = BenchSuiteMaker()

		self.command = "pick_otus.py"
		self.command2 = "split_libraries_fastq.py -m mapping.txt"
		self.command3 = "parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna"

		self.param_single = {'jobs_to_start' : ["8", "16", "32"]}
		self.param_mult = {'jobs_to_start' : ["8", "16", "32"],
								'similarity' : ["0.94", "0.97", "0.99"]}

		self.bench_files_single = [["1000000.fna"],
								   ["2000000.fna"],
								   ["3000000.fna"]]
		self.bench_files_mult = [["reads/1000000.fna",
									"barcodes/1000000.fna"],
								 ["reads/2000000.fna",
								 	"barcodes/2000000.fna"],
								 ["reads/3000000.fna",
								 	"barcodes/3000000.fna"]]

		self.in_opts_single = ['-i']
		self.in_opts_mult = ['-i', '-b']

	def test_single_input_file_suite(self):
		"""Bench suite correctly generated with a single input file command"""
		obs = self.cmd(command=self.command,
						bench_files=self.bench_files_single)
		self.assertEqual(obs.keys(), ['bench_suite'])
		obs = obs['bench_suite']
		self.assertEqual(obs, single_file_suite)

		obs = self.cmd(command=self.command,
						bench_files=self.bench_files_single,
						in_opts=self.in_opts_single)
		self.assertEqual(obs.keys(), ['bench_suite'])
		obs = obs['bench_suite']
		self.assertEqual(obs, single_file_suite)

	def test_multiple_input_files_suite(self):
		"""Bench suite correctly generated with multiple input files command"""
		obs = self.cmd(command=self.command2,
						bench_files=self.bench_files_mult,
						in_opts=self.in_opts_mult)
		self.assertEqual(obs.keys(), ['bench_suite'])
		obs = obs['bench_suite']
		self.assertEqual(obs, multiple_file_suite)

	def test_single_parameter_suite(self):
		"""Bench suite correctly generated with a single parameter"""
		obs = self.cmd(command=self.command3,
						parameters=self.param_single)
		self.assertEqual(obs.keys(), ['bench_suite'])
		obs = obs['bench_suite']
		self.assertEqual(obs, single_parameter_suite)

	def test_multiple_parameter_suite(self):
		"""Bench suite correctly generated with multiple parameters"""
		obs = self.cmd(command=self.command3,
						parameters=self.param_mult)
		self.assertEqual(obs.keys(), ['bench_suite'])
		obs = obs['bench_suite']
		self.assertEqual(obs, multiple_parameter_suite)

	def test_invalid_input(self):
		"""Correctly handles invalid input by raising a CommandError."""
		# Too many options
		with self.assertRaises(CommandError):
			_ = self.cmd(command=self.command,
						 parameters=self.param_single,
						 bench_files=self.bench_files_single)

		# Multiple bench files are provided, but only a single in_opt
		with self.assertRaises(CommandError):
			_ = self.cmd(command=self.command,
						 bench_files=self.bench_files_mult)

		with self.assertRaises(CommandError):
			_ = self.cmd(command=self.command,
						 bench_files=self.bench_files_mult,
						 in_opts=self.in_opts_single)

		# Single bench files are provided, but multiple in_opts
		with self.assertRaises(CommandError):
			_ = self.cmd(command=self.command,
						 bench_files=self.bench_files_single,
						 in_opts=self.in_opts_mult)

single_file_suite = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/pick_otus$date
mkdir $dest

# Create output directory structure
output_dest = $dest"/command_outputs"
timing_dest = $dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/1000000
mkdir $timing_dest/1000000
mkdir $output_dest/2000000
mkdir $timing_dest/2000000
mkdir $output_dest/3000000
mkdir $timing_dest/3000000
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/1000000/$i.txt pick_otus.py -i 1000000.fna -o $output_dest/1000000/$i
    timing_wrapper.sh $timing_dest/2000000/$i.txt pick_otus.py -i 2000000.fna -o $output_dest/2000000/$i
    timing_wrapper.sh $timing_dest/3000000/$i.txt pick_otus.py -i 3000000.fna -o $output_dest/3000000/$i
done

# Get the benchmark results and produce the plots
scaling process-bench-results -i $timing_dest/ -o $dest/plots/
"""

multiple_file_suite = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/split_libraries_fastq$date
mkdir $dest

# Create output directory structure
output_dest = $dest"/command_outputs"
timing_dest = $dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/1000000
mkdir $timing_dest/1000000
mkdir $output_dest/2000000
mkdir $timing_dest/2000000
mkdir $output_dest/3000000
mkdir $timing_dest/3000000
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/1000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/1000000.fna -b barcodes/1000000.fna -o $output_dest/1000000/$i
    timing_wrapper.sh $timing_dest/2000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/2000000.fna -b barcodes/2000000.fna -o $output_dest/2000000/$i
    timing_wrapper.sh $timing_dest/3000000/$i.txt split_libraries_fastq.py -m mapping.txt -i reads/3000000.fna -b barcodes/3000000.fna -o $output_dest/3000000/$i
done

# Get the benchmark results and produce the plots
scaling process-bench-results -i $timing_dest/ -o $dest/plots/
"""

single_parameter_suite = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/parallel_pick_otus_uclust_ref$date
mkdir $dest

# Create output directory structure
output_dest = $dest"/command_outputs"
timing_dest = $dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/jobs_to_start
mkdir $timing_dest/jobs_to_start
mkdir $output_dest/jobs_to_start/8
mkdir $timing_dest/jobs_to_start/8
mkdir $output_dest/jobs_to_start/16
mkdir $timing_dest/jobs_to_start/16
mkdir $output_dest/jobs_to_start/32
mkdir $timing_dest/jobs_to_start/32
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/jobs_to_start/8/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 8 -o $output_dest/jobs_to_start/8/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/16/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 16 -o $output_dest/jobs_to_start/16/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/32/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 32 -o $output_dest/jobs_to_start/32/$i
done

# Get the benchmark results and produce the plots
mkdir $dest/plots
scaling process-bench-results -i $timing_dest/jobs_to_start -o $dest/plots/jobs_to_start
"""

multiple_parameter_suite = """#!/bin/bash

# Number of times each command should be executed
num_rep=1

# Check if the user supplied a (valid) number of repetitions
if [[ $# -eq 1 ]]; then
    if [[ $1 =~ ^[0-9]+$ ]]; then
        num_rep=$1
    else
        echo "USAGE: $0 [num_reps]"
    fi
fi

# Get a string with current date (format YYYYMMDD_HHMMSS) to name
# the directory with the benchmark results
cdate=`date +_%Y%m%d_%H%M%S`
dest=$PWD/parallel_pick_otus_uclust_ref$date
mkdir $dest

# Create output directory structure
output_dest = $dest"/command_outputs"
timing_dest = $dest"/timing"

mkdir $output_dest
mkdir $timing_dest
mkdir $output_dest/jobs_to_start
mkdir $timing_dest/jobs_to_start
mkdir $output_dest/jobs_to_start/8
mkdir $timing_dest/jobs_to_start/8
mkdir $output_dest/jobs_to_start/16
mkdir $timing_dest/jobs_to_start/16
mkdir $output_dest/jobs_to_start/32
mkdir $timing_dest/jobs_to_start/32
mkdir $output_dest/similarity
mkdir $timing_dest/similarity
mkdir $output_dest/similarity/0.94
mkdir $timing_dest/similarity/0.94
mkdir $output_dest/similarity/0.97
mkdir $timing_dest/similarity/0.97
mkdir $output_dest/similarity/0.99
mkdir $timing_dest/similarity/0.99
# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
    timing_wrapper.sh $timing_dest/jobs_to_start/8/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 8 -o $output_dest/jobs_to_start/8/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/16/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 16 -o $output_dest/jobs_to_start/16/$i
    timing_wrapper.sh $timing_dest/jobs_to_start/32/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --jobs_to_start 32 -o $output_dest/jobs_to_start/32/$i
    timing_wrapper.sh $timing_dest/similarity/0.94/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.94 -o $output_dest/similarity/0.94/$i
    timing_wrapper.sh $timing_dest/similarity/0.97/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.97 -o $output_dest/similarity/0.97/$i
    timing_wrapper.sh $timing_dest/similarity/0.99/$i.txt parallel_pick_otus_uclust_ref.py -r ref_file.fna -i input.fna --similarity 0.99 -o $output_dest/similarity/0.99/$i
done

# Get the benchmark results and produce the plots
mkdir $dest/plots
scaling process-bench-results -i $timing_dest/jobs_to_start -o $dest/plots/jobs_to_start
scaling process-bench-results -i $timing_dest/similarity -o $dest/plots/similarity
"""

if __name__ == '__main__':
	main()