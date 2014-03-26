#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from scaling.util import BenchSummary


def parse_parameters_file(lines):
    """Parses the parameters file encoded in lines and returns it as a dict

    The format of the parameter file is:
        param_name_1 <tab> value1,value2,...
        param_name_2 <tab> value1,value2,...

    Parameters
    ----------
    lines: iterable
        The contents of the parameters file

    Returns
    -------
    dict of {string: list}
        Keys are the name of the parameters and list the values for such
        parameter
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
