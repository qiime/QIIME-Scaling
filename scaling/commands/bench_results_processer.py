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

from scaling.process_results import (process_benchmark_results, CompData)
from scaling.cluster_util import wait_on


class BenchResultsProcesser(Command):
    BriefDescription = "Processes the benchmark suite results"
    LongDescription = ("Takes the benchmark suite output directory and "
                       "processes the benchmark measurements, creating plots "
                       "and collapsing results in a usable form.")
    CommandIns = ParameterCollection([
        CommandIn(Name='bench_results', DataType=list,
                  Description='List with the benchmark results',
                  Required=True),
        CommandIn(Name='job_ids', DataType=list,
                  Description='List of job ids to wait for if running in a '
                  'pbs cluster', Required=False)
    ])

    CommandOuts = ParameterCollection([
        CommandOut(Name="bench_data", DataType=CompData,
                   Description="Dictionary with the benchmark results"),
    ])

    def run(self, **kwargs):
        result = {}

        bench_results = kwargs['bench_results']
        job_ids = kwargs['job_ids']

        if job_ids:
            wait_on(job_ids)

        data = process_benchmark_results(bench_results)

        result['bench_data'] = data

        return result

CommandConstructor = BenchResultsProcesser
