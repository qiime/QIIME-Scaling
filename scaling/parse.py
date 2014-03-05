#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"


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
