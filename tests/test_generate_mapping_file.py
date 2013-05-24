#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from cogent.util.unit_test import TestCase, main
from numpy.random import seed
from numpy import array
from qiime.util import get_tmp_filename, load_qiime_config
from os import remove, path
from scaling.generate_mapping_file import parse_reference_file, \
    random_discrete_value, random_continuous_value, generate_mapping_file

class TestGenerateMappingFile(TestCase):
    def setUp(self):
        # Get QIIME's temp dir
        self.qiime_config = load_qiime_config()
        self.tmp_dir = self.qiime_config['temp_dir'] or '/tmp/'
        # Reference files for testing barcode parser
        self.ref_file = reference_file.splitlines()
        self.empty_ref_file = empty_reference_file.splitlines()
        self.bad_ref_file = bad_reference_file.splitlines()
        # Test folder
        test_folder = path.dirname(path.abspath(__file__))
        # Otu table filepath
        self.biom_fp = path.join(test_folder, 'support_files/10x10x0.010_bench.biom')
        # Reference filepath
        self.ref_fp = path.join(test_folder, 'support_files/test_reference.txt')
        # Primer sequence to use
        self.primer = 'TATGGTAATT'

        self._paths_to_clean_up = []

    def tearDown(self):
        map(remove, self._paths_to_clean_up)

    def test_parse_reference_file(self):
        """"""
        obs = parse_reference_file(self.ref_file)
        self.assertEquals(obs.next(), "TCCCTTGTCTCC")
        self.assertEquals(obs.next(), "ACGAGACTGATT")
        self.assertEquals(obs.next(), "GCTGTACGGATT")
        self.assertEquals(obs.next(), "ATCACCAGGTGT")
        self.assertRaises(StopIteration, obs.next)

        obs = parse_reference_file(self.empty_ref_file)
        self.assertRaises(StopIteration, obs.next)

        obs = parse_reference_file(self.bad_ref_file)
        self.assertRaises(ValueError, obs.next)


    def test_random_discrete_value(self):
        def random_func(n=3, size=5):
            return array([2,1,2,2,0])

        obs = random_discrete_value(5, random_f=random_func)
        self.assertEquals(obs.next(), "Value_C")
        self.assertEquals(obs.next(), "Value_B")
        self.assertEquals(obs.next(), "Value_C")
        self.assertEquals(obs.next(), "Value_C")
        self.assertEquals(obs.next(), "Value_A")
        self.assertRaises(StopIteration, obs.next)

    def test_random_continuos_value(self):
        def random_func(n=5):
            return array([0.123,0.321,0.222,0.5424,0.43124])

        obs = random_continuous_value(5, random_f=random_func)
        self.assertAlmostEquals(obs.next(), 0.123)
        self.assertAlmostEquals(obs.next(), 0.321)
        self.assertAlmostEquals(obs.next(), 0.222)
        self.assertAlmostEquals(obs.next(), 0.5424)
        self.assertAlmostEquals(obs.next(), 0.43124)
        self.assertRaises(StopIteration, obs.next)

    def test_generate_mapping_file(self):
        outpath = get_tmp_filename(tmp_dir=self.tmp_dir,suffix='.txt')
        self._paths_to_clean_up = [outpath]

        def random_func_disc(n=3, size=10):
            return array([2,1,2,2,0,2,2,1,2,1])

        def random_func_cont(n=10):
            return array([0.980764198385, 0.684829738585, 0.480931901484,
                0.392117518194, 0.343178016151, 0.729049707384, 0.43857224468, 
                0.0596778966096, 0.39804425533, 0.737995405732])


        generate_mapping_file(self.biom_fp, self.ref_fp, self.primer, outpath,
            rand_disc_f=random_func_disc, rand_cont_f=random_func_cont)

        exp = expected_mapping_fp

        outfile = open(outpath, 'U')
        self.assertEquals(outfile.readlines(), exp)
        outfile.close()
        


reference_file="""#This line is a comment and it is ignored
# More comments
# Empty lines should be ignored too

CAAGCAGAAGACGGCATACGAGAT\tTCCCTTGTCTCC\tAGTCAGTCAG\tCC\tGGACTACHVGGGTWTCTAAT\t806rcbc0
CAAGCAGAAGACGGCATACGAGAT\tACGAGACTGATT\tAGTCAGTCAG\tCC\tGGACTACHVGGGTWTCTAAT\t806rcbc1
CAAGCAGAAGACGGCATACGAGAT\tGCTGTACGGATT\tAGTCAGTCAG\tCC\tGGACTACHVGGGTWTCTAAT\t806rcbc2
# Comments can be anywhere
CAAGCAGAAGACGGCATACGAGAT\tATCACCAGGTGT\tAGTCAGTCAG\tCC\tGGACTACHVGGGTWTCTAAT\t806rcbc3
# Also at the end"""

empty_reference_file="""#A reference file with no barcodes
#It should throw an error (StopIteration error)"""

bad_reference_file="""#A reference file not following the specified format
#It should throw and error (bad format)
CAAGCAGAAGACGGCATACGAGAT\tGCTGTACGGATT\tGGACTACHVGGGTWTCTAAT\t806rcbc2"""

expected_mapping_fp=[
"#SampleID\tBarcodeSequence\tLinkerPrimerSequence\tDiscrete\tContinuous\tDescription\n",
"0\tTCCCTTGTCTCC\tTATGGTAATT\tValue_C\t0.980764198385\tSampleId_0\n",
"1\tACGAGACTGATT\tTATGGTAATT\tValue_B\t0.684829738585\tSampleId_1\n",
"2\tGCTGTACGGATT\tTATGGTAATT\tValue_C\t0.480931901484\tSampleId_2\n",
"3\tATCACCAGGTGT\tTATGGTAATT\tValue_C\t0.392117518194\tSampleId_3\n",
"4\tTGGTCAACGATA\tTATGGTAATT\tValue_A\t0.343178016151\tSampleId_4\n",
"5\tATCGCACAGTAA\tTATGGTAATT\tValue_C\t0.729049707384\tSampleId_5\n",
"6\tGTCGTGTAGCCT\tTATGGTAATT\tValue_C\t0.43857224468\tSampleId_6\n",
"7\tAGCGGAGGTTAG\tTATGGTAATT\tValue_B\t0.0596778966096\tSampleId_7\n",
"8\tATCCTTTGGTTC\tTATGGTAATT\tValue_C\t0.39804425533\tSampleId_8\n",
"9\tTACAGCGCATAC\tTATGGTAATT\tValue_B\t0.737995405732\tSampleId_9\n"]

if __name__ == '__main__':
    main()