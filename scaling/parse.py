#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from collections import namedtuple


def parse_parameters_file(lines):
    """Parses the parameters file encoded in lines and returns it as a dict

    Inputs:
        lines: open file object

    The format of the parameter file is:
        param_name <tab> value1,value2,...

    The output dictionary is keyed by parameter name and values are lists with
        the parameter values to test
    """
    param_dict = {}
    for line in lines:
        line = line.strip()
        if line:
            (param, values) = line.split('\t')
            param_dict[param] = values.split(',')
    return param_dict


def parse_summarized_results(lines):
    """Parses the summarized results file

    Parameters
    ----------
    lines : iterable
        The contents of the summarize results file
    """
    BenchSummary = namedtuple('BenchSummary', ('label', 'wall_mean',
                                               'wall_stdev', 'user_mean',
                                               'user_stdev', 'kernel_mean',
                                               'kernel_stdev', 'mem_mean',
                                               'mem_stdev'))
    result = BenchSummary([], [], [], [], [], [], [], [], [])
    # Begin iterating over lines
    for line in lines:
        if not line or line.startswith('#'):
            continue
        line = line.strip()
        values = line.split('\t')
        result.label.append(values[0])
        result.wall_mean.append(float(values[1]))
        result.wall_stdev.append(float(values[2]))
        result.user_mean.append(float(values[3]))
        result.user_stdev.append(float(values[4]))
        result.kernel_mean.append(float(values[5]))
        result.kernel_stdev.append(float(values[6]))
        result.mem_mean.append(float(values[7]))
        result.mem_stdev.append(float(values[8]))
    return result
