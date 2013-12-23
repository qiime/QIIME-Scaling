#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from pyqi.core.exception import IncompetentDeveloperError
from pyqi.core.interfaces.optparse.output_handler import (write_list_of_strings,
                                                          write_string)
import os

def write_summarized_results(result_key, data, option_value=None):
    """Write the benchmark results in a tab-delimited format

    option_value is the base output directory

    Writes a file with the benchmark results in a tab-delimited form,
    with the following headers: label, wall_mean, wall_std, user_mean, user_std,
    kernel_mean, kernel_std, mem_mean, mem_std
    Each row contains the results for a single experiment
    """

    if option_value is None:
        raise IncompetentDeveloperError("Cannot write output without an "
                                        "output directory.")

    output_fp = os.path.join(option_value, "%s.txt" % result_key)

    lines = []
    headers = ["#label", "wall_mean", "wall_std", "user_mean", "user_std",
        "kernel_mean", "kernel_std", "mem_mean", "mem_std"]
    lines.append("\t".join(headers))
    # Loop over all the experiments
    for i, label in enumerate(data['label']):
        values = [str(label)]
        values.append(str(data['wall_time'][0][i]))
        values.append(str(data['wall_time'][1][i]))
        values.append(str(data['cpu_user'][0][i]))
        values.append(str(data['cpu_user'][1][i]))
        values.append(str(data['cpu_kernel'][0][i]))
        values.append(str(data['cpu_kernel'][1][i]))
        values.append(str(data['memory'][0][i]))
        values.append(str(data['memory'][1][i]))
        lines.append("\t".join(values))
    
    write_list_of_strings(result_key, lines, option_value=output_fp)

def write_matplotlib_figure(result_key, data, option_value=None):
    """Write a matplotlib figure to disk

    option_value is the base output directory
    """
    if option_value is None:
        raise IncompetentDeveloperError("Cannot write output without an "
                                        "output directory.")

    if os.path.exists(option_value) and os.path.isfile(option_value):
        raise IOError("Output directory '%s' already exists and it is a file."
                      % option_value)

    output_fp = os.path.join(option_value, "%s.png" % result_key)
    if os.path.exists(output_fp):
        raise IOError("Output path %s already exists." % output_fp)

    data.savefig(output_fp)

def write_string_to_dir(result_key, data, option_value=None):
    """Write a string to a file

    option_value is the base output directory
    """
    if option_value is None:
        raise IncompetentDeveloperError("Cannot write output without an "
                                        "output directory.")

    if os.path.exists(option_value) and os.path.isfile(option_value):
        raise IOError("Output directory '%s' already exists and it is a file."
                      % option_value)

    output_fp = os.path.join(option_value, "%s.txt" % result_key)
    write_string(result_key, data, option_value=output_fp)