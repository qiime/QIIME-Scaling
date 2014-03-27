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
from os.path import abspath, join, isdir
from warnings import warn

from scaling.parse import parse_parameters_file, parse_summarized_results
from scaling.util import natural_sort, BenchCase


def load_parameters(param_fp):
    """Return a parsed parameters file

    Parameters
    ----------
    param_fp : string
        Filepath to the parameters file

    Returns
    -------
    Dictionary with the parameters file contents
    """
    if param_fp:
        with open(param_fp, 'U') as param_f:
            return parse_parameters_file(param_f)


def load_summarized_results_list(input_fps):
    """Parses all the results summary in input_fps

    Parameters
    ----------
    input_fps : Iterable
        Filepaths to the results summary files

    Returns
    -------
    GeneratorType
        Yields the parsed files
    """
    for input_fp in input_fps:
        with open(input_fp, 'U') as f:
            yield parse_summarized_results(f)


def get_bench_paths(input_dirs):
    """Goes through the contents in each directory and returns their path

    Lists all the elements in each of the directories listed in input_dirs and
    group the files based on their name ordering.

    Parameters
    ----------
    input_dirs : Iterable
        Paths to the directories where the benchmark files are located

    Returns
    -------
    list of lists: return a list of input cases in which each input case is
        a list of files

    Raises
    ------
    ValueError
        If all the input directories does not contain the same number of items
    """
    if input_dirs:
        bench_paths_by_dir = []

        # Loop through the list of directories
        for input_dir in input_dirs:
            # Get the contents of the current folder
            input_dir = abspath(input_dir)
            paths = listdir(input_dir)
            # Add the folder to the paths, we get absolute paths already
            paths = map(join, [input_dir] * len(paths), paths)
            bench_paths_by_dir.append(paths)

        # Check that all the input folders contain the same number of items
        n = len(bench_paths_by_dir[0])
        if not all(len(x) == n for x in bench_paths_by_dir):
            raise ValueError("All the input directories should contain the "
                             "same number of items.")

        # Sort all the lists. It is assumed that all the file or directory
        # names present on such directories match across benchmark folders
        bench_paths_by_dir = map(natural_sort, bench_paths_by_dir)

        # Group the files in different folders by their name matching
        bench_files = []
        for i in range(len(bench_paths_by_dir[0])):
            bench_files.append([paths[i] for paths in bench_paths_by_dir])

        return bench_files


def parse_timing_directory(timing_dir):
    """Retrieves the timing results stored in timing_dir in a dict form

    Parameters
    ----------
    timing_dir : string
        path to the directory containing the timing results. It should contain
        only directories in the first level in the directory structure and only
        files on the second level of the directory structure

    Returns
    -------
    GeneratorType
        Yields BenchCase namedtuples

    Raises
    ------
    ValueError
        If there is some file in the first level of the input directory
        structure
    """
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
        # Initialize the BenchCase results tuple
        case = BenchCase(dirname, [], [], [], [])
        # Loop over the timing files in the current directory
        filelist = listdir(dirpath)
        filelist = natural_sort(filelist)
        for filename in filelist:
            # Get the path to the current timing file
            filepath = join(dirpath, filename)
            # Read the first line of the timing file
            with open(filepath, 'U') as f:
                info = f.readline().strip().split(';')
            # If first line does not follow the structure
            # <wall time>;<user time>;<cpu time>;<memory>
            # means that the command didn't finish correctly. Print a warning
            # message to let the user know
            if len(info) != 4:
                warn("File %s not used" % filepath, RuntimeWarning)
            else:
                case.wall.append(float(info[0]))
                case.user.append(float(info[1]))
                case.kernel.append(float(info[2]))
                case.mem.append(float(info[3]))
        yield case
