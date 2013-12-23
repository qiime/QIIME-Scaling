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
from os.path import abspath, join
from scaling.parse import parse_parameters_file

def load_parameters(param_fp):
    """Return a parsed parameters file"""
    if param_fp:
        with open(param_fp, 'U') as param_f:
            return parse_parameters_file(param_f)
    return None

def get_bench_paths(input_dirs):
    """Goes through the item in each directory and returns their path

    Inputs:
        input_dirs: list of paths to the directories where the benchmark files
            are located
    Output:
        list of lists: return a list of input cases in which each input case is
            a list of files

    Lists all the elements in each of the directories listed in input_dirs and
    group the files based on their name ordering.

    Note: Raises a ValueError if all the input directories does not contain the
        same number of items
    """
    bench_paths_by_dir = []
    # Loop through the list of directories
    for input_dir in input_dirs:
        # Get the contents of the current folder
        input_dir = abspath(input_dir)
        paths = listdir(input_dir)
        # Add the folder to the paths, we get absolute paths already
        paths = map(join, [input_dir for p in paths], paths)
        bench_paths_by_dir.append(paths)
    # Check that all the input folders contain the same number of items
    n = len(bench_paths_by_dir[0])
    if not all(len(x) == n for x in bench_paths_by_dir):
        raise ValueError, "All the input directories should contain the same "+\
            "number of items."
    # Sort all the lists. It is assumed that all the file or directory names
    # present on such directories match across benchmark folders
    map(sorted, bench_paths_by_dir)
    # Group the files in different folders by their name matching
    bench_files = [[paths[i] for paths in bench_paths_by_dir]
        for i in range(len(bench_paths_by_dir[0]))]
    return bench_files