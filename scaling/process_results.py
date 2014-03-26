#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from itertools import izip
import numpy as np

from scaling.util import SummarizedResults, BenchData, FittedCurve, CompData


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
    # Get all the benchmark data in a single structure
    # with mean and standard deviation values
    labels = []
    result_means = BenchData([], [], [], [])
    result_stdev = BenchData([], [], [], [])
    for case in case_results:
        labels.append(case.label)

        result_means.wall.append(np.mean(case.wall))
        result_means.user.append(np.mean(case.user))
        result_means.kernel.append(np.mean(case.kernel))
        result_means.mem.append(np.mean(case.mem))

        result_stdev.wall.append(np.std(case.wall))
        result_stdev.user.append(np.std(case.user))
        result_stdev.kernel.append(np.std(case.kernel))
        result_stdev.mem.append(np.std(case.mem))

    # Check if the labels is numerical
    try:
        x = np.asarray(labels, dtype=np.float64)
    except ValueError:
        x = np.arange(len(labels))
    # Get the polynomial that fits the wall time
    wall_poly, wall_deg = curve_fitting(x, result_means.wall)
    wall_curve = FittedCurve(wall_poly, wall_deg)
    # Get the polynomial that fits the memory usage
    mem_poly, mem_deg = curve_fitting(x, result_means.mem)
    mem_curve = FittedCurve(mem_poly, mem_deg)

    result = SummarizedResults(labels, result_means, result_stdev, wall_curve,
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
    comp_data = CompData(results[0].label, {}, {})
    for label, res in izip(labels, results):
        if set(comp_data.x) != set(res.label):
            raise ValueError("In order to compare different benchmark "
                             "results, they should be over the same set of"
                             " test cases: %s != %s" % (comp_data.x, label))
        comp_data.time[label] = (res.wall_mean, res.wall_stdev)
        comp_data.mem[label] = (res.mem_mean, res.mem_stdev)
    return comp_data
