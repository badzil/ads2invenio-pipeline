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
sys.path.append('/proj/ads/soft/python/lib/site-packages')

import inspect
import multiprocessing
import libxml2
import itertools
import time

import ads.ADSExports_libxml2

import settings
import write_files
import xml_transformer


class ADSRecordExtractor(object):
    """Class that manages the actual extraction of the record from ADS to MarcXML"""
    
    def __init__(self, bibcodes_to_extract_list, bibcodes_to_delete_list, extraction_directory):
        """Constructor"""
        self.bibcodes_to_extract_list = bibcodes_to_extract_list
        #the bibcodes to extract MUST NOT be sorted
        self.bibcodes_to_delete_list = bibcodes_to_delete_list
        self.bibcodes_to_delete_list.sort()
        self.extraction_directory = extraction_directory
        
    def extract(self):
        """manager of the extraction"""
        if settings.DEBUG:
            sys.stdout.write("In function %s \n" % inspect.stack()[0][3]) 
        
        ########################################################################
        #part where the bibcode to delete are processed
        
        #I have to upload first the bibcodes to delete and then the others.
        #So I process them first
        if self.bibcodes_to_delete_list:
            try:
                self.process_bibcodes_to_delete()
            except Exception:
                sys.stdout.write("Unable to process the bibcodes to delete \n")
                raise
        
        ########################################################################
        #part where the bibcode to extract (new or update) are processed
        
        #a queue for the bibcodes to process
        q_todo = multiprocessing.Queue()
        #a queue for the bibcodes processed
        q_done = multiprocessing.Queue()
        #a queue for the bibcodes with problems
        q_probl = multiprocessing.Queue()
        #a lock to write in stdout
        lock_stdout = multiprocessing.Lock()
        
        #I split the list of bibcodes to process in multiple groups
        bibtoprocess_splitted = self.grouper(settings.NUMBER_OF_BIBCODES_PER_GROUP, self.bibcodes_to_extract_list)

        #I split all the bibcodes in groups of NUMBER_OF_BIBCODES_PER_GROUP and I put them in the todo queue
        counter = 0 #I need the counter to uniquely identify each group
        for grp in bibtoprocess_splitted:
            counter += 1
            q_todo.put([str(counter).zfill(7), grp])
        
        #I define the number of processes to run
        number_of_processes = settings.NUMBER_WORKERS #in production should be a part of multiprocessing.cpu_count 
        
        #I define the worker processes
        processes = [multiprocessing.Process(target=extractor_process, args=(q_todo, q_done, q_probl, lock_stdout, self.extraction_directory)) for i in range(number_of_processes)]
        
        #I append to the todo queue a list of commands to stop the worker processes
        for i in range(number_of_processes):
            q_todo.put(['STOP', ''])
        
        #I define a "done bibcode" worker
        donebib = multiprocessing.Process(target=done_extraction_process, args=(q_done, number_of_processes, lock_stdout, self.extraction_directory))
        #I define a "problematic bibcode" worker
        problbib = multiprocessing.Process(target=problematic_extraction_process, args=(q_probl, number_of_processes, lock_stdout, self.extraction_directory))
            
        #I start the worker processes
        for p in processes:
            p.start()
        #and the output handlers
        donebib.start()
        problbib.start()
        
        #I join all the processes
        for p in processes:
            p.join()
        donebib.join()
        problbib.join()
        
        #print '####################### GETTING RESULTS'
        #for i in range(len(bibtoprocess_splitted)):
        #    print q_done.get()
        
        sys.stdout.write("Extraction ended! \n") 
        
    
    def grouper(self, n, iterable):
        """method to split a list in multiple groups"""
        args = [iter(iterable)] * n
        return list(([e for e in t if e != None] for t in itertools.izip_longest(*args)))
        
        
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
            sub = d970.newChild(None, 'subfield', bibcode.replace('&', '&amp;'))
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
        
        #I write to the file
        w2f = write_files.writeFile(self.extraction_directory)
        filename_delete = w2f.write_bibcodes_to_delete_file(marcxml_string, self.bibcodes_to_delete_list)
        
        if filename_delete:
            if settings.DEBUG:
                sys.stdout.write("The MarcXML for the bibcode to delete has been written to the file %s \n" % filename_delete)
        else:
            raise "ERROR: Impossible to create the file for the MarcXML of the bibcodes to delete"
        
        return True
        
        
        
def extractor_process(q_todo, q_done, q_probl, lock_stdout, extraction_directory):
    """Worker function for the extraction of bibcodes from ADS
        it has been defined outside any class because it's more simple to treat with multiprocessing """
    
    #while there is something to process I try to process
    while (True):
                
        task_todo = q_todo.get()
        if task_todo[0] == 'STOP':
            break
        
        #I print when I'm startring the extraction
        lock_stdout.acquire()
        sys.stdout.write(multiprocessing.current_process().name + (' (worker) starting to process group %s at %s \n' % (task_todo[0], time.strftime("%Y-%m-%d %H:%M:%S"))))  
        lock_stdout.release() 
        
        ############
        #then I process the bibcodes
        # I define a couple of lists where to store the bibcodes processed
        bibcodes_ok = []
        bibcodes_probl = []
        
        #I define a ADSEXPORT object
        recs = ads.ADSExports_libxml2.ADSRecords('full', 'XML')
        
        for bibcode in task_todo[1]:
            try:
                recs.addRecord(bibcode)
                bibcodes_ok.append(bibcode)
            except:
                sys.stdout.write('ERROR: problem retrieving the bibcode "%s" \n' % bibcode)
                bibcodes_probl.append(bibcode)
        
        #I extract the object I created
        xmlobj = recs.export()
        del recs
        
        try:
            #I define a transformation object
            tr = xml_transformer.xmlTransformer()
            #and I transform my object
            marcXML = tr.transform(xmlobj)
        except:
            raise 'ERROR: Impossible to create a transformation object!'
        
        #if the transformation was ok, I write the file
        if marcXML:
            w2f = write_files.writeFile(extraction_directory)
            wrote_filename = w2f.write_marcXML_file(marcXML, task_todo[0])
            #if the writing of the xml is wrong I consider all the bibcodes problematic
            if not wrote_filename:
                bibcodes_probl = bibcodes_probl + bibcodes_ok
                bibcodes_ok = []
        #otherwise I put all the bibcodes in the problematic
        else:
            bibcodes_probl = bibcodes_probl + bibcodes_ok
            bibcodes_ok = []
        
        #finally I pass to the done bibcodes to the proper file    
        q_done.put([task_todo[0], bibcodes_ok, wrote_filename])
        #and the problematic bibcodes
        q_probl.put([task_todo[0], bibcodes_probl])
             
        lock_stdout.acquire()
        sys.stdout.write(multiprocessing.current_process().name + (' (worker) finished to process group %s at %s \n' % (task_todo[0], time.strftime("%Y-%m-%d %H:%M:%S"))))  
        lock_stdout.release() 
    
    #I tell the output processes that I'm done
    q_done.put(['WORKER DONE'])
    q_probl.put(['WORKER DONE'])
        
    lock_stdout.acquire()
    sys.stdout.write(multiprocessing.current_process().name + ' (worker) job finished: exiting \n')  
    lock_stdout.release()    
        


def done_extraction_process(q_done, num_active_workers, lock_stdout, extraction_directory):
    """Worker that takes care of the groups of bibcodes processed and writes the bibcodes to the related file
        NOTE: this can be also the process that submiths the upload processes to invenio
    """
    while(True):
        group_done = q_done.get()
        
        #first of all I check if the group I'm getting is a message from a process that finished
        if group_done[0] == 'WORKER DONE':
            num_active_workers = num_active_workers - 1
            #if there are no active worker any more, I'm done with processing output
            if num_active_workers == 0:
                break
        else:    
            #otherwise I process the output:
            # I puth the bibcodes in the file of the done bibcodes
            if len(group_done[1]) > 0:
                w2f = write_files.writeFile(extraction_directory)
                w2f.write_done_bibcodes_to_file(group_done[1])
                
                lock_stdout.acquire()
                sys.stdout.write(multiprocessing.current_process().name + (' (done bibcodes worker) wrote done bibcodes for group %s \n' % group_done[0]))  
                lock_stdout.release()
                
            # I call the procedure to submit to invenio the process to upload the file
            filename_path = group_done[2]
            
            
    lock_stdout.acquire()
    sys.stdout.write(multiprocessing.current_process().name + ' (done bibcodes worker) job finished: exiting \n')  
    lock_stdout.release()
            

def problematic_extraction_process(q_probl, num_active_workers, lock_stdout, extraction_directory):
    """Worker that takes care of the bibcodes that couldn't be extracted and writes them to the related file"""

    while(True):
        group_probl = q_probl.get()
        
        #first of all I check if the group I'm getting is a message from a process that finished
        if group_probl[0] == 'WORKER DONE':
            num_active_workers = num_active_workers - 1
            #if there are no active worker any more, I'm done with processing output
            if num_active_workers == 0:
                break
        else:
            #otherwise I process the output:
            # I puth the bibcodes in the file of the problematic bibcodes
            if len(group_probl[1]) > 0:
                w2f = write_files.writeFile(extraction_directory)
                w2f.write_problematic_bibcodes_to_file(group_probl[1])
                
                lock_stdout.acquire()
                sys.stdout.write(multiprocessing.current_process().name + (' (problematic bibcodes worker) wrote problematic bibcodes for group %s \n' % group_probl[0]))  
                lock_stdout.release()
            
    lock_stdout.acquire()
    sys.stdout.write(multiprocessing.current_process().name + ' (problematic bibcodes worker) job finished: exiting \n')  
    lock_stdout.release()
        
        