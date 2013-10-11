#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from scaling.option_parsing import parse_command_line_parameters, make_option
from scaling.process_results import compare_benchmark_results

script_info = {}
script_info['brief_description'] = """"""
script_info['script_description'] = """"""
script_info['script_usage'] = []
script_info['output_description'] = """"""
script_info['required_options'] = [
    make_option('-i', '--input_dirs', type='existing_dirpaths',
        help="Comma-separated list of paths to the directories containing" +
            "the timing results"),
    make_option('-l', '--labels', type='string',
        help="Comma-separated list of labels for each of the input " + 
            "directories. Used for label the plot data")
]
script_info['optional_options'] = [
    make_option('-o', '--output_dir', type='new_dirpath',
        default='./bench_compare', help="Path to the output directory " "[]")
]
script_info['version'] = __version__

if __name__ == '__main__':
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    results_dirs = opts.input_dirs
    labels = opts.labels.split(',')
    output_dir = opts.output_dir

    if len(labels) != len(results_dirs):
        raise ValueError, "You should pass a label for each input directory"

    compare_benchmark_results(results_dirs, labels, output_dir)