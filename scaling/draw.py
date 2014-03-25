#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from matplotlib import use
use('Agg', warn=False)
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import numpy as np
from itertools import izip

from scaling.util import generate_poly_label


def make_bench_plot(x, ys, y_errors, labels, title, ylabel, poly, deg,
                    output_fp, scale=1):
    """Generates a plot with the benchmark results

    Parameters
    ----------
    x : list
        The values for the x axis
    ys : list of lists
        Each element of the list a series of data to plot
    y_errors : list of lists
        Values of the errorbars for each data series
    labels : list of strings
        Data series names
    title : string
        The plot title
    ylabel : string
        The y axis label
    poly : array
        Polynomial that fits the dataseries
    deg : integer
        Degree of the polynomial
    output_fp : string
        The path to the output figure
    scale : number, optional
        Value used to scale the y values (default: 1, no scale is performed)
    """
    # Check if the x axis is numerical
    x_ticks = x
    try:
        x = np.asarray(x, dtype=np.float64)
    except ValueError:
        x = np.arange(len(x))
    # For the function resulted from curve fitting, we use an extended x axis,
    # so the trend line is more clear
    interval = x[1] - x[0]
    x2 = np.arange(x[0] - interval, x[-1] + 2*interval)
    # Generate plot
    # First plot the fitted curve
    y2 = np.polyval(poly, x2)
    # Scale the y2 value
    y2 = y2 / scale
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.plot(x2, y2, 'k', label=generate_poly_label(poly, deg))
    # Plot the benchmark data
    for label, y, y_err in izip(labels, ys, y_errors):
        y = np.array(y) / scale
        y_err = np.array(y_err) / scale
        ax.errorbar(x, y, yerr=y_err, label=label)
    figure.suptitle(title)
    ax.set_xlabel("Input file")
    ax.set_ylabel(ylabel)
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(loc='best', prop=fontP, fancybox=True).get_frame().set_alpha(0.2)
    ax.set_xticks(x)
    ax.set_xticklabels(x_ticks)
    figure.savefig(output_fp)


def make_comparison_plot(x, data, title, ylabel, output_fp, scale=1):
    """Generates a plot for performance comparison

    Parameters
    ----------
    x : list
        The values for the x axis
    data : dict
        Dict of {label : tuple(list means, list stdevs)} in which each data
        series to be plotted is keyed by its label
    title : string
        Plot title
    ylabel : string
        The y axis label
    output_fp : string
        The path to the output figure
    scale : number, optional
        Value used to scale the y values (default: 1, no scale is performed)
    """
    # Check if the x axis is numerical
    x_ticks = x
    try:
        x = np.asarray(x, dtype=np.float64)
    except ValueError:
        x = np.arange(len(x))
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for label, values in data.iteritems():
        y = np.array(values[0]) / scale
        y_err = np.array(values[1]) / scale
        ax.errorbar(x, y, yerr=y_err, label=label)
    figure.suptitle(title)
    ax.set_xlabel('Input file')
    ax.set_ylabel(ylabel)
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(loc='best', prop=fontP, fancybox=True).get_frame().set_alpha(0.2)
    ax.set_xticks(x)
    ax.set_xticklabels(x_ticks)
    figure.savefig(output_fp)
