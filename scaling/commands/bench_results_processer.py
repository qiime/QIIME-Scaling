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
from matplotlib.figure import Figure
from scaling.process_results import process_benchmark_results
from scaling.cluster_util import wait_on


class BenchResultsProcesser(Command):
    BriefDescription = "Processes the benchmark suite results"
    LongDescription = ("Takes the benchmark suite output directory and "
                       "processes the benchmark measurements, creating plots "
                       "and collapsing results in a usable form.")
    CommandIns = ParameterCollection([
        CommandIn(Name='input_dir', DataType=str,
                  Description='Path to the directory with the time results',
                  Required=True),
        CommandIn(Name='job_ids', DataType=list,
                  Description='List of job ids to wait for if running in a '
                  'pbs cluster', Required=False, Default=[])
    ])

    CommandOuts = ParameterCollection([
        CommandOut(Name="bench_data", DataType=dict,
                   Description="Dictionary with the benchmark results"),
        CommandOut(Name="time_fig", DataType=Figure,
                   Description="Figure with the execution time results"),
        CommandOut(Name="time_str", DataType=str,
                   Description="String with the best polynomial fit to the "
                   "benchmark execution time results"),
        CommandOut(Name="mem_fig", DataType=Figure,
                   Description="Figure with the memory consumption results"),
        CommandOut(Name="mem_str", DataType=str,
                   Description="String with the best polynomial fit to the "
                   "benchmark memory consumption results")
    ])

    def run(self, **kwargs):
        result = {}

        input_dir = kwargs['input_dir']
        job_ids = kwargs['job_ids']

        wait_on(job_ids)

        data, time_fig, time_str, mem_fig, mem_str = \
            process_benchmark_results(input_dir)

        result['bench_data'] = data
        result['time_fig'] = time_fig
        result['time_str'] = time_str
        result['mem_fig'] = mem_fig
        result['mem_str'] = mem_str

        return result

CommandConstructor = BenchResultsProcesser
