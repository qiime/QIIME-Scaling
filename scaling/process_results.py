#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import listdir
from os.path import join, isdir

from collections import namedtuple
from itertools import izip
import numpy as np

from scaling.util import natural_sort


def compute_rsquare(y, SSerr):
    """Computes the Rsquare value using the points y and the Sum of Squares

    Input:
        y: numpy array
        SSerr: numpy array with 1 float

    Computes Rsquare using the following formula:
                            SSerr
            Rsquare = 1 - ---------
                            SStot

    Where SSerr is the sum of squares due to error and SStot is the sum of
    squares about the mean, computed as:

            SStot = sum( (y-mean)^2 )
    """
    mean = np.mean(y)
    SStot = np.sum((y-mean)**2)
    rsquare = 1 - (SSerr/SStot)

    return rsquare


def curve_fitting(x, y):
    """Fits a polynomial curve to the data points defined by the arrays x and y

    Input:
        x: numpy array of floats
        y: numpy array of floats

    Returns the polynomial curve with less degree that fits the data points
        with an Rsquare over 0.999; and its degree.
    """
    deg = 0
    rsquare = 0
    while rsquare < 0.999:
        deg += 1
        poly, SSerr, rank, sin, rc = np.polyfit(x, y, deg, full=True)
        if len(SSerr) == 0:
            break
        rsquare = compute_rsquare(y, SSerr)

    return poly, deg


def process_benchmark_results(case_results):
    """Processes the benchmark results stored in input_dir

    Parameters
    ----------
    case_results : Iterable
        BenchCase namedtuples with the results of each benchmark case

    Returns
    -------
    SummarizedResults
        namedtuple with the benchmark suite results
    """
    BenchData = namedtuple('BenchData', ('label', 'wall', 'user', 'kernel',
                                         'mem'))
    # Get all the benchmark data in a single structure
    # with mean and standard deviation values
    result_means = BenchData([], [], [], [], [])
    result_stdev = BenchData([], [], [], [], [])
    for case in case_results:
        result_means.label.append(case.label)
        result_means.wall.append(np.mean(case.wall))
        result_means.user.append(np.mean(case.user))
        result_means.kernel.append(np.mean(case.kernel))
        result_means.mem.append(np.mean(case.mem))

        result_stdev.label.append(case.label)
        result_stdev.wall.append(np.std(case.wall))
        result_stdev.user.append(np.std(case.user))
        result_stdev.kernel.append(np.std(case.kernel))
        result_stdev.mem.append(np.std(case.mem))

    FittedCurve = namedtuple('FittedCurve', ('poly', 'deg'))
    # Get the polynomial that fits the wall time
    wall_poly, wall_deg = curve_fitting(result_means.label, result_means.wall)
    wall_curve = FittedCurve(wall_poly, wall_deg)
    # Get the polynomial that fits the memory usage
    mem_poly, mem_deg = curve_fitting(result_means.label, result_means.mem)
    mem_curve = FittedCurve(mem_poly, mem_deg)

    SummarizedResults = namedtuple('SummarizedResults', ('means', 'stdevs',
                                   'wall_curve', 'mem_curve'))
    result = SummarizedResults(result_means, result_stdev, wall_curve,
                               mem_curve)
    return result


def compare_benchmark_results(results, labels):
    """
    Parameters
    ----------
    results : Iterable
        The results for each execution of the bench suite

    labels : Iterable
        The label for each data series
    """
    x_axis = None
    comp_data = {}
    for label, res in izip(labels, results):
        if not x_axis:
            x_axis = res.label
        else:
            if set(x_axis) != set(res.label):
                raise ValueError("In order to compare different benchmark "
                                 "results, they should be over the same set of"
                                 " test cases")
        data[label] = res.mean
    return x_axis, data


def compare_benchmark_results(bench_results, labels):
    """Compares in a single plot the benchmark results listed in input_dirs

    Parameters
    ----------
    bench_results : Iterable
        The results of the different runs of the same benchmark suite

    labels : Iterable
        The label of each data series

    Note: raises a ValueError if all the benchmark results doesn't belong to
        the same bench suite
    """
    # Get the benchmark results
    data = {}
    for in_dir, label in zip(input_dirs, labels):
        d = process_timing_directory(in_dir)
        data[label] = d
    # Check that all the provided results correspond to the same bench suite
    x_axis = None
    for l, d in data.iteritems():
        if x_axis is None:
            x_axis = d['label']
        else:
            if set(x_axis) != set(d['label']):
                raise ValueError("In order to compare different benchmark "
                                 "results, they should be over the same set of"
                                 " test cases")
    # Generate comparison plots
    time_fig = make_comparison_plot(data, x_axis, 'wall_time', 'Running time',
                                    'Time (seconds)')
    mem_fig = make_comparison_plot(data, x_axis, 'memory', 'Memory usage',
                                   'Memory (GB)', scale=1024*1024)
    return time_fig, mem_fig


def make_comparison_plot(data, x_axis, key, title, ylabel, scale=1):
    """Creates a matplotlib figure with the benchmark results of multiple runs

    Input:
        data: dictionary with the benchmark results
        x_axis: array to use as X axis values
        key: key of data to plot in the figure
        scale: value to use as a scaling factor for the values in data
    """
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for d in data:
        y, y_err = data[d][key]
        y = np.array(y) / scale
        y_err = np.array(y_err) / scale
        ax.errorbar(x_axis, y, yerr=y_err, label=d)
    figure.suptitle(title)
    ax.set_xlabel('Input file')
    ax.set_ylabel(ylabel)
    return figure
