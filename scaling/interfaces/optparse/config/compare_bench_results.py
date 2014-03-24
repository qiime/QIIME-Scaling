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

from scaling.commands.bench_results_comparator import CommandConstructor
from scaling.interfaces.optparse.input_handler import (
    load_summarized_results_list)
from scaling.interfaces.optparse.output_handler import write_comparison_results

# Convenience function for looking up parameters by name.
cmd_in_lookup = make_command_in_collection_lookup_f(CommandConstructor)
cmd_out_lookup = make_command_out_collection_lookup_f(CommandConstructor)

# Examples of how the command can be used from the command line using an
# optparse interface.
usage_examples = [
    OptparseUsageExample(ShortDesc="Compare different runs results of the same"
                         " bench suite",
                         LongDesc="Takes a comma-separated list with paths to "
                         "directories with benchmark results and generates a "
                         "plot with the wall time and a plot with the memory "
                         "consumption of the different runs, allowing "
                         "performance comparison between them.",
                         Ex="%prog -i timing1,timing2 -l run1,run2 -o plots")
]

# inputs map command line arguments and values onto Parameters. It is possible
# to define options here that do not exist as parameters, e.g., an output file.
inputs = [
    OptparseOption(Parameter=cmd_in_lookup('bench_results'),
                   Type='existing_filepaths',
                   Action='store',
                   Handler=load_summarized_results_list,
                   ShortName='i',
                   Name='input_dirs',
                   Required=True,
                   Help="Comma-separated list with the paths to the "
                        "directories of the time results of different runs of "
                        "the same bench suite",
                   ),
    OptparseOption(Parameter=cmd_in_lookup('labels'),
                   Type='str',
                   Action='store',
                   Handler=string_list_handler,
                   ShortName='l',
                   Name='labels',
                   Required=True,
                   Help='List of strings to label each data series of the plot'
                   ),
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
    OptparseResult(Parameter=cmd_out_lookup('comp_data'),
                   Handler=write_comparison_results,
                   InputName='output-dir'),
]
