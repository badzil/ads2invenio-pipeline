""" Class that define an engine for XSLT transformations

"""

#libraries to transform the xml
import libxml2
import libxslt
import inspect
import sys 

import settings

class xmlTransformer(object):
    """ Class that transform an ADS xml in MarcXML"""
        
    def __init__(self):
        """ Constructor"""
        #definition of the stilesheet
        self.stylesheet = settings.STYLESHEET_PATH
    
    def init_stylesheet(self):
        """ Method that initialize the transformation engine """
        #create the stylesheet obj
        try:
            self.style_obj = libxslt.parseStylesheetDoc(libxml2.parseFile(self.stylesheet))
        except:
            sys.stdout.write("ERROR: problem loading stylesheet \n") 
            return False
        return True
    
    def transform(self, doc):
        """ Method that actually make the transformation"""
        if settings.DEBUG:
            sys.stdout.write("In function %s \n" % inspect.stack()[0][3])
        
        if self.init_stylesheet():
            return False
        
        #transformation
        try:
            doc = self.style_obj.applyStylesheet(doc, None)
        except:
            sys.stdout.write("ERROR: Transformation failed \n") 
            return False
        
        #to string
        result = self.style_obj.saveResultToString(doc)
        
        #self.styleObj.freeStylesheet()
        doc.freeDoc()
        
        return result
    
