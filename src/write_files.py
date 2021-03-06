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

'''
Module that manages the writing of files
It has been created to be sure that the resources allocated for this operation 
can be freed just after the operation is complete
'''

import os
import inspect

import settings
from global_functions import printmsg
from errors import GenericError

class WriteFile(object):
    """Class that writes the output files of the pipeline"""
    
    def __init__(self, dirname, verbose):
        """Constructor"""
        #I set the directory where to write
        self.dirname = dirname
        self.verbose = verbose
    
    def write_bibcodes_to_delete_file(self, xmlstring, bibcodes_list, extraction_name):
        """method that writes the file with the bibcodes to delete and updates the file with the done bibcodes"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        #I build the complete path and filename for the file to extract
        filename = settings.BIBCODE_TO_DELETE_OUT_NAME + '_'+ extraction_name + '.xml'
        filepath = os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, filename)
        
        printmsg(self.verbose, "Writing the MarcXML file %s \n" % filepath) 
        #then I actually write the file
        try:
            file_obj = open(filepath,'w')
            file_obj.write(xmlstring)
            file_obj.close()
        except:
            return False
        
        del file_obj, xmlstring
        
        #then I append the list of bibcodes actually written extracte to the "done file"
        bibdone_filename = os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, settings.BASE_FILES['done'])
        printmsg(self.verbose, 'Updating the "processed bibcodes" file %s \n' % bibdone_filename) 
        try:
            file_obj = open(bibdone_filename, 'a')
            for bibcode in bibcodes_list:
                file_obj.write(bibcode+'\n')
            file_obj.close()
        except:
            raise GenericError('Impossible to write in the "bibcode done file" %s \n' % bibdone_filename)
        
        del file_obj, bibcodes_list
        
        return filepath

    def write_marcxml_file(self, xmlstring, taskname, extraction_name):
        """method that writes the marcXML to a file naming it in the proper way"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        filename = settings.MARCXML_FILE_BASE_NAME + '_' + extraction_name + '_'+ taskname + '.xml'
        filepath = os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, filename)
        
        printmsg(self.verbose, "Writing the MarcXML file %s \n" % filepath) 
        #then I actually write the file
        try:
            file_obj = open(filepath,'w')
            file_obj.write(xmlstring)
            file_obj.close()
        except:
            return False
        
        del file_obj, xmlstring

        return filepath
    
    def write_done_bibcodes_to_file(self, bibcodes_list):
        """Method that writes a list of bibcodes in the file of the done bibcodes"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        filepath = os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, settings.BASE_FILES['done'])
        
        try:
            file_obj = open(filepath, 'a')
            for bibcode in bibcodes_list:
                file_obj.write(bibcode+'\n')
            file_obj.close()
        except:
            raise GenericError('Impossible to write in the "bibcode done file" %s \n' % filepath)

        return True
    
    def write_problem_bibcodes_to_file(self, bibcodes_list):
        """Method that writes a list of bibcodes in the file of the done bibcodes"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        filepath = os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, settings.BASE_FILES['prob'])
        
        try:
            file_obj = open(filepath, 'a')
            for bibcode in bibcodes_list:
                file_obj.write(bibcode+'\n')
            file_obj.close()
        except:
            raise GenericError('ERROR: impossible to write in the "bibcode problematic file" %s \n' % filepath)

        return True 

