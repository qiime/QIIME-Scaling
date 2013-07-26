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
from os.path import abspath, join, exists, basename, splitext

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
# timing_wrapper.sh <out time file> <command> <var opts & bench files> <out opt>
# <out path>
COMMAND_TEMPLATE = """timing_wrapper.sh %s %s %s %s %s\n"""

def get_bench_files(input_dirs):
    """Returns a list with the full path of the files in the given directory

    Inputs:
        input_dir: path to the directory where the benchmark files are located

    Note: raises a ValueError if input_dir contains any directory
    """
    bench_files_by_dir = []
    for input_dir in input_dirs:
        dir_files = []
        for dirpath, dirnames, filenames in walk(abspath(input_dir)):
            if len(dirnames) > 0:
                raise ValueError, "The directory with the benchmark files " +\
                    "cannot contain any folder: %s" % dirpath
            for f in filenames:
                dir_files.append(join(dirpath, f))
        dir_files = sorted(dir_files)
        bench_files_by_dir.append(dir_files)

    bench_files = []
    for i in range(len(bench_files_by_dir[0])):
        bench_files.append([dir_files[i] for dir_files in bench_files_by_dir])

    return bench_files

def get_bench_params(parameters_fp):
    """Returs a dict with the parameters to test and its values

    Inputs:
        parameters_fp: path to the file containing the parameters to benchmark
    """
    param_f = open(parameters_fp, 'U')
    param_dict = {}
    for line in param_f:
        line = line.strip()
        if line:
            (param, values) = line.split('\t')
            param_dict[param] = values.split(',')
    param_f.close()

    return param_dict

def get_command_string(command, var_opts, var_values, out_opt, output_dir,
    time_dir, index):
    """Returns a string with the command to execute

    Inputs:
        command: command to benchmark
        var_opts: list of options of the command used to provide the benchmark
            files (same length as var_values)
        var_values: list with the benchamrk values for the options (same length
            as var_opts)
        out_opt: the option of the command used to provide the output path
        output_dir: path to the directory which will contain the command output
        time_dir: path to the directory which will contain the benchmark results
        index: iteration number for the current command

    Note: Raises ValueError if var_opts and var_values don't have the same length
    """
    if len(var_opts) != len(var_values):
        raise ValueError, "The number of input options and the number of " +\
            "benchmark files should be the same"

    out_path = join(output_dir, str(index))
    time_fp = join(time_dir, str(index) + '.txt')
    input_files_str = ""
    for opt, fp in zip(var_opts, var_values):
        input_files_str = " ".join([input_files_str, opt, fp])

    command_str = COMMAND_TEMPLATE % (time_fp, command, input_files_str,
        out_opt, out_path)

    return command_str.replace("\"", "")

def write_commands_files(command, var_opts, input_dirs, out_opt, base_out_dir,
    base_time_dir, pbsf, num_reps):
    """Writes the commands in a PBS file for benchmarking a command using a set
        of bench files

    Inputs:
        command: a string with the command to benchmark
        var_opts: list of options of the command used to provide the benchmark
            files
        input_dirs: list of paths to the directories containing the different
            benchmark files to use as a value for each option in var_opts
        out_opt: the option of the command that defines the path to its
            output
        base_out_dir: base file where to store the output of the command
        base_time_dir: base file where to store the benchmark measurements
        pbsf: the PBS file handler
        num_reps: number of times each command should be executed
    """
    # Get the list of the benchmark files
    bench_files = get_bench_files(input_dirs)

    # Iterate over all the benchmark files
    for bfs in bench_files:
        # Create a directory in command_outputs for the current files
        bf = bfs[0]
        base_name = splitext(basename(bf))[0]
        file_base_outpath = join(base_out_dir, base_name)
        if not exists(file_base_outpath):
            mkdir(file_base_outpath)

        # Create a directory in timing for the current file
        file_base_timepath = join(base_time_dir, base_name)
        if not exists(file_base_timepath):
            mkdir(file_base_timepath)

        # Create the command as many times as it should be executed
        for i in range(num_reps):
            command_string = get_command_string(command, var_opts, bfs, out_opt,
                file_base_outpath, file_base_timepath, i)
            pbsf.write(command_string)

def write_commands_parameters(command, parameters_fp, out_opt, base_out_dir,
    base_time_dir, pbsf, num_reps):
    """Writes the commands in a PBS file for benchmarking a command using a set
        of parameter values

    Inputs:
        command: a string with the command to benchmark
        parameters_fp: path to the file containing the parameters to benchmark
        out_opt: the option of the command that defines the path to its
            output
        base_out_dir: base file where to store the output of the command
        base_time_dir: base file where to store the benchmark measurements
        pbsf: the PBS file handler
        num_reps: number of times each command should be executed
    """
    # Get the list of parameters to benchmark
    bench_params = get_bench_params(parameters_fp)
    # Iterate over all the benchmark parameters
    for bp in bench_params:
        # Create a directory in command_outputs for the current parameter
        param_base_dirpath = join(base_out_dir, bp)
        if not exists(param_base_dirpath):
            mkdir(param_base_dirpath)
        # Create a directort in timing for the current parameter
        param_base_timedir = join(base_time_dir, bp)
        if not exists(param_base_timedir):
            mkdir(param_base_timedir)
        # Loop through all the possible values of the current parameter
        for val in bench_params[bp]:
            # Create a directory in the base output for the curernt value
            outdir = join(param_base_dirpath, val)
            if not exists(outdir):
                mkdir(outdir)
            # Create a directory in the base timing for the current value
            timedir = join(param_base_timedir, val)
            if not exists(timedir):
                mkdir(timedir)
            # Create the command as many times as it should be executed
            for i in range(num_reps):
                command_string = get_command_string(command, ['--' + bp],
                    [val], out_opt, outdir, timedir, i)
                pbsf.write(command_string)

def make_pbs(command, var_opts, input_dirs, parameters_fp, out_opt, bench_dir,
    pbs_fp, bench_name, num_reps):
    """Generate a PBS file for benchmarking a command

    Inputs:
        command: a string with the command to benchmark
        var_opts: list of options of the command used to provide the benchmark
            files
        input_dirs: list of paths to the directories containing the different
            benchmark files to use as a value for each option in var_opts
        parameters_fp: path to the file containing the parameters to benchmark
        out_opt: the option of the command that defines the path to its
            output
        bench_dir: path to the directory where the benchmark results will be
            stored
        pbs_fp: path to write the output PBS file
        bench_name: name of the benchmark. It will be displayed in qstat
        num_reps: number of times each command should be executed
    """
    # Create the output folder in the bench directory. It will contain the
    # output of the executed commands
    base_out_dir = join(bench_dir, "command_outputs")
    if not exists(base_out_dir):
        mkdir(base_out_dir)

    # Create the timing folder in the bench directory. It will contain the
    # benchmark measurements of the executed commands
    base_time_dir = join(bench_dir, "timing")
    if not exists(base_time_dir):
        mkdir(base_time_dir)

    # Write PBS file header
    outf = open(pbs_fp, 'w')
    outf.write(PBS_HEADER % bench_name)

    # Write commands to PBS file
    if parameters_fp:
        write_commands_parameters(command, parameters_fp, out_opt, base_out_dir,
            base_time_dir, outf, num_reps)
    else:
        write_commands_files(command, var_opts, input_dirs, out_opt,
            base_out_dir, base_time_dir, outf, num_reps)

    # Close PBS file
    outf.close()