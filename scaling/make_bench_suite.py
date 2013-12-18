#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os.path import basename, splitext

# Contains the header of the bash bench suite
BASH_HEADER = """#!/bin/bash

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
cdate=`date +_%%Y%%m%%d_%%H%%M%%S`
dest=$PWD/%s$date
mkdir $dest

# Create output directory structure
output_dest = $dest"/command_outputs"
timing_dest = $dest"/timing"

mkdir $output_dest
mkdir $timing_dest
"""

# Bash command for creating the output directories
MKDIR_OUTPUT_CMD = "mkdir $output_dest/%s\n"
MKDIR_TIMING_CMD = "mkdir $timing_dest/%s\n"

# The command template follows this structure
# timing_wrapper.sh <out time file> <command> <var opts & bench_files> <out opt> <out path>
COMMAND_TEMPLATE = """    timing_wrapper.sh $timing_dest/%s/$i.txt %s %s %s $output_dest/%s/$i"""

# The bash loop used to execute the commands as many times as provided by the user
FOR_LOOP = """# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
%s
done

# Get the benchmark results and produce the plots
"""

# Bash command to collapse the results and generate the scaling plots
GET_RESULTS = """get_benchmark_results.py -i $timing_dest/%s -o $dest/plots/%s\n"""

def get_command_string(command, base_name, opts, values, out_opt):
    """Generates the bash string to execute the benchmark command
    Inputs:
        command: string with the command to benchmark
        base_name: string with the base name of the output file (w/o extension)
        opts: list with the different options to provide to the command
        values: list of values to provide to the previous options
        out_opt: string with the option used to indicate the output path to the
            command

    Note: raises a ValueError if the number of options and the number of values
    provided does not match

    The opts list and the values list are paired in the same order, i.e. opts[0]
    with values[0], opts[1] with values[1] and so on.
    """
    if len(opts) != len(values):
        raise ValueError("The number of options and the number of values " +
            "provided must be the same")
    # Get the string with the input options and their values
    in_opts = []
    for opt, val in zip(opts, values):
        in_opts.append(opt)
        in_opts.append(val)
    options_str = " ".join(in_opts)

    return COMMAND_TEMPLATE % (base_name, command, options_str,
                                out_opt, base_name)

def make_bench_suite_files(command, in_opts, bench_files, out_opt):
    """Generates a string with the bash commands to execute the benchmark suite
    Inputs:
        command: string with the command to execute
        in_opts: list with the options used to provide the input files to the 
            command
        bench_files: list of lists with the input files for each bench case
            e.g.  [ ["option1_file1","option2_file1"],
                    ["option1_file2","option2_file2"],
                    ["option1_file3","option2_file3"] ]
        out_opt: string with the option used to indicate the output path to the
            command
    """
    # Initialize the result string list with the bash header
    # Get the base name of the command
    base_cmd = command.split(" ")[0].split(".")[0]
    result = [BASH_HEADER % base_cmd]
    # Iterate over all the benchmark files
    commands = []
    for bfs in bench_files:
        # Add the command to create the directory to store the results of the 
        # benchmark suite
        bf = bfs[0]
        base_name = splitext(basename(bf))[0]
        result.append(MKDIR_OUTPUT_CMD % base_name)
        result.append(MKDIR_TIMING_CMD % base_name)
        # Get the string of the command to be executed
        commands.append( get_command_string(command, base_name, in_opts,
                                            bfs, out_opt) )
    # Insert the command in the bash for loop and
    # append these lines to the result string
    result.append( FOR_LOOP % ("\n".join(commands)) )
    # Append to the results string the command to get the results and
    # generate the benchmark plots
    result.append(GET_RESULTS % ("",""))
    return "".join(result)

def make_bench_suite_parameters(command, parameters, out_opt):
    """Generates a string with the bash commands to execute the benchmark suite
    Inputs:
        command: string with the command to execute
        parameters: dictionary with the parameter values to test, keyed by
            parameter
            e.g.  { 'param1' : ["v1", "v2", "v3"],
                    'param2' : ["val1", "val2", "val3"]}
        out_opt: string with the option used to indicate the output path to the
            command
    """
    # Initialize the result string list with the bash header
    # Get the base name of the command
    base_cmd = command.split(" ")[0].split(".")[0]
    result = [BASH_HEADER % base_cmd]
    # Iterate over the benchmark parameters
    commands = []
    get_results_list = []
    for param in parameters:
        # Add the commands to create the directories to store the
        # results of the benchmark suite
        result.append(MKDIR_OUTPUT_CMD % param)
        result.append(MKDIR_TIMING_CMD % param)
        # Loop through all the possible values of the current parameter
        get_results_list.append(GET_RESULTS % (param, param))
        for val in parameters[param]:
            # Create a directory for storing the output commands
            # and timing results for current parameter value
            param_dir = "/".join([param, val])
            result.append(MKDIR_OUTPUT_CMD % param_dir)
            result.append(MKDIR_TIMING_CMD % param_dir)
            # Get the string of the command to be executed
            param_str = "--" + param
            commands.append( get_command_string(command, param_dir, [param_str],
                                                [val], out_opt) )
    # Insert the commands in the bash for loop and
    # append these lines to the result string
    result.append( FOR_LOOP % ("\n".join(commands)) )
    # Append the result string for each parameter to get the
    # results and generate the benchmark plots
    result.append("mkdir $dest/plots\n")
    result.extend(get_results_list)
    return "".join(result)