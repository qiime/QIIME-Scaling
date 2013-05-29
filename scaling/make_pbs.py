#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import walk, mkdir
from os.path import abspath, join, exists, basename

PBS_HEADER = """#!/bin/bash
#PBS -q memroute
#PBS -l pvmem=512gb
#PBS -N %s
#PBS -k oe

# cd into the directory where 'qsub *.pbs' was run
cd $PBS_O_WORKDIR

# benchmarking commands:

"""

# The command template follows this structure:
# timing_wrapper.sh <out time file> <command> <var opt> <bench file> <out opt>
#   <out path>
COMMAND_TEMPLATE = """timing_wrapper.sh %s %s %s %s %s %s\n"""

def get_bench_files(input_dir):
    """Returns a list with the full path of the files in the given directory

    Inputs:
        input_dir: path to the directory where the benchmark files are located

    Note: raises a ValueError if the given directory contains any directory
    """
    bench_files = []
    for dirpath, dirnames, filenames in walk(abspath(input_dir)):
        if len(dirnames) > 0:
            raise ValueError, "The directory with the benchmark files cannot" +\
                " contain any folder."
        for f in filenames:
            bench_files.append(join(dirpath, f))

    return bench_files

def get_command_string(command, var_opt, input_fp, out_opt, index):

    return COMMAND_TEMPLATE % (time_fp, command, var_opt, bf, out_opt, out_path)

def make_pbs_file(command, var_opt, input_dir, out_opt, bench_dir, output_fp, 
    bench_name, num_reps):
    """Generate a PBS file for benchmarking a command

    Inputs:
        command: a string with the command to benchmark
        var_opt: the option of the command that will change from execution
            to execution.
        input_dir: path to the directory containing the different files to use
            as a value in the var_opt
        out_opt: the option of the command that defines the path to its
            output
        bench_dir: path to the directory where the benchmark results will be
            stored
        output_fp: path to write the output PBS file
        bench_name: name of the benchmark. It will be displayed in qstat
        num_reps: number of times each command should be executed
    """
    # Get the list of the benchmark files
    bench_files = get_bench_files(input_dir)
    # Create the benchmark folder if it doesn't exists
    if not exists(bench_dir):
        mkdir(bench_dir)
    # Create the output folder in the bench directory. It will contain the
    # output of the executed command
    base_out_dir = join(bench_dir, "command_outputs")
    mkdir(base_out_dir)
    # Create the timing folder in the bench directory. It will contain the
    # benchmark measurements of the executed command
    base_time_dir = join(bench_dir, "timing")
    mkdir(base_time_dir)
    # Write the PBS header
    outf = open(output_fp)
    outf.write(PBS_HEADER % bench_name)
    # Iterate over all the benchmark files
    for bf in bench_files:
        # Create a directory in command_outputs for the current file
        base_name = basename(bf)
        # file_base_outpath = join(base_out_dir, "")
        # for i in range(num_reps):
        #     command_string = get_command_string(command, var_opt, bf,
        #         out_opt, i)
        #     outf.write(command_string)

    outf.close()