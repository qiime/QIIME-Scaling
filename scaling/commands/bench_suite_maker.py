#!/usr/bin/env python
from __future__ import division

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from pyqi.core.command import (Command, CommandIn, CommandOut,
                               ParameterCollection)
from pyqi.core.exception import CommandError
from scaling.make_bench_suite import (make_bench_suite_files,
                                      make_bench_suite_parameters)


class BenchSuiteMaker(Command):
    BriefDescription = "Generates a benchmark suite file"
    LongDescription = ("Given a command and a list of benchmarks files or a "
                       "dictionary with the options to test, %prog generates a"
                       " shell script that executes a complete benchmark "
                       "suite.")
    CommandIns = ParameterCollection([
        CommandIn(Name='command', DataType=str,
                  Description='command to benchmark', Required=True),
        CommandIn(Name='parameters', DataType=dict,
                  Description='dictionary where the keys are the parameters '
                  'to test and the values are a list of values for such '
                  'parameter.',
                  DefaultDescription='No parameters used', Default=None),
        CommandIn(Name='bench_files', DataType=list,
                  Description='List of lists of paths to the benchmark files '
                  'to use as input for the command. Each inner list is a test '
                  'case and should have the same length as the in_opts '
                  'parameter.',
                  DefaultDescription='No bench_files used',
                  Required=False, Default=None),
        CommandIn(Name='in_opts', DataType=list,
                  Description='list of options used for providing the '
                  'benchmark files to the command. It should have the same '
                  'length and order than the inner lists of bench_files.',
                  DefaultDescription='["-i"] is used as a default',
                  Required=False, Default=["-i"]),
        CommandIn(Name='out_opt', DataType=str,
                  Description='Option used for providing the output path to '
                  'the command to benchmark.',
                  DefaultDescription='"-o" is used as default',
                  Required=False, Default="-o"),
        CommandIn(Name='pbs', DataType=bool,
                  Description='Flag to determine if the benchmark suite will '
                  'run in a PBS cluster environment',
                  DefaultDescription='False: run serially in bash',
                  Required=False, Default=False),
        CommandIn(Name='job_prefix', DataType=str,
                  Description='Prefix for the job name in case of a PBS '
                  'cluster environment',
                  DefaultDescription='"bench_" is used as a default prefix',
                  Required=False, Default="bench_"),
        CommandIn(Name='queue', DataType=str,
                  Description='PBS queue to submit jobs',
                  DefaultDescription='"" is used as default, which will submit'
                  ' the jobs to the system default queue',
                  Required=False, Default=""),
        CommandIn(Name='pbs_extra_args', DataType=str,
                  Description='Any extra arguments needed to qsub',
                  DefaultDescription='No extra arguments are used',
                  Required=False, Default="")
    ])
    CommandOuts = ParameterCollection([
        CommandOut(Name='bench_suite', DataType=str,
                   Description='String with the benchmark suite')])

    def run(self, **kwargs):
        result = {}

        # Get command parameters
        command = kwargs['command']
        out_opt = kwargs['out_opt']
        parameters = kwargs['parameters']
        bench_files = kwargs['bench_files']
        in_opts = kwargs['in_opts']
        pbs = kwargs['pbs']
        job_prefix = kwargs['job_prefix']
        queue = kwargs['queue']
        pbs_extra_args = kwargs['pbs_extra_args']

        # Check which type of bench suite are we generating
        if parameters:
            # We are generating a benchmark suite based on different parameter
            # values. In such case, the user should not provide any bench file
            if bench_files:
                raise CommandError("Parameters or bench_files should be "
                                   "provided, but not both.")
            bench_str = make_bench_suite_parameters(command, parameters,
                                                    out_opt, pbs, job_prefix,
                                                    queue, pbs_extra_args)
        elif bench_files:
            # We are generating a benchmark suite based on input files,
            # Check that the number of benchmark files for test case match
            # the number of options to provide the input files
            if not all(len(x) == len(in_opts) for x in bench_files):
                raise CommandError("The length of bench_files and in_opts "
                                   "must be the same.")
            bench_str = make_bench_suite_files(command, in_opts, bench_files,
                                               out_opt, pbs, job_prefix, queue,
                                               pbs_extra_args)
        else:
            # Not enough parameters!
            raise CommandError("Must specify parameters or bench_files.")

        result['bench_suite'] = bench_str

        return result

CommandConstructor = BenchSuiteMaker
