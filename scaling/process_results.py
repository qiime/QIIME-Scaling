#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import listdir, mkdir
from os.path import join, isdir, exists
import numpy as np
from matplotlib import use
use('Agg', warn=False)
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from scaling.util import natural_sort


def process_timing_directory(timing_dir):
    """Retrieves the timing results stored in timing_dir in a dict form

    Inputs:
        timing_dir: path to the directory containing the timing results. It
            should contain only directories in the first level in the directory
            structure and only files on the second level of the directory
            structure

    Returns a dictionary with the following structure:
        {
            label: list of strings with the test cases names,
            wall_time: (list of float - means, list of float - std dev),
            cpu_user: (list of float - means, list of float - std dev),
            cpu_kernel: (list of float - means, list of float - std dev),
            memory: (list of float - means, list of float - std dev)
        }

    Note: raises a ValueError if there is some file in the first level in the
        directory structure of timing_dir
    """
    # Initialize output dictionary
    data = {}
    data['label'] = []
    data['wall_time'] = ([], [])
    data['cpu_user'] = ([], [])
    data['cpu_kernel'] = ([], [])
    data['memory'] = ([], [])

    # listdir returns the contents in an arbitrary order - sort them
    dirlist = listdir(timing_dir)
    dirlist = natural_sort(dirlist)
    # Loop over the contents of timing_dir
    for dirname in dirlist:
        # Get the path to the current content
        dirpath = join(timing_dir, dirname)
        # Check if it is not a directory - raise a ValueError if True
        if not isdir(dirpath):
            raise ValueError("%s contains a file: %s. Only directories are "
                             "allowed!" % (timing_dir, dirpath))

        # Initialize lists for bench results
        wall_time = []
        cpu_user = []
        cpu_kernel = []
        memory = []
        # Loop over the timing files in the current directory
        filelist = listdir(dirpath)
        filelist = sorted(filelist)
        for filename in filelist:
            # Get the path to the current timing file
            filepath = join(dirpath, filename)
            # Read the first line of the timing file
            f = open(filepath, 'U')
            info = f.readline().strip().split(';')
            f.close()
            # If first line is not of the form
            # <wall time>;<user time>;<cpu time>;<memory>
            # means that the command didn't finish correctly. Print a warning
            # message to let the user know
            if len(info) != 4:
                print "Warning - File %s not used:" % filepath
            else:
                wall_time.append(float(info[0]))
                cpu_user.append(float(info[1]))
                cpu_kernel.append(float(info[2]))
                memory.append(float(info[3]))

        # Cast Python arrays to numpy arrays
        wall_time = np.array(wall_time)
        cpu_user = np.array(cpu_user)
        cpu_kernel = np.array(cpu_kernel)
        memory = np.array(memory)
        # Add mean and std-dev to the output dictionary
        data['label'].append(float(dirname))
        data['wall_time'][0].append(np.mean(wall_time))
        data['wall_time'][1].append(np.std(wall_time))
        data['cpu_user'][0].append(np.mean(cpu_user))
        data['cpu_user'][1].append(np.std(cpu_user))
        data['cpu_kernel'][0].append(np.mean(cpu_kernel))
        data['cpu_kernel'][1].append(np.std(cpu_kernel))
        data['memory'][0].append(np.mean(memory))
        data['memory'][1].append(np.std(memory))

    # Transform labels to a numpy array
    data['label'] = np.array(data['label'])
    # Return the output dictionary
    return data


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


def generate_poly_label(poly, deg):
    """Returns a string representing the given polynomial

    Input:
        poly: numpy array of float
        deg: float
    """
    s = ""
    for i in range(deg):
        s += str(poly[i]) + "*x^" + str(deg-i) + " + "
    s += str(poly[deg])
    return s


def make_bench_plot(data, fit_key, keys, title, ylabel, scale=1):
    """Creates a matplotlib figure with the benchmark results present in data

    Input:
        data: dictionary with the benchmark results
        fit_key: key of data to use for computing the curve fitting
        keys: list of keys of data to plot in the figure
        title: string with the title of the plot
        ylabel: string with the title of the y axis
        scale: value to use as a scaling factor for the values in data
    """
    # Get the x axis data
    x = data['label']
    # For the function resulted from curve fitting, we use an extended x axis,
    # so the trend line is more clear
    interval = x[1] - x[0]
    x2 = np.arange(x[0] - interval, x[-1] + 2*interval)
    # Generate plot
    # First plot the fitted curve
    poly, deg = curve_fitting(x, data[fit_key][0])
    poly_label = generate_poly_label(poly, deg)
    y = np.polyval(poly, x2)
    y = y / scale
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.plot(x2, y, 'k', label=poly_label)
    # Plot the rest of the keys
    for key in keys:
        y, y_err = data[key]
        y = np.array(y) / scale
        y_err = np.array(y) / scale
        ax.errorbar(x, y, yerr=y_err, label=key)
    fontP = FontProperties()
    fontP.set_size('small')
    figure.suptitle(title)
    ax.set_xlabel('Input file')
    ax.set_ylabel(ylabel)
    return figure, poly_label


def process_benchmark_results(input_dir):
    """Processes the benchmark results stored in input_dir

    Inputs:
        input_dir: path to the directory containing the timing results

    Walks through the input_dir folder retrieving the benchmark information and
        generates a figure with the timing results and the memory consumption
        results. It also returns two string containing the polynomial with the
        best curve fit to the wall time and memory consumption data.
    """
    # Retrieve the benchmark results
    data = process_timing_directory(input_dir)
    # Generate the plot with the timing results
    fit_key = "wall_time"
    keys = ["wall_time", "cpu_user", "cpu_kernel"]
    time_plot, time_poly = make_bench_plot(data, fit_key, keys, "Running time",
                                           "Time (s)")
    # Generate the plot with the memory results
    fit_key = "memory"
    keys = ["memory"]
    mem_plot, mem_poly = make_bench_plot(data, fit_key, keys, "Memory usage",
                                         "Memory (GB)", scale=1024*1024)
    return data, time_plot, time_poly, mem_plot, mem_poly


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


def compare_benchmark_results(input_dirs, labels):
    """Compares in a single plot the benchmark results listed in input_dirs

    Inputs:
        input_dirs: list of paths to the directories containing the timing
            results
        labels: list of strings to label the plot data series

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
