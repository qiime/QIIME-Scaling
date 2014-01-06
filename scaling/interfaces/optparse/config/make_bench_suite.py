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
from pyqi.core.interfaces.optparse.output_handler import write_string
from scaling.commands.bench_suite_maker import CommandConstructor
from scaling.interfaces.optparse.input_handler import (get_bench_paths,
                                                        load_parameters)

# Convenience function for looking up parameters by name.
cmd_in_lookup = make_command_in_collection_lookup_f(CommandConstructor)
cmd_out_lookup = make_command_out_collection_lookup_f(CommandConstructor)

# Examples of how the command can be used from the command line using an
# optparse interface.
usage_examples = [
    OptparseUsageExample(ShortDesc="Parameters example usage",
        LongDesc="Test the command \"pick_otus.py\" using different "
            "similarity values. The file parameters.txt should follow these "
            "structure\nsimilarity<tab>val1,val2,val3",
        Ex="%prog -c \"pick_otus.py -i seqs.fna\" -p parameters.txt "
            "-o pick_otus_bench_suite.sh"),
    OptparseUsageExample(ShortDesc="Input files example usage",
        LongDesc="Test the command \"pick_otus.py\" using different input files"
            "The folder bench_files should include only the input files used "
            "by the command",
        Ex="%prog -c \"pick_otus.py\" -i bench_files -o "
            "pick_otus_bench_suite.sh"),
    OptparseUsageExample(ShortDesc="Multiple input files example usage",
        LongDesc="Test the command \"split_librarires_fastq.py\" using "
            "different input files. These command takes the input file in pairs"
            " so we provide the input files in two different folders",
        Ex="%prog -c \"split_librarires_fastq.py -m mapping.txt\" -i "
            "seqs_folder,barcode_folder --in_opts \"-i,-q\" -o "
            "split_librarires_fastq_bench_suite.sh")
]

# inputs map command line arguments and values onto Parameters. It is possible
# to define options here that do not exist as parameters, e.g., an output file.
inputs = [
    OptparseOption(Parameter=cmd_in_lookup('bench_files'),
                   Type='existing_dirpaths',
                   Action='store', # default is 'store', change if desired
                   Handler=get_bench_paths, # must be defined if desired
                   ShortName='i', # must be defined if desired
                   # Name='bench_files', # implied by Parameter
                   # Required=False, # implied by Parameter
                   # Help='List of lists of paths to the benchmark files to use as input for the command. Each inner list is a test case and should have the same length as the in_opts parameter.', # implied by Parameter
                   # Default=None, # implied by Parameter
                   # DefaultDescription='No bench_files used', # implied by Parameter),
                   ),
    OptparseOption(Parameter=cmd_in_lookup('command'),
                   Type='str',
                   Action='store', # default is 'store', change if desired
                   Handler=None, # must be defined if desired
                   ShortName='c', # must be defined if desired
                   # Name='command', # implied by Parameter
                   # Required=True, # implied by Parameter
                   # Help='command to benchmark', # implied by Parameter
                   ),
    OptparseOption(Parameter=cmd_in_lookup('in_opts'),
                   Type='str',
                   Action='store', # default is 'store', change if desired
                   Handler=string_list_handler, # must be defined if desired
                   ShortName=None, # must be defined if desired
                   # Name='in_opts', # implied by Parameter
                   # Required=False, # implied by Parameter
                   # Help='list of options used for providing the benchmark files to the command. It should have the same length and order than the inner lists of bench_files.', # implied by Parameter
                   Default='-i', # implied by Parameter
                   # DefaultDescription='No in_opts used', # implied by Parameter),
                   ),
    OptparseOption(Parameter=cmd_in_lookup('out_opt'),
                   Type='str',
                   Action='store', # default is 'store', change if desired
                   Handler=None, # must be defined if desired
                   ShortName=None, # must be defined if desired
                   # Name='out_opt', # implied by Parameter
                   # Required=False, # implied by Parameter
                   # Help='Option used for providing the output path to the command to benchmark.', # implied by Parameter
                   # Default='-o', # implied by Parameter
                   # DefaultDescription='"-o" is used as default', # implied by Parameter),
                   ),
    OptparseOption(Parameter=cmd_in_lookup('parameters'),
                   Type='existing_filepath',
                   Action='store', # default is 'store', change if desired
                   Handler=load_parameters, # must be defined if desired
                   ShortName='p', # must be defined if desired
                   # Name='parameters', # implied by Parameter
                   # Required=False, # implied by Parameter
                   # Help='dictionary where the keys are the parameters to test and the values are a list of values for such parameter.', # implied by Parameter
                   # Default=None, # implied by Parameter
                   # DefaultDescription='No parameters used', # implied by Parameter),
                   ),
    OptparseOption(Parameter=None,
                    Type='new_filepath',
                    ShortName='o',
                    Name='output-fp',
                    Required=True,
                    Help='the output filepath')
]

# outputs map result keys to output options and handlers. It is not necessary
# to supply an associated option, but if you do, it must be an option from the
# inputs list (above).
outputs = [
    # An example option that maps to a CommandIn.
    # OptparseResult(Parameter=cmd_out_lookup('name_of_a_command_out'),
    #                Handler=write_string, # a function applied to the output of the Command
    #                # the name of the option (defined in inputs, above), whose
    #                # value will be made available to Handler. This name
    #                # can be either an underscored or dashed version of the
    #                # option name (e.g., 'output_fp' or 'output-fp')
    #                InputName='output-fp'), 
    #
    # An example option that does not map to a CommandIn.
    # OptparseResult(Parameter=cmd_out_lookup('some_other_result'),
    #                Handler=print_string)

    OptparseResult(Parameter=cmd_out_lookup('bench_suite'),
                    Handler=write_string, # must be defined
                    InputName='output-fp'), # define if tying to an OptparseOption
]
