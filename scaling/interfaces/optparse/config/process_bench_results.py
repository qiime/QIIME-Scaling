#!/usr/bin/env python
from __future__ import division

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME scaling project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from pyqi.core.interfaces.optparse import (OptparseUsageExample,
                                           OptparseOption, OptparseResult)
from pyqi.core.command import (make_command_in_collection_lookup_f,
                               make_command_out_collection_lookup_f)
from scaling.commands.bench_results_processer import CommandConstructor
from scaling.interfaces.optparse.output_handler import (write_summarized_results,
                                                        write_matplotlib_figure,
                                                        write_string_to_dir)

# Convenience function for looking up parameters by name.
cmd_in_lookup = make_command_in_collection_lookup_f(CommandConstructor)
cmd_out_lookup = make_command_out_collection_lookup_f(CommandConstructor)

# Examples of how the command can be used from the command line using an
# optparse interface.
usage_examples = [
    OptparseUsageExample(ShortDesc="A short single sentence description of the example",
                         LongDesc="A longer, more detailed description",
                         Ex="%prog --foo --bar some_file")
]

# inputs map command line arguments and values onto Parameters. It is possible
# to define options here that do not exist as parameters, e.g., an output file.
inputs = [
    OptparseOption(Parameter=cmd_in_lookup('input_dir'),
                   Type='existing_filepath',
                   Action='store', # default is 'store', change if desired
                   Handler=None, # must be defined if desired
                   ShortName='i', # must be defined if desired
                   # Name='input_dir', # implied by Parameter
                   # Required=True, # implied by Parameter
                   # Help='Path to the directory with the time results', # implied by Parameter
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
    OptparseResult(Parameter=cmd_out_lookup('bench_data'),
                    Handler=write_summarized_results,
                    InputName='output-dir'),
    OptparseResult(Parameter=cmd_out_lookup('mem_fig'),
                    Handler=write_matplotlib_figure,
                    InputName='output-dir'),
    OptparseResult(Parameter=cmd_out_lookup('mem_str'),
                    Handler=write_string_to_dir,
                    InputName='output-dir'),
    OptparseResult(Parameter=cmd_out_lookup('time_fig'),
                    Handler=write_matplotlib_figure,
                    InputName='output-dir'),
    OptparseResult(Parameter=cmd_out_lookup('time_str'),
                    Handler=write_string_to_dir,
                    InputName='output-dir'),
]
