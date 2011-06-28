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
    
    return parameters

def main():
    """ Main Function"""
    
    #Manage parameters
    parameters = parse_parameters()
    
    #I call the global manager
    gm = pipeline_manager.pipelineManager(parameters['mode'])
    gm.manage()
    
if __name__ == "__main__":
    main()