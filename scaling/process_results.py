#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import listdir, mkdir
from os.path import join, isdir, exists
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

def process_timing_directory(timing_dir, log_file):
    """Retrieves the timing results stored in timing_dir

    Inputs:
        timing_dir: path to the directory containing the timing results. It
            should contain only directories
        log_file: open file object for the log file

    Returns a dictionary with the following structure:
        {
            label: list of strings,
            wall_time: (list of float - means, list of float - std dev),
            cpu_user: (list of float - means, list of float - std dev),
            cpu_kernel: (list of float - means, list of float - std dev),
            memory: (list of float - means, list of float - std dev)
        }

    Note: raises a ValueError if there is some file in timing_dir
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
    dirlist = sorted(dirlist)
    # Loop over the contents of timing_dir
    for dirname in dirlist:
        # Get the path to the current content
        dirpath = join(timing_dir, dirname)
        # Check if it is not a directory - raise a ValueError if True
        if not isdir(dirpath):
            raise ValueError, "%s contains a file: %s." % (timing_dir,
                dirpath) + "Only directories are allowed!"

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
            # means that the command didn't finish correctly. Add a note on the
            # log file to let the user know
            if len(info) != 4:
                log_file.write("File %s not used: " % (filepath) + 
                    "the command didn't finish correctly\n")
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

def write_summarized_results(data, output_fp):
    """Writes in output_fp the summarized benchmark results present in data

    Input:
        data: a dictionary with the benchmark results (see
            process_timing_directory for the dictionary structure)
        output_fp: path to the output file

    Writes the benchmark results in a tab-delimited file, with the following
    headers: label, wall_mean, wall_std, user_mean, user_std, kernel_mean,
    kernel_std, mem_mean, mem_std
    Each row contains the results for a single experiment
    """
    # Write the headers in the file
    out_f = open(output_fp, 'w')
    headers = ["#label", "wall_mean", "wall_std", "user_mean", "user_std",
        "kernel_mean", "kernel_std", "mem_mean", "mem_std"]
    out_f.write("\t".join(headers) + "\n")
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
        out_f.write("\t".join(values) + "\n")
    out_f.close()

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
    SStot = np.sum( (y-mean)**2 )
    rsquare = 1 - (SSerr/SStot)

    return rsquare

def curve_fitting(x, y):
    """Fits a polynomial curve to the data points defined by x and y

    Input:
        x: numpy array of floats
        y: numpy array of floats

    Returns the polynomial curve with less degree that fits the data points
    with an Rsquare over 0.99999; and its degree.
    """
    deg = 0
    rsquare = 0
    while rsquare < 0.99999:
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

def make_plots(data, time_fp, mem_fp, log_file):
    """Generates the plots with the benchmark results present in data

    Input:
        data: a dictionary with the benchmark results (see
            process_timing_directory for the dictionary structure)
        time_fp: path to the output timing plot
        mem_fp: path to the output memory plot
        log_file: open file object for the log file

    Generates a plot with the timing results and the function that best fits the
    wall time mean curve. It also generates a plot with the memory usage results
    with the best fitted function too.
    """
    # Get the x axis data
    x = data['label']
    # For the function resulted from curve fitting, we use an extended x axis,
    # so the trend line is more clear
    interval = x[1] - x[0]
    x2 = np.arange(x[0] - interval, x[-1] + interval)

    # Generate time plot
    log_file.write("Generating time plot... \n")
    # Perform curve fitting against the wall time data
    poly, deg = curve_fitting(x, data['wall_time'][0])
    poly_label = generate_poly_label(poly, deg)
    y = np.polyval(poly, x2)
    plt.plot(x2, y, 'k', label=poly_label)
    log_file.write("Best fit: %s\n" % poly_label)

    # Plot the wall, user and kernel times
    for key in ['wall_time', 'cpu_user', 'cpu_kernel']:
        y, y_err = data[key]
        plt.errorbar(x, y, yerr=y_err, label=key)
    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(loc='best', prop=fontP, fancybox=True).get_frame().set_alpha(0.2)
    plt.title('Running time')
    plt.xlabel('Input file')
    plt.ylabel('Time (seconds)')
    plt.savefig(time_fp)
    plt.close()
    log_file.write("Generating time plot finished\n")

    # Generate memory plot
    log_file.write("Generating memory plot... \n")
    # Perform curve fitting against memory data
    poly, deg = curve_fitting(x, data['memory'][0])
    poly_label = generate_poly_label(poly, deg)
    y = np.polyval(poly, x2)
    y = y / (1024*1024)
    plt.plot(x2, y, 'k', label=poly_label)
    log_file.write("Best fit: %s\n" % poly_label)

    # Plot the memory data
    y, y_err = data['memory']
    y = np.array(y) / (1024*1024)
    y_err = np.array(y_err) / (1024*1024)
    plt.errorbar(x, y, yerr=y_err, label='Memory')
    plt.legend(loc='best', prop=fontP, fancybox=True).get_frame().set_alpha(0.2)
    plt.title('Memory usage')
    plt.xlabel('Input file')
    plt.ylabel('Memory (GB)')
    plt.savefig(mem_fp)
    plt.close()
    log_file.write("Generating memory plot finished\n")

def process_benchmark_results(input_dir, output_dir):
    """Processes the benchmark results stored in input_dir

    Inputs:
        input_dir: path to the directory containing the timing results
        output_dir: path to the output directory
    """
    # Create the output directory if it doesn't exists
    if not exists(output_dir):
        mkdir(output_dir)
    # Prepare the log file
    log_fp = join(output_dir, 'get_benchmark_results_log.txt')
    log_file = open(log_fp, 'w')
    # Retrieve the benchmark results
    log_file.write('Retrieving benchmark results... \n')
    data = process_timing_directory(input_dir, log_file)
    log_file.write('Retrieving benchmark results finished\n')
    # Write a file with the results summarized
    log_file.write('Writing summarized output... \n')
    summarized_fp = join(output_dir, 'summarized_results.txt')
    write_summarized_results(data, summarized_fp)
    log_file.write('Writing summarized output finished\n')
    # Generate the output plots
    log_file.write('Generating plots:\n')
    plot_time_fp = join(output_dir, 'time_plot.png')
    plot_mem_fp = join(output_dir, 'memory_plot.png')
    make_plots(data, plot_time_fp, plot_mem_fp, log_file)
    log_file.write('Generating plots finished\n')
    log_file.close()