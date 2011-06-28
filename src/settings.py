'''
Settings file
'''

###########
#Debug Variable
DEBUG = True
###########

from os.path import dirname, abspath
basedir = dirname(abspath(__file__)) + '/'

#base path for the output of the procedure
BASE_OUTPUT_PATH = basedir + 'out'

#list of files that MUST be in each output directory
BASE_FILES = {'new':'bibcodes_to_extract_new_mod.dat', 'del':'bibcodes_to_extract_del.dat', 'done':'bibcodes_extracted.dat', 'prob':'bibcodes_with_problems.dat'}

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