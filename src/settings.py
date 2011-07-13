'''
Settings file
'''

from os.path import dirname, abspath
basedir = dirname(abspath(__file__)) + '/'

#base path for the output of the procedure
BASE_OUTPUT_PATH = basedir + 'out'

#list of files that MUST be in each output directory
BASE_FILES = {'new':'bibcodes_to_extract_new_mod.dat', 'del':'bibcodes_to_extract_del.dat', 'done':'bibcodes_extracted.dat', 'prob':'bibcodes_with_problems.dat'}

#file where to store the extraction name log
EXTRACTION_FILENAME_LOG = 'extraction_name_log.txt'
EXTRACTION_BASE_NAME = 'extraction_'

#files with list of bibcodes and timestamps
#AST
BIBCODES_AST = '/proj/ads/abstracts/ast/load/latest/index.status'
#PHY
BIBCODES_PHY = '/proj/ads/abstracts/phy/load/latest/index.status'
#GEN
BIBCODES_GEN = '/proj/ads/abstracts/gen/load/latest/index.status'
#PRE
BIBCODES_PRE = '/proj/ads/abstracts/pre/load/latest/index.status'
#ALL
BIBCODES_ALL = '/proj/ads/abstracts/config/bib2accno.dat'

#style sheet path
STYLESHEET_PATH = basedir + 'xsl/adsXml2MarkXml.xsl'

#base name for the file of bibcodes to delete
BIBCODE_TO_DELETE_OUT_NAME = 'AAA_bibcode_to_delete'
#base name for the marcXML files
MARCXML_FILE_BASE_NAME = 'marcxml'

#maximum number of bibcodes per group of extraction -> it means that this is also the maximum number of bibcodes per file of marcxml
NUMBER_OF_BIBCODES_PER_GROUP = 10000

#maximum number of worker processes that have to run
NUMBER_WORKERS = 6