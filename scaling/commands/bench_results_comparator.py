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
from scaling.process_results import compare_benchmark_results
from matplotlib.figure import Figure


class BenchResultsComparator(Command):
    BriefDescription = "Compare different runs results of the same bench suite"
    LongDescription = ("Takes a list with paths to directories with benchmark "
                       "results and generates a plot with the wall time and a "
                       "plot with the memory consumption of the different "
                       "runs, allowing performance comparison between them.")
    CommandIns = ParameterCollection([
        CommandIn(Name='input_dirs', DataType=list,
                  Description='List with the path to the directories with the '
                  'time results of different runs of the same bench suite',
                  Required=True),
        CommandIn(Name='labels', DataType=list,
                  Description='List of strings to label each data series of '
                  'the plot', Required=True)
    ])

    CommandOuts = ParameterCollection([
        CommandOut(Name="time_fig", DataType=Figure,
                   Description="matplotlib figure with the wall time plot"),
        CommandOut(Name="mem_fig", DataType=Figure,
                   Description="matplotlib figure with the memory consumption "
                               "plot"),
    ])

    def run(self, **kwargs):
        result = {}

        input_dirs = kwargs['input_dirs']
        labels = kwargs['labels']

        if len(input_dirs) < 2:
            raise CommandError("You should provide at least two directories "
                               "with the benchmark results")

        time_fig, mem_fig = compare_benchmark_results(input_dirs, labels)

        result['time_fig'] = time_fig
        result['mem_fig'] = mem_fig

        return result

CommandConstructor = BenchResultsComparator
