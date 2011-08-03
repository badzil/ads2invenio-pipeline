# Copyright (C) 2011, The SAO/NASA Astrophysics Data System
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Class that define an engine for XSLT transformations

"""

#libraries to transform the xml
import libxml2
import libxslt
import inspect 

import settings
from global_functions import printmsg
from errors import GenericError

class XmlTransformer(object):
    """ Class that transform an ADS xml in MarcXML"""
        
    def __init__(self, verbose):
        """ Constructor"""
        self.verbose = verbose
        #definition of the stilesheet
        self.stylesheet = settings.STYLESHEET_PATH
        #I initialize the style sheet object
        self.style_obj = None
    
    def init_stylesheet(self):
        """ Method that initialize the transformation engine """
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        #create the stylesheet obj
        try:
            self.style_obj = libxslt.parseStylesheetDoc(libxml2.parseFile(self.stylesheet))
        except:
            raise GenericError("ERROR: problem loading stylesheet \n")
        
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
    
