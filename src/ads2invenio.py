'''
Main module

It parses the parameters and calls the global manager
'''

import pipeline_manager

def parse_parameters():
    """Function that parse the parameters passed to the script"""
    from optparse import OptionParser
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
            raise 'Wrong parameter: the extraction can be only full or update'
    else:
        raise 'Wrong parameter: the extraction can be only full or update'
    
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
    gm = pipeline_manager.pipelineManager(parameters['mode'], parameters['verbose'])
    gm.manage()
    
if __name__ == "__main__":
    main()