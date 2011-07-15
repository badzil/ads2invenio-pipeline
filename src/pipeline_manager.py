'''
It checks the situation of the latest extraction
if the latest extraction is ok or if there is no extraction I run a new complete extraction (that can be full or an update)
if the last extraction failed, I start again where I stopped the last time

if there has to be a new extraction, I create a new folder with the new four files:
1- the bibcodes to parse (new or modification)
2- the bibcodes to parse (delete)
3- the parsed bibcodes
4- the bibcodes that gave problems during the extraction
then I write the bibcodes to extract in the proper file

Finally I lunch the manager with the entire list of bibcodes to extract

'''

import os
import sys
from time import strftime
import inspect
import shutil

import settings
import ads_record_extractor
from global_functions import printmsg
from errors import GenericError

class pipelineManager(object):
    """Class that manages the extraction of bibcodes from ADS"""
    def __init__(self, mode, verbose):
        """Constructor"""
        self.mode = mode
        self.verbose = verbose
    
    def manage(self):
        """public function"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3])) 

        #If there is a wrong mode, I will raise an exception
        if self.mode != 'full' and self.mode != 'update':
            raise GenericError('Wrong parameter: the extraction can be only full or update')
        #otherwise I proceed
        else:
            #retrieve the list of bibcode to extract and the list of bibcodes to delete
            (bibcodes_to_extract_list, bibcodes_to_delete_list) = self.retrieve_bibcodes_to_extract()
            #call the extractor manager
            are = ads_record_extractor.ADSRecordExtractor(bibcodes_to_extract_list, bibcodes_to_delete_list, self.dirname, self.verbose)
            del bibcodes_to_extract_list
            del bibcodes_to_delete_list
            are.extract()
            
            return
            
    def retrieve_bibcodes_to_extract(self):
        """method that retrieves the bibcodes that need to be extracted from ADS"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        #check the status of the last extraction
        status_last_extraction = self.check_last_extraction()
        
        if status_last_extraction == 'OK' or status_last_extraction == 'NOTHING FOUND' or status_last_extraction == 'NOT VALID DIRECTORY CONTENT':
            printmsg(self.verbose, "Last extraction was fine: proceeding with a new one \n")
            #I create directory and files of bibcodes to extract
            self.dirname = strftime("%Y_%m_%d-%H_%M_%S")
            os.mkdir(os.path.join(settings.BASE_OUTPUT_PATH, self.dirname), 0755)
            for filetype in settings.BASE_FILES:
                fileobj = open(os.path.join(os.path.join(settings.BASE_OUTPUT_PATH, self.dirname), settings.BASE_FILES[filetype]),'w')
                fileobj.write('')
                fileobj.close()
            # I write also the file to log the extraction name
            fileobj = open(os.path.join(os.path.join(settings.BASE_OUTPUT_PATH, self.dirname), settings.EXTRACTION_FILENAME_LOG),'w')
            fileobj.write('')
            fileobj.close()
            del fileobj
            #then I extract the list of bibcodes according to "mode"
            if self.mode == 'full':
                #if node == full I have to extrat all the bibcodes
                return self.extract_full_list_of_bibcodes()
            elif self.mode == 'update':
                return self.extract_update_list_of_bibcodes()
        else:
            printmsg(self.verbose, "Last extraction was not fine: recovering \n")
            #I retrieve the bibcodes missing from the last extraction
            self.dirname = self.lastest_extr_dir
            return self.remaining_bibcode_to_extract_delete(os.path.join(settings.BASE_OUTPUT_PATH, self.lastest_extr_dir))
            
            
    def check_last_extraction(self):
        """method that checks if the last extraction finished properly"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
            
        #I retrieve the list of entries in the output directory
        list_of_elements = os.listdir(settings.BASE_OUTPUT_PATH)
        #I extract only the directories
        directories = []
        for elem in list_of_elements:
            if os.path.isdir(os.path.join(settings.BASE_OUTPUT_PATH, elem)):
                directories.append(elem)
        
        #I set a variable for the latest dir of extraction
        self.lastest_extr_dir = ''
        
        #if I don't have any result I return the proper status
        if len(directories) == 0:
            printmsg(self.verbose, "Checked last extraction: status returned NOTHING FOUND \n")
            return 'NOTHING FOUND'
        else: 
            #I sort the directories in desc mode and I take the first one
            directories.sort(reverse=True)
            self.lastest_extr_dir = directories[0]
            
            printmsg(self.verbose, "Checking the directory %s \n" % os.path.join(settings.BASE_OUTPUT_PATH, self.lastest_extr_dir))
            
            #I extract the content of the last extraction
            elements_from_last_extraction = os.listdir(os.path.join(settings.BASE_OUTPUT_PATH, self.lastest_extr_dir))
            
            #then I check if all the mandatory files are there, otherwise
            for name in settings.BASE_FILES:
                if settings.BASE_FILES[name] not in elements_from_last_extraction:
                    printmsg(self.verbose, "Checked last extraction: status returned NOT VALID DIRECTORY CONTENT \n")
                    return 'NOT VALID DIRECTORY CONTENT'
            del name
        
            #if I pass all this checks the content is basically fine
            #But then I have to check if the lists of bibcodes are consistent: bibcodes extracted + bibcodes with problems = sum(bibcodes to extract)
            printmsg(self.verbose, "Checking if the list of bibcodes actually extracted is equal to the one I had to extract \n")
            bibcodes_still_pending = self.extract_diff_bibcodes_from_extraction(os.path.join(settings.BASE_OUTPUT_PATH, self.lastest_extr_dir))
            if len(bibcodes_still_pending) == 0:
                printmsg(self.verbose, "All the bibcodes from the last extraction have been processed \n")
            else:
                printmsg(self.verbose, "Checked last extraction: status returned LATEST NOT ENDED CORRECTLY \n")
                return 'LATEST NOT ENDED CORRECTLY'
        
        #if everything is Ok I return it
        printmsg(self.verbose, "Checked last extraction: status returned OK \n")
        return 'OK'

    def extract_full_list_of_bibcodes(self):
        """ method that extracts the complete list of bibcodes
            it first extracts the list of arxiv bibcodes and then all the others
        """
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
            
        #first I extract the list of preprint
        preprint_bibcodes = self.read_bibcode_file(settings.BIBCODES_PRE)
        #I copy the preprint file, because I need a copy locally
        try:
            shutil.copy(settings.BIBCODES_PRE, os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, 'PRE_'+os.path.basename(settings.BIBCODES_PRE)))
        except:
            raise GenericError('Impossible to copy a mandatory file from %s to %s' % (settings.BIBCODES_PRE, os.path.join(settings.BASE_OUTPUT_PATH, self.dirname)))
        #then I extract the complete list
        all_bibcodes = self.read_bibcode_file(settings.BIBCODES_ALL)
        not_pre_bibcodes = list(set(all_bibcodes) - set(preprint_bibcodes))
        not_pre_bibcodes.sort()
        
        #I write these lists bibcodes to the file of bibcodes to extract
        #and in the meanwhile I create the list with first the preprint and then the published
        bibcode_file = open(os.path.join(settings.BASE_OUTPUT_PATH, self.dirname, settings.BASE_FILES['new']), 'a')
        bibcode_to_extract = []
        #first the preprints because they can be overwritten by the published ones
        for bibcode in preprint_bibcodes:
            bibcode_file.write(bibcode + '\n')
            bibcode_to_extract.append(bibcode)
        #then all the other bibcodes
        for bibcode in not_pre_bibcodes:
            bibcode_file.write(bibcode + '\n')
            bibcode_to_extract.append(bibcode)
        bibcode_file.close()
        del bibcode
        del bibcode_file
        
        printmsg(self.verbose, "Full list of bibcodes and related file generated \n")
        #finally I return the full list of bibcodes and an empty list for the bibcodes to delete
        return (bibcode_to_extract, [])

    def extract_update_list_of_bibcodes(self):
        """Method that extracts the list of bibcodes to update"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        #I return the list of bibcodes to extract and the list of bibcodes to delete
        return ([],[])
    
    def extract_diff_bibcodes_from_extraction(self, extraction_dir):
        """method that extracts the list of bibcodes not processed from a directory used for an extraction"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3])) 
        #first I extract the list of bibcodes that I had to extract
        bibcodes_to_extract = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['new']))
        #then the ones I had to delete
        bibcodes_to_delete = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['del']))
        #then the ones that had problems during the extraction
        bibcodes_probl = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['prob']))
        #finally the ones that have been extracted correctly
        bibcodes_done = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['done']))
        #then I extract the ones remaining
        bibcodes_remaining = list((set(bibcodes_to_extract).union(set(bibcodes_to_delete))) - (set(bibcodes_probl).union(set(bibcodes_done))))
        return bibcodes_remaining
                   
        
    def remaining_bibcode_to_extract_delete(self, extraction_dir):
        """method that finds the bibcodes to extract and to delete not processed in an extraction """
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        #first I extract the list of bibcodes that I had to extract
        bibcodes_to_extract = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['new']))
        #then the ones I had to delete
        bibcodes_to_delete = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['del']))
        #then the ones that had problems during the extraction
        bibcodes_probl = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['prob']))
        #finally the ones that have been extracted correctly
        bibcodes_done = self.read_bibcode_file(os.path.join(extraction_dir, settings.BASE_FILES['done']))
        
        bibcode_processed = list(set(bibcodes_probl).union(set(bibcodes_done)))
        #then I find the ones remaining to extract
        bibcodes_to_extract_remaining = list(set(bibcodes_to_extract) - set(bibcode_processed))
        #then I find the ones remaining to delete
        bibcodes_to_delete_remaining = list(set(bibcodes_to_delete) - set(bibcode_processed))
        
        #now I want the list of extraction  ordered with first the preprint and then the other bibcodes
        #only if I have something remaining
        if len(bibcodes_to_extract_remaining) > 0:
            #I load the saved preprint file 
            bibcodes_preprint =  self.read_bibcode_file(os.path.join(settings.BASE_OUTPUT_PATH, extraction_dir, 'PRE_'+os.path.basename(settings.BIBCODES_PRE)))
            remaining_preprint = list(set(bibcodes_to_extract_remaining).intersection(set(bibcodes_preprint)))
            remaining_preprint.sort()
            other_remaining = list(set(bibcodes_to_extract_remaining) - set(remaining_preprint))
            other_remaining.sort()
            bibcodes_to_extract_remaining =  remaining_preprint + other_remaining
        
        return (bibcodes_to_extract_remaining, bibcodes_to_delete_remaining)
        
    
    def read_bibcode_file(self, bibcode_file_path):
        """ Function that read the list of bibcodes in one file:
            The bibcodes must be at the beginning of a row.
        """
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        printmsg(self.verbose, "Reading %s \n" % bibcode_file_path)
        try:
            bibfile = open(bibcode_file_path, "rU")
        except IOError:
            sys.stdout.write("Input file not readable \n")
            raise GenericError('Mandatory file not readable. Please check %s \n' % bibcode_file_path)
        
        bibcodes_list = []
        
        for bibrow in bibfile:
            if bibrow[0] != " ":
                bibrow_elements =  bibrow.split('\t')
                bibcode = bibrow_elements[0].rstrip('\n')
                if bibcode != '':
                    bibcodes_list.append(bibcode)
        
        bibfile.close()
        del bibfile
        #return the list of bibcodes        
        return bibcodes_list




