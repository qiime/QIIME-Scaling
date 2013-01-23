#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2011, The QIIME Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from cogent.util.option_parsing import parse_command_line_parameters, make_option
from biom.parse import parse_biom_table
from os.path import split, splitext
from numpy.random import rand, randint

DEFAULT_REF_FILE = './support_files/Caporaso_et_al_ISME_2012_8.txt'
DEFAULT_PRIMER = 'TATGGTAATT'

script_info = {}
script_info['brief_description'] = """Generates a sample mapping file for a given OTU table."""
script_info['script_description'] = """Given an OTU table, the script generates a QIIME mapping file \
with the following headers: SampleID, BarcodeSequence, LinkerPrimerSequence, Discrete, Continuous, Description \
where SampleID are the sample Ids from the input OTU table, the BarcodeSequence are the barcode sequences from \
the given reference file, the LinkerPrimerSequence is the given linker primer sequence (or the default), \
the Discrete column contains discrete values, the Continuous column contins continuous values and the \
Description columns contains a description of the sample (currently, the SampleID)."""
script_info['script_usage'] = [
	("Example:", "Generate the mapping file 'map_file.txt' for the OTU table 'otu_table.biom", "%prog -i otu_table.biom -o map_file")]
script_info['output_description'] = """A QIIME mapping file"""
script_info['required_options'] = [
	make_option('-i', '--input_biom', type='existing_filepath',
		help='OTU table for which the mapping file is for.')
	]
script_info['optional_options'] = [
	make_option('-o', '--output_map', type='new_filepath',
		help='The output mapping file path.'),
	make_option('-b', '--barcode_ref', type='existing_filepath', default=DEFAULT_REF_FILE,
		help='A reference file from where to extract the barcodes [default: %default].'),
	make_option('-p', '--primer', type='string', default=DEFAULT_PRIMER,
		help='The linker primer sequence to use in the mapping file [default: %default].')
	]
script_info['version'] = __version__

def parse_reference_file(lines):
	"""Yields a Golay barcode from the reference file.

	Arguments:
		- lines: the reference file object

	The reference file should have the following format:
		- Any line starting with a # is a comment
		- For each line, the following fields (tab separated)
			* Reverse complement
			* Golay barcode
			* Reverse primer pad
			* Reverse primer linker
			* Reverse primer
	"""
	for line in lines:
		line = line.strip()
		if line:
			if not line.startswith('#'):
				rev_comp, golay_bc, rev_prim_pad, rev_prim_link, rev_prim, idx = line.split('\t')
				yield golay_bc

def random_discrete_value(num_values):
	"""Yields a random discrete value from a default set of 3 values

	Arguments:
		- num_values: the maximum number of values to yield

	The default set of values is (Value_A, Value_B and Value_C)
	"""
	rand_idx = randint(3, size=num_values)
	values_list = ['Value_A','Value_B','Value_C']
	for i in rand_idx:
		yield values_list[i]

def random_continuous_value(num_values):
	"""Yields a random continuous values from the interval [0, 1)
	
	Arguments:
		- num_values: the maximum number of values to yield

	Uses numpy.random.rand to return random number from a uniform
	distribution over [0, 1)
	"""
	rand_values = rand(num_values)
	for val in rand_values:
		yield val

def create_mapping_file(otu_table, out_file, bc_generator, primer):
	"""Creates a mapping file in out_file for otu_table.

	Arguments:
		- otu_table: the OTU table
		- out_file: the output file object where to write the mapping file
		- bc_generator: the barcode generator
		- primer: the linker primer sequence

	Creates a mapping file in 'out_file' for the otu table 'otu_table' using
	the barcode generator 'bc_generator' and the linker primer sequence 'primer'.
	It also adds a 'Discrete' column which contains discrete values, a 'Continous'
	columns which contains continuous values and a 'Description' column.
	"""
	# Write the headers to the output file
	out_file.write("#SampleID\tBarcodeSequence\tLinkerPrimerSequence\tDiscrete\tContinuous\tDescription\n")
	# Create random discrete and continuous value generators
	rand_discrete = random_discrete_value(len(otu_table.SampleIds))
	rand_continuous = random_continuous_value(len(otu_table.SampleIds))
	# For each sampleID create a new line
	for sid in otu_table.SampleIds:
		out_file.write(sid+"\t"+bc_generator.next()+"\t"+primer+"\t"+rand_discrete.next()+"\t"+str(rand_continuous.next())+"\t"+"SampleId_"+sid+"\n")

if __name__ == '__main__':
	option_parser, opts, args = parse_command_line_parameters(**script_info)
	input_biom = opts.input_biom
	output_map = opts.output_map
	barcode_ref = opts.barcode_ref
	primer = opts.primer

	if not output_map:
		# Get the otu table file basename and add '_mapping.txt' at the end
		output_map = splitext(split(input_biom)[1])[0] + '_mapping.txt'

	biom_file = open(input_biom, 'U')
	out_file = open(output_map, 'w')
	ref_file = open(barcode_ref, 'U')

	otu_table = parse_biom_table(biom_file)
	bc_generator = parse_reference_file(ref_file)

	create_mapping_file(otu_table, out_file, bc_generator, primer)

	biom_file.close()
	out_file.close()
	ref_file.close()