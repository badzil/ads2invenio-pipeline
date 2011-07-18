'''
Main module

It parses the parameters and calls the global manager
'''

from optparse import OptionParser

import pipeline_manager
from errors import GenericError

def parse_parameters():
    """Function that parse the parameters passed to the script"""
    parser = OptionParser()
    
    parser.add_option("-m", "--mode", dest="mode", help="Specify the method of extraction (full or update) ", metavar="MODEVALUE")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help='Use this parameter if a verbose execution is needed ')
    
    # catch the parameters from the command line
    options, _ = parser.parse_args()
    
    #Dictionary to return parameters
    parameters = {}
    
    if options.mode:
        if options.mode == 'full' or options.mode == 'update':
            parameters['mode'] = options.mode
        else:
            raise GenericError('Wrong parameter: the extraction can be only full or update')
    else:
        raise GenericError('Wrong parameter: the extraction can be only full or update')
    
    if options.verbose:
        parameters['verbose'] = True
    else:
        parameters['verbose'] = False
    
    return parameters

def main():
    """ Main Function"""
    
    #Manage parameters
    parameters = parse_parameters()
    
    #I call the global manager
    genm = pipeline_manager.pipelineManager(parameters['mode'], parameters['verbose'])
    genm.manage()
    
if __name__ == "__main__":
    main()