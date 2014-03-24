#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

import os
import numpy as np
from os.path import join
from itertools import izip

from pyqi.core.exception import IncompetentDeveloperError
from pyqi.core.interfaces.optparse.output_handler import write_list_of_strings

from scaling.util import generate_poly_label


def write_bench_results(result_key, data, option_value=None):
    """Output handler for the bench_results_processer command

    Parameters
    ----------
    result_key : string
        The key used in the results dictionary
    data : BenchData namedtuple
        The results of the command
    option_value : string
        Path to the output directory

    Raises
    ------
    IOError
        If the output directory exists and it's a file
    """
    # Check that we are not dealing with incompetent developers
    if option_value is None:
        raise IncompetentDeveloperError("Cannot write output without an "
                                        "output directory.")

    # Check that the output directory exists
    if os.path.exists(option_value):
        # Check that it is not a file, so we can use it
        if os.path.isfile(option_value):
            raise IOError("Output directory '%s' already exists and it is a "
                          "file." % option_value)
    else:
        # The output directory does not exists, create it
        os.mkdir(option_value)

    # Write a tab delimited file with a summary of the benchmark results
    summary_fp = join(option_value, "summarized_results.txt")
    lines = ["\t".join(["#label", "wall_mean", "wall_std", "user_mean",
                        "user_std", "kernel_mean", "kernel_std",
                        "mem_mean", "mem_std"])]
    # Loop over all the tests cases
    for mean, stdev in izip(data.means, data.stdevs):
        lines.append("\t".join([mean.label,
                                mean.wall,
                                stdev.wall,
                                mean.user,
                                stdev.user,
                                mean.kernel,
                                stdev.kernel,
                                mean.mem,
                                stdev.mem]))
    write_list_of_strings(result_key, lines, option_value=summary_fp)

    # Write the polynomials that fit the wall time and memory usage in
    # human-readable form
    poly_fp = join(option_value, "curves.txt")
    lines = [generate_poly_label(data.wall_curve.poly, data.wall_curve.deg),
             generate_poly_label(data.mem_curve.poly, data.mem_curve.deg)]
    write_list_of_strings(result_key, lines, option_value=poly_fp)

    # Create plots with benchmark results
    x = [mean.label for mean in means]
    # Create a plot with the time results
    time_plot_fp = join(option_value, "time_fig.png")
    ys = [[mean.wall for mean in data.means],
          [mean.user for mean in data.means],
          [mean.kernel for mean in data.means]]
    y_errors = [[stdev.wall for stdev in mean.stdevs],
                [stdev.user for stdev in mean.stdevs],
                [stdev.kernel for stdev in mean.stdevs]]

    make_bench_plot(x, ys, y_errors, "Running time", "Time (seconds)",
                    data.wall_curve.poly, data.wall_curve.deg, time_plot_fp)

    # Create a plot with the memory results
    mem_plot_fp = join(option_value, "mem_fig.png")
    yx = [[mean.mem for mean in data.means]]
    y_errors = [[stdev.mem for stdev in data.stdevs]]
    make_bench_plot(x, ys, y_errors, "Memory usage", "Memory (MB)",
                    data.mem_curve.poly, data.mem_curve.deg, mem_plot_fp,
                    scale=1024)
