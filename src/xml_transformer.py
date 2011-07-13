""" Class that define an engine for XSLT transformations

"""

#libraries to transform the xml
import libxml2
import libxslt
import inspect 

import settings
from global_functions import printmsg

class xmlTransformer(object):
    """ Class that transform an ADS xml in MarcXML"""
        
    def __init__(self, verbose):
        """ Constructor"""
        self.verbose = verbose
        #definition of the stilesheet
        self.stylesheet = settings.STYLESHEET_PATH
    
    def init_stylesheet(self):
        """ Method that initialize the transformation engine """
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        #create the stylesheet obj
        try:
            self.style_obj = libxslt.parseStylesheetDoc(libxml2.parseFile(self.stylesheet))
        except:
            raise "ERROR: problem loading stylesheet \n"
        
        return True
    
    def transform(self, doc):
        """ Method that actually make the transformation"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        #I load the stylesheet
        self.init_stylesheet()
                
        #transformation
        try:
            doc = self.style_obj.applyStylesheet(doc, None)
        except:
            printmsg(True, "ERROR: Transformation failed \n") 
            return False
        
        #to string
        result = self.style_obj.saveResultToString(doc)
        
        #self.styleObj.freeStylesheet()
        doc.freeDoc()
        
        return result
    
