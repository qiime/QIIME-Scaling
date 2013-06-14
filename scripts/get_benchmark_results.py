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
from scaling.process_results import process_benchmark_results

script_info = {}
script_info['brief_description'] = """"""
script_info['script_description'] = """"""
script_info['script_usage'] = []
script_info['output_description'] = """"""
script_info['required_options'] = [
    make_option('-i', '--input_dir', type='existing_dirpath',
        help="Path to the directory containing the timing results")
]
script_info['optional_options'] = [
    make_option('-o', '--output_dir', type='new_dirpath',
        help="Path to the output directory")
]
script_info['version'] = __version__

if __name__ == '__main__':
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    results_dir = opts.input_dir
    output_dir = opts.output_dir

    process_benchmark_results(results_dir, output_dir)
