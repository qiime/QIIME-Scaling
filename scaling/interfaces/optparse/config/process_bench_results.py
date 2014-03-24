#!/usr/bin/env python
from __future__ import division

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from pyqi.core.interfaces.optparse import (OptparseUsageExample,
                                           OptparseOption, OptparseResult)
from pyqi.core.command import (make_command_in_collection_lookup_f,
                               make_command_out_collection_lookup_f)
from pyqi.core.interfaces.optparse.input_handler import string_list_handler

from scaling.commands.bench_results_processer import CommandConstructor
from scaling.interfaces.optparse.output_handler import write_bench_results
from scaling.interfaces.optparse.input_handler import parse_timing_directory

# Convenience function for looking up parameters by name.
cmd_in_lookup = make_command_in_collection_lookup_f(CommandConstructor)
cmd_out_lookup = make_command_out_collection_lookup_f(CommandConstructor)

# Examples of how the command can be used from the command line using an
# optparse interface.
usage_examples = [
    OptparseUsageExample(ShortDesc="Processes the benchmark suite results",
                         LongDesc="Takes the benchmark suite output directory "
                         "and processes the benchmark measurements, creating "
                         "plots and collapsing results in a usable form.",
                         Ex="%prog -i timing -o plots"),
    OptparseUsageExample(ShortDesc="Wait for a set of PBS jobs to complete and"
                         " process the benchmark suite results",
                         LongDesc="Takes a list of PBS job ids, wait for its "
                         "completion and then takes the benchmark suite output"
                         " directory and processes the benchmark measurements,"
                         " creating plots and collapsing results in a usable "
                         "form.",
                         Ex="%prog -i timing -o plots -w 124311,124312,124313")
]

# inputs map command line arguments and values onto Parameters. It is possible
# to define options here that do not exist as parameters, e.g., an output file.
inputs = [
    OptparseOption(Parameter=cmd_in_lookup('bench_results'),
                   Type='existing_dirpath',
                   Action='store',
                   Handler=parse_timing_directory,
                   ShortName='i',
                   Name='input_dir',
                   Required=True,
                   Help='Path to the directory with the time results',
                   ),
    OptparseOption(Parameter=cmd_in_lookup('job_ids'),
                   Type='str',
                   Action='store',
                   Handler=string_list_handler,
                   ShortName='w',
                   Name='wait_on',
                   Required=False,
                   Help='Comma-separated list of job ids to wait for before '
                        'processing the results'),
    OptparseOption(Parameter=None,
                   Type='new_dirpath',
                   ShortName='o',
                   Name='output-dir',
                   Required=True,
                   Help='The output directory')
]

# outputs map result keys to output options and handlers. It is not necessary
# to supply an associated option, but if you do, it must be an option from the
# inputs list (above).
outputs = [
    OptparseResult(Parameter=cmd_out_lookup('bench_data'),
                   Handler=write_bench_results,
                   InputName='output-dir'),
]
