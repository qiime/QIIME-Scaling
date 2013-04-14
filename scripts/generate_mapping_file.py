#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from cogent.util.option_parsing import parse_command_line_parameters,\
                                        make_option
from scaling.generate_mapping_file import generate_mapping_file
from os.path import split, splitext

DEFAULT_REF_FILE = '../scaling/support_files/Caporaso_et_al_ISME_2012_8.txt'
DEFAULT_PRIMER = 'TATGGTAATT'

script_info = {}
script_info['brief_description'] = """Generates a sample mapping\
 file for a given OTU table."""
script_info['script_description'] = """Given an OTU table, the script generates\
 a QIIME mapping file with the following headers: SampleID, BarcodeSequence,\
 LinkerPrimerSequence, Discrete, Continuous, Description where SampleID are the\
 sample Ids from the input OTU table, the BarcodeSequence are the barcode\
 sequences from the given reference file, the LinkerPrimerSequence is the given\
 linker primer sequence (or the default), the Discrete column contains discrete\
 values, the Continuous column contins continuous values and the Description\
 columns contains a description of the sample (currently, the SampleID)."""
script_info['script_usage'] = [ ("Example:", "Generate the mapping file\
 'map_file.txt' for the OTU table 'otu_table.biom'",
 "%prog -i otu_table.biom -o map_file")]
script_info['output_description'] = """A QIIME mapping file"""
script_info['required_options'] = [
    make_option('-i', '--input_biom', type='existing_filepath',
        help='OTU table for which the mapping file is for.')
    ]
script_info['optional_options'] = [
    make_option('-o', '--output_map', type='new_filepath',
        help='The output mapping file path.'),
    make_option('-b', '--barcode_ref', type='existing_filepath',
        default=DEFAULT_REF_FILE,
        help="A reference file from where to extract the barcodes\
         [default: %default]."),
    make_option('-p', '--primer', type='string', default=DEFAULT_PRIMER,
        help='The linker primer sequence to use in the mapping file\
         [default: %default].')
    ]
script_info['version'] = __version__

if __name__ == '__main__':
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    input_biom = opts.input_biom
    output_map = opts.output_map
    barcode_ref = opts.barcode_ref
    primer = opts.primer

    if not output_map:
        # Get the otu table file basename and add '_mapping.txt' at the end
        output_map = splitext(split(input_biom)[1])[0] + '_mapping.txt'

    generate_mapping_file(input_biom, barcode_ref, primer, output_map)