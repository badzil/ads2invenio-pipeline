'''
The manager is the leading process for the extraction

It takes in input a list of bibcodes

then it splits the list in multiple groups sized according to the settings

these groups are put in a "to process queue"

different processes will take a group each from the "to process queue" and they will extract the bibcodes assigned
after the extraction they will insert the processed bibcodes in an unique "processed queue"

finally a last process will take the processed bibcodes and will write them to the proper file
'''

class ADSRecordExtractor(object):
    """"""