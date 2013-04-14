#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from biom.parse import parse_biom_table
from numpy.random import rand, randint

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
                try:
                    (rev_comp, golay_bc, rev_prim_pad,
                        rev_prim_link, rev_prim, idx) = line.split('\t')
                except ValueError, e:
                    raise ValueError, "The reference file is not well-formated"
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

def generate_mapping_file(biom_fp, barcode_ref_fp, primer, output_fp):
    """ Creates a mapping file in output_fp for the otu table biom_fp

    Arguments:
        - biom_fp: the otu table file path in biom format
        - barcode_ref_fp: the reference file used to get the barcodes
        - primer: primer sequence to use in the mapping file
        - output_fp: output mapping file

    Creates a mapping file in 'output_fp' for the otu table 'biom_fp' using
    barcodes from the 'barcode_ref_fp' file and the linker primer sequence
    'primer'. It also adds to the mapping file two columns: 'Discrete' and 
    'Continuous', which contains a different discrete and continuous values,
    respectively.
    E.g. Discrete: Value_A, Value_B and Value_C
         Continuous: uniform distribution over [0, 1)
    """
    # Open all the files
    biom_file = open(biom_fp, 'U')
    ref_file = open(barcode_ref_fp, 'U')
    out_file = open(output_fp, 'w')

    # parse the input otu table
    otu_table = parse_biom_table(biom_file)
    # create a barcode generator from the reference file
    bc_generator = parse_reference_file(ref_file)
    # create a random discrete value generator
    rand_discrete = random_discrete_value(len(otu_table.SampleIds))
    # create a random continuous value generator
    rand_continuous = random_continuous_value(len(otu_table.SampleIds))

    # Write headers to the mapping file
    headers = ['#SampleID', 'BarcodeSequence', 'LinkerPrimerSequence',
                'Discrete', 'Continuous', 'Description']
    out_file.write("\t".join(headers) + "\n")

    # Add a new line in the mapping file for each Sample ID
    for sid in otu_table.SampleIds:
        values = [sid, bc_generator.next(), primer, rand_discrete.next(),
                str(rand_continuous.next()), "SampleId_"+sid]
        out_file.write("\t".join(values) + "\n")

    # Close all the files
    biom_file.close()
    out_file.close()
    ref_file.close()