#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import mkdir
from os.path import join, exists, isfile

from pyqi.core.exception import IncompetentDeveloperError
from pyqi.core.interfaces.optparse.output_handler import write_list_of_strings

from scaling.util import generate_poly_label
from scaling.draw import make_bench_plot, make_comparison_plot


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
    if exists(option_value):
        # Check that it is not a file, so we can use it
        if isfile(option_value):
            raise IOError("Output directory '%s' already exists and it is a "
                          "file." % option_value)
    else:
        # The output directory does not exists, create it
        mkdir(option_value)

    # Write a tab delimited file with a summary of the benchmark results
    summary_fp = join(option_value, "summarized_results.txt")
    lines = ["\t".join(["#label", "wall_mean", "wall_std", "user_mean",
                        "user_std", "kernel_mean", "kernel_std",
                        "mem_mean", "mem_std"])]
    # Loop over all the tests cases
    for i, label in enumerate(data.labels):
        lines.append("\t".join([label,
                                str(data.means.wall[i]),
                                str(data.stdevs.wall[i]),
                                str(data.means.user[i]),
                                str(data.stdevs.user[i]),
                                str(data.means.kernel[i]),
                                str(data.stdevs.kernel[i]),
                                str(data.means.mem[i]),
                                str(data.stdevs.mem[i])
                                ]))
    write_list_of_strings(result_key, lines, option_value=summary_fp)

    # Write the polynomials that fit the wall time and memory usage in
    # human-readable form
    poly_fp = join(option_value, "curves.txt")
    lines = ["Wall time fitted curve",
             generate_poly_label(data.wall_curve.poly, data.wall_curve.deg),
             "Memory usage fitted curve",
             generate_poly_label(data.mem_curve.poly, data.mem_curve.deg)]
    write_list_of_strings(result_key, lines, option_value=poly_fp)

    # Create plots with benchmark results
    # Create a plot with the time results
    time_plot_fp = join(option_value, "time_fig.png")
    ys = [data.means.wall, data.means.user, data.means.kernel]
    y_errors = [data.stdevs.wall, data.stdevs.user, data.stdevs.kernel]
    labels = ['wall', 'user', 'kernel']
    make_bench_plot(data.labels, ys, y_errors, labels, "Running time",
                    "Time (seconds)", data.wall_curve.poly,
                    data.wall_curve.deg, time_plot_fp)

    # Create a plot with the memory results
    mem_plot_fp = join(option_value, "mem_fig.png")
    y_errors = [data.stdevs.mem]
    labels = ['memory']
    make_bench_plot(data.labels, ys, y_errors, labels, "Memory usage",
                    "Memory (GB)", data.mem_curve.poly, data.mem_curve.deg,
                    mem_plot_fp, scale=1024*1024)


def write_comp_results(result_key, data, option_value=None):
    """Output handler for the bench_results_processer command

    Parameters
    ----------
    result_key : string
        The key used in the results dictionary
    data : CompData namedtuple
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
    if exists(option_value):
        # Check that it is not a file, so we can use it
        if isfile(option_value):
            raise IOError("Output directory '%s' already exists and it is a "
                          "file." % option_value)
    else:
        # The output directory does not exists, create it
        mkdir(option_value)
    # Create the plots with the benchmark comparison
    time_plot_fp = join(option_value, "time_fig.png")
    make_comparison_plot(data.x, data.time, "Running time", "Time (seconds)",
                         time_plot_fp)
    mem_plot_fp = join(option_value, "mem_fig.png")
    make_comparison_plot(data.x, data.mem, "Memory usage", "Memory (GB)",
                         mem_plot_fp, scale=1024*1024)
