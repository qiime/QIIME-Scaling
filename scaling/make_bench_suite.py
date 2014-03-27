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
dest=$PWD/%s$cdate
mkdir $dest

# Create output directory structure
output_dest=$dest"/command_outputs"
timing_dest=$dest"/timing"

mkdir $output_dest
mkdir $timing_dest
"""

# Bash command for creating the output directories
MKDIR_OUTPUT_CMD = "mkdir $output_dest/%s\n"
MKDIR_TIMING_CMD = "mkdir $timing_dest/%s\n"

# The command template follows this structure
# timing_wrapper.sh <out time file> <command> <var opts & bench_files>
#    <out opt> <out path>
COMMAND_TEMPLATE = ("    timing_wrapper.sh $timing_dest/%s/$i.txt %s %s %s "
                    "$output_dest/%s/$i")

# The PBS template follows this structure - blah=${blah#?}
# <job id var>+=";"`echo "cd $PWD; <command>" | qsub -k oe -N <job_name>
#   -q <queue> <extra args>`
PBS_CMD_TEMPLATE = ("    %s+=\",\"`echo \"cd $PWD; %s\" | qsub -k oe"
                    " -N %s%d -q %s %s`")

# The bash loop used to execute the commands as many times as
# provided by the user
FOR_LOOP = """# Loop as many times as desired
for i in `seq $num_rep`
do
    # benchmarking commands:
%s
done

# Get the benchmark results and produce the plots
"""

# Bash command to collapse the results and generate the scaling plots
GET_RESULTS = ("scaling process-bench-results -i $timing_dest/%s -o "
               "$dest/plots/%s %s\n")


def get_command_string(command, base_name, opts, values, out_opt):
    """Generates the bash string with the benchmark command

    The opts list and the values list are paired in the same order, i.e.
    opts[0] with values[0], opts[1] with values[1] and so on.

    Parameters
    ----------
    command: string
        The base command to benchmark
    base_name: string
        The base name of the output file (w/o extension)
    opts: list
        The different options to provide to the command
    values: list
        The values to provide to the options
    out_opt: string
        The option used to indicate the output path to the command

    Raises
    ------
    ValueError
        if the number of options and the number of values provided does not
        match
    """
    if len(opts) != len(values):
        raise ValueError("The number of options and the number of values "
                         "provided must be the same")
    # Get the string with the input options and their values
    in_opts = []
    for opt, val in zip(opts, values):
        in_opts.append(opt)
        in_opts.append(val)
    options_str = " ".join(in_opts)

    return COMMAND_TEMPLATE % (base_name, command, options_str,
                               out_opt, base_name)


def make_bench_suite_files(command, in_opts, bench_files, out_opt, pbs=False,
                           job_prefix="bench_", queue="", pbs_extra_args=""):
    """Generates a string with the bash commands to execute the benchmark suite

    Parameters
    ----------
    command: string
        The base command to execute
    in_opts: list with the options used to provide the input files to the
        command
    bench_files: list of lists
        The input files for each bench case
        e.g.  [ ["option1_file1","option2_file1"],
                ["option1_file2","option2_file2"],
                ["option1_file3","option2_file3"] ]
    out_opt: string
        Option used to indicate the output path to the command
    pbs: bool
        Ture if the benchmark suite will run in a PBS cluster environment
    job_prefix: string
        Prefix for the job name in case of a PBS cluster environment
    queue: string
        PBS queue to submit jobs
    pbs_extra_args: string
        Any extra arguments needed to qsub
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
        commands.append(get_command_string(command, base_name, in_opts,
                                           bfs, out_opt))
    if pbs:
        # We are creating a benchmark suite in a cluster environment
        # Clean up the scaling_jobs variable
        result.append("scaling_jobs=\"\"\n")
        # Add the qsub command for each job
        commands = [PBS_CMD_TEMPLATE % ("scaling_jobs", cmd, job_prefix, i,
                    queue, pbs_extra_args) for i, cmd in enumerate(commands)]
    # Insert the command in the bash for loop and
    # append these lines to the result string
    result.append(FOR_LOOP % ("\n".join(commands)))
    if pbs:
        # We need to remove the first ";" character of scaling_jobs
        result.append("scaling_jobs=${scaling_jobs#?}\n")
        # Append to the results string the command to get the results and
        # generate the benchmark plots
        result.append(GET_RESULTS % ("", "", "-w $scaling_jobs"))
    else:
        # Append to the results string the command to get the results and
        # generate the benchmark plots
        result.append(GET_RESULTS % ("", "", ""))
    return "".join(result)


def make_bench_suite_parameters(command, parameters, out_opt, pbs=False,
                                job_prefix="bench_", queue="",
                                pbs_extra_args=""):
    """Generates a string with the bash commands to execute the benchmark suite

    Parameters
    ----------
    command: string
        The command to execute
    parameters: dict of {string: list of strings}
        The parameter values to test, keyed by parameter
        e.g.  { 'param1' : ["v1", "v2", "v3"],
                'param2' : ["val1", "val2", "val3"]}
    out_opt: string
        The option used to indicate the output path to the command
    pbs: bool
        True if the benchmark suite will run in a PBS cluster environment
    job_prefix: string
        Prefix for the job name in case of a PBS cluster environment
    queue: string
        PBS queue to submit jobs
    pbs_extra_args: string
        Any extra arguments needed to qsub
    """
    # Initialize the result string list with the bash header
    # Get the base name of the command
    base_cmd = command.split(" ")[0].split(".")[0]
    result = [BASH_HEADER % base_cmd]
    # Iterate over the parameters to benchmark
    commands = []
    get_results_list = []
    # These two variables are used in case of a pbs env
    count = 0
    var_jobs = []
    for param in parameters:
        # Add the commands to create the directories to store the
        # results of the benchmark suite
        result.append(MKDIR_OUTPUT_CMD % param)
        result.append(MKDIR_TIMING_CMD % param)
        # Loop through all the possible values of the current parameter
        param_cmds = []
        for val in parameters[param]:
            # Create a directory for storing the output commands
            # and timing results for current parameter value
            param_dir = "/".join([param, val])
            result.append(MKDIR_OUTPUT_CMD % param_dir)
            result.append(MKDIR_TIMING_CMD % param_dir)
            # Get the string of the command to be executed
            param_str = "--" + param
            param_cmds.append(get_command_string(command, param_dir,
                                                 [param_str], [val], out_opt))
        # Check if we are crating the command for a cluster environment
        if pbs:
            var_job = "%s_jobs" % param
            var_jobs.append(var_job)
            param_cmds = [PBS_CMD_TEMPLATE % (var_job, cmd, job_prefix,
                          count + i, queue, pbs_extra_args) for i, cmd in
                          enumerate(param_cmds)]
            count += len(param_cmds)
            # Create the process results command
            get_results_list.append(GET_RESULTS % (param, param,
                                                   "-w $%s" % var_job))
        else:
            # Create the process results command
            get_results_list.append(GET_RESULTS % (param, param, ""))
        # Extend the commands list with the param commands
        commands.extend(param_cmds)
    # Clean up bash variables
    # Note that if we are not in a pbs command, var_jobs is empty
    for var_job in var_jobs:
        result.append("%s=\"\"\n" % var_job)
    # Insert the commands in the bash for loop and
    # append these lines to the result string
    result.append(FOR_LOOP % ("\n".join(commands)))
    # Append the result string for each parameter to get the
    # results and generate the benchmark plots
    result.append("mkdir $dest/plots\n")
    # Remove the first ";" character of the bash variables
    # Note that if we are not in a pbs command, var_jobs is empty
    for var_job in var_jobs:
        result.append("%s=${%s#?}\n" % (var_job, var_job))
    result.extend(get_results_list)
    return "".join(result)
