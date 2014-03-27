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


class BenchResultsComparator(Command):
    """Subclassing the pyqi.core.command.Command class"""
    BriefDescription = "Compare different run results of the same bench suite"
    LongDescription = ("Takes the benchmark results of different runs of the "
                       "same benchmark suite and generates a plot with the "
                       "wall time and a plot with the memory consumption of "
                       "the different runs, allowing performance comparison "
                       "between them.")
    CommandIns = ParameterCollection([
        CommandIn(Name='bench_results', DataType=list,
                  Description='List with the benchmark results of the '
                              'different runs of the same benchmark suite',
                  Required=True),
        CommandIn(Name='labels', DataType=list,
                  Description='List of strings to label each data series of '
                              'the plot',
                  Required=True)
    ])

    CommandOuts = ParameterCollection([
        CommandOut(Name="comp_data", DataType=dict,
                   Description="")
    ])

    def run(self, **kwargs):
        bench_results = list(kwargs['bench_results'])
        labels = kwargs['labels']

        if len(bench_results) < 2:
            raise CommandError("You should provide at least two directories "
                               "with the benchmark results")
        if len(bench_results) != len(labels):
            raise CommandError("The number of results and the number of labels"
                               " should match: %s != %s" % (len(bench_results),
                                                            len(labels)))

        data = compare_benchmark_results(bench_results, labels)

        return {'comp_data': data}

CommandConstructor = BenchResultsComparator
