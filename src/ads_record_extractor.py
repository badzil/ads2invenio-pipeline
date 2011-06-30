'''
The manager is the leading process for the extraction

It takes in input a list of bibcodes

then it splits the list in multiple groups sized according to the settings

these groups are put in a "to process queue"

different processes will take a group each from the "to process queue" and they will extract the bibcodes assigned
after the extraction they will insert the processed bibcodes in an unique "processed queue"

finally a last process will take the processed bibcodes and will write them to the proper file

This class uses multiprocessing, so it is compatible only with python 2.6+
'''

import sys
import inspect
import multiprocessing
import libxml2

import settings


class ADSRecordExtractor(object):
    """Class that manages the actual extraction of the record from ADS to MarcXML"""
    
    def __init__(self, bibcodes_to_extract_list, bibcodes_to_delete_list):
        """Constructor"""
        self.bibcodes_to_extract_list = bibcodes_to_extract_list
        self.bibcodes_to_extract_list.sort()
        self.bibcodes_to_delete_list = bibcodes_to_delete_list
        self.bibcodes_to_delete_list.sort()
        
    def extract(self):
        """manager of the extraction"""
        if settings.DEBUG:
            sys.stdout.write("In function %s \n" % inspect.stack()[0][3]) 
        
        #I have to upload first the bibcodes to delete and then the others.
        #So I process them first
        try:
            self.process_bibcodes_to_delete()
        except Exception:
            sys.stdout.write("Unable to process the bibcodes to delete \n")
            raise
        
        #I define a queue
        #q = multiprocessing.Queue()
        
        
    def process_bibcodes_to_delete(self):
        """method that creates the MarcXML for the bibcodes to delete"""
        if settings.DEBUG:
            sys.stdout.write("In function %s \n" % inspect.stack()[0][3]) 
        
        #I create an unique file for all the bibcodes to delete: 
        #I don't think it's necessary to split the content in groups, since the XML is really simple
            
        #I create the base object for the tree 
        doc = libxml2.newDoc("1.0")
        root = doc.newChild(None, "collection", None)
        
        #then for each bibcode to delete I create the proper record
        for bibcode in self.bibcodes_to_delete_list:
            record = root.newChild(None, 'record', None)
            #I add to the record the 2 necessary datafields
            d970 = record.newChild(None, 'datafield', None)
            d970.setProp('tag', '970')
            d970.setProp('ind1', '')
            d970.setProp('ind1', '')
            #I create the subfield tag
            sub = d970.newChild(None, 'subfield', bibcode)
            sub.setProp("code", "a")
            d980 = record.newChild(None, 'datafield', None)
            d980.setProp('tag', '980')
            d980.setProp('ind1', '')
            d980.setProp('ind1', '')
            #I create the subfield tag
            sub = d980.newChild(None, 'subfield', "DELETED")
            sub.setProp("code", "c")
                    
        #I extract the node
        marcxml_string = doc.serialize('UTF-8', 2)
        #I remove the data
        doc.freeDoc()
        del doc
        
        print marcxml_string
        
        
        
        
        
        