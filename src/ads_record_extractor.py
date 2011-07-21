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
import os

import ads.ADSExports_alternative

import settings
import write_files
import xml_transformer
from global_functions import printmsg
from errors import GenericError


class ADSRecordExtractor(object):
    """Class that manages the actual extraction of the record from ADS to MarcXML"""
    
    def __init__(self, bibcodes_to_extract_list, bibcodes_to_delete_list, extraction_directory, verbose):
        """Constructor"""
        self.verbose = verbose
        self.bibcodes_to_extract_list = bibcodes_to_extract_list
        #the bibcodes to extract MUST NOT be sorted
        self.bibcodes_to_delete_list = bibcodes_to_delete_list
        self.bibcodes_to_delete_list.sort()
        self.extraction_directory = extraction_directory
        #I extract or generate the extraction name
        self.extraction_name = self.set_extraction_name()
        
    def extract(self):
        """manager of the extraction"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3])) 

        ########################################################################
        #part where the bibcode to delete are processed
        
        #I have to upload first the bibcodes to delete and then the others.
        #So I process them first
        if self.bibcodes_to_delete_list:
            try:
                self.process_bibcodes_to_delete()
            except Exception:
                printmsg(True, "Unable to process the bibcodes to delete \n")
                raise GenericError("Unable to process the bibcodes to delete \n")
        
        ########################################################################
        #part where the bibcode to extract (new or update) are processed
        
        #I split the list of bibcodes to process in multiple groups
        bibtoprocess_splitted = self.grouper(settings.NUMBER_OF_BIBCODES_PER_GROUP, self.bibcodes_to_extract_list)

        #I define a manager for the workers
        manager = multiprocessing.Process(target=extractor_manager_process, args=(bibtoprocess_splitted, self.extraction_directory, self.extraction_name, self.verbose))        
        #I start the process
        manager.start()
        #I join the process
        manager.join()
        
        printmsg(True, "Extraction ended! \n") 
        
    
    def grouper(self, n, iterable):
        """method to split a list in multiple groups"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        args = [iter(iterable)] * n
        return list(([e for e in t if e != None] for t in itertools.izip_longest(*args)))
        
        
    def process_bibcodes_to_delete(self):
        """method that creates the MarcXML for the bibcodes to delete"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
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
        w2f = write_files.WriteFile(self.extraction_directory, self.verbose)
        filename_delete = w2f.write_bibcodes_to_delete_file(marcxml_string, self.bibcodes_to_delete_list, self.extraction_name)
        
        if filename_delete:
            printmsg(self.verbose, "The MarcXML for the bibcode to delete has been written to the file %s \n" % filename_delete)
        else:
            raise GenericError("Impossible to create the file for the MarcXML of the bibcodes to delete")
        
        return True
    
    def set_extraction_name(self):
        """Method that sets the name of the current extraction"""
        printmsg(self.verbose, "In function %s.%s \n" % (self.__class__.__name__, inspect.stack()[0][3]))
        
        filepath = os.path.join(settings.BASE_OUTPUT_PATH, self.extraction_directory, settings.EXTRACTION_FILENAME_LOG)
        file_obj = open(filepath,'r')
        rows = file_obj.readlines()
        file_obj.close()
        if len(rows) > 0:
            last_name =  rows[len(rows) - 1]
            number_ext = int(last_name.split(settings.EXTRACTION_BASE_NAME)[1])
            number_ext = number_ext + 1
        else:
            last_name = None
            number_ext = 1
        
        extraction_name = settings.EXTRACTION_BASE_NAME + str(number_ext)  
        #Then I write the number of extraction to the file
        file_obj = open(filepath,'a')
        file_obj.write(extraction_name + '\n')
        file_obj.close()
        
        return extraction_name


def extractor_manager_process(bibtoprocess_splitted, extraction_directory, extraction_name, verbose):
    """Process that takes care of managing all the other worker processes
        this process also creates new worker processes when the existing ones reach the maximum number of groups of bibcode to process 
    """
    #a queue for the bibcodes to process
    q_todo = multiprocessing.Queue()
    #a queue for the bibcodes processed
    q_done = multiprocessing.Queue()
    #a queue for the bibcodes with problems
    q_probl = multiprocessing.Queue()
    #a lock to write in stdout
    lock_stdout = multiprocessing.Lock()
    #a queue for the messages from the workers that have to tell the manager when they reach the maximum number of chunks to process
    q_life = multiprocessing.Queue()
    
    lock_stdout.acquire()
    printmsg(verbose, multiprocessing.current_process().name + ' (Manager) Filling the queue with the tasks \n')  
    lock_stdout.release()
    
    #I split all the bibcodes in groups of NUMBER_OF_BIBCODES_PER_GROUP and I put them in the todo queue
    counter = 0 #I need the counter to uniquely identify each group
    for grp in bibtoprocess_splitted:
        counter += 1
        q_todo.put([str(counter).zfill(7), grp])
    
    lock_stdout.acquire()
    printmsg(verbose, multiprocessing.current_process().name + ' (Manager) Creating the first pool of workers \n')  
    lock_stdout.release()
    
    #I define the number of processes to run
    number_of_processes = settings.NUMBER_WORKERS #in production should be a part of multiprocessing.cpu_count 
    
    #I define the worker processes
    processes = [multiprocessing.Process(target=extractor_process, args=(q_todo, q_done, q_probl, lock_stdout, q_life, extraction_directory, extraction_name, verbose)) for i in range(number_of_processes)]
    
    #I append to the todo queue a list of commands to stop the worker processes
    for i in range(number_of_processes):
        q_todo.put(['STOP', ''])
    
    lock_stdout.acquire()
    printmsg(verbose, multiprocessing.current_process().name + ' (Manager) Creating the output workers \n')  
    lock_stdout.release()
    
    #I define a "done bibcode" worker
    donebib = multiprocessing.Process(target=done_extraction_process, args=(q_done, number_of_processes, lock_stdout, q_life, extraction_directory, verbose))
    #I define a "problematic bibcode" worker
    problbib = multiprocessing.Process(target=problematic_extraction_process, args=(q_probl, number_of_processes, lock_stdout, q_life, extraction_directory, verbose))
    
    lock_stdout.acquire()
    printmsg(verbose, multiprocessing.current_process().name + ' (Manager) Starting all the workers \n')  
    lock_stdout.release()
        
    #I start the worker processes
    for p in processes:
        p.start()
    #and the output handlers
    donebib.start()
    problbib.start()
    
    #I join all the processes
    #for p in processes:
    #    p.join()
    #donebib.join()
    #problbib.join()
    
    #then I have to wait for the workers that have to tell me if they reached the maximum amount of chunk to process or if the extraction ended
    #in the first case I have to start another process
    #in the second I have to decrease the counter of active workers
    active_workers = settings.NUMBER_WORKERS
    additional_workers = 2
    while active_workers > 0 or additional_workers > 0:
        #I get the message from the worker
        death_reason = q_life.get()
        #if the reason of the death is that the process reached the max number of groups to process, then I have to start another one
        if death_reason[0] == 'MAX LIFE REACHED':
            newprocess = multiprocessing.Process(target=extractor_process, args=(q_todo, q_done, q_probl, lock_stdout, q_life, extraction_directory, extraction_name, verbose))
            newprocess.start()
            additional_workers = additional_workers - 1
            lock_stdout.acquire()
            printmsg(True, multiprocessing.current_process().name + ' (Manager) New worker created \n')  
            lock_stdout.release()
        elif death_reason[0] == 'QUEUE EMPTY':
            active_workers = active_workers - 1
            lock_stdout.acquire()
            printmsg(verbose, multiprocessing.current_process().name + ' (Manager) %s workers waiting to finish their job \n' % str(active_workers))  
            lock_stdout.release()
        elif death_reason[0] == 'PROBLEMBIBS DONE':
            additional_workers = additional_workers - 1
            lock_stdout.acquire()
            printmsg(verbose, multiprocessing.current_process().name + ' (Manager) %s additional workers waiting to finish their job \n' % str(additional_workers))  
            lock_stdout.release()
        elif death_reason[0] == 'DONEBIBS DONE':
            additional_workers = additional_workers - 1
            lock_stdout.acquire()
            printmsg(verbose, multiprocessing.current_process().name + ' (Manager) %s additional workers waiting to finish their job \n' % str(additional_workers))  
            lock_stdout.release()
    
    lock_stdout.acquire()
    printmsg(verbose, multiprocessing.current_process().name + ' (Manager) All the workers are done. Exiting... \n')  
    lock_stdout.release()

       
def extractor_process(q_todo, q_done, q_probl, lock_stdout, q_life, extraction_directory, extraction_name, verbose):
    """Worker function for the extraction of bibcodes from ADS
        it has been defined outside any class because it's more simple to treat with multiprocessing """
    #I get the maximum number of groups I can process
    max_num_groups = settings.MAX_NUMBER_OF_GROUP_TO_PROCESS
    #variable used to know if I'm exiting because the queue is empty or because I reached the maximum number of groups to process
    queue_empty = False
      
    #while there is something to process or I reach the maximum number of groups I can process,  I try to process
    for grpnum in range(max_num_groups):
        
        task_todo = q_todo.get()
        if task_todo[0] == 'STOP':
            
            queue_empty = True
            #I exit the loop
            break
        
        #I print when I'm starting the extraction
        lock_stdout.acquire()
        printmsg(True, multiprocessing.current_process().name + (' (worker) starting to process group %s \n' % task_todo[0]))  
        lock_stdout.release() 
        
        ############
        #then I process the bibcodes
        # I define a couple of lists where to store the bibcodes processed
        bibcodes_ok = []
        bibcodes_probl = []
        
        #I define a ADSEXPORT object
        recs = ads.ADSExports_alternative.ADSRecords('full', 'XML')
        
        # I define a maximum amount of bibcodes I can skip per each cicle: the number of bibcodes per group / 10 (minimum 500)
        # if i skip more than this amount it means that there is something 
        # wrong with the access to the data and it's better to stop everything
        max_number_of_bibs_to_skip = max(settings.NUMBER_OF_BIBCODES_PER_GROUP / 10, 500)
        
        for bibcode in task_todo[1]:
            try:
                recs.addRecord(bibcode)
                bibcodes_ok.append(bibcode)
            except:
                printmsg(True, 'ERROR: problem retrieving the bibcode "%s" \n' % bibcode)
                bibcodes_probl.append(bibcode)
                max_number_of_bibs_to_skip = max_number_of_bibs_to_skip - 1
            #If i=I reach 0 It means that I skipped 1k bibcodes and probably there is a problem: so I simulate an exit for empty queue
            if max_number_of_bibs_to_skip == 0:
                break
        #I exit from both loops
        if max_number_of_bibs_to_skip == 0:
            lock_stdout.acquire()
            printmsg(True, multiprocessing.current_process().name + (' (worker) Detected possible error with ADS data access: skipped %s bibcodes in one group \n' % max(settings.NUMBER_OF_BIBCODES_PER_GROUP / 10, 500)))  
            lock_stdout.release()
            queue_empty = True
            break
        
        #I extract the object I created
        xmlobj = recs.export()
        del recs
        
        try:
            #I define a transformation object
            transf = xml_transformer.XmlTransformer(verbose)
            #and I transform my object
            marcxml = transf.transform(xmlobj)
        except:
            raise GenericError('Impossible to transform the XML!')
        
        #if the transformation was ok, I write the file
        if marcxml:
            w2f = write_files.WriteFile(extraction_directory, verbose)
            wrote_filename = w2f.write_marcxml_file(marcxml, task_todo[0], extraction_name)
            #if the writing of the xml is wrong I consider all the bibcodes problematic
            if not wrote_filename:
                bibcodes_probl = bibcodes_probl + bibcodes_ok
                bibcodes_ok = []
            del w2f
        #otherwise I put all the bibcodes in the problematic
        else:
            bibcodes_probl = bibcodes_probl + bibcodes_ok
            bibcodes_ok = []
            wrote_filename = False
        
        #finally I pass to the done bibcodes to the proper file    
        q_done.put([task_todo[0], bibcodes_ok, wrote_filename])
        #and the problematic bibcodes
        q_probl.put([task_todo[0], bibcodes_probl])
             
        lock_stdout.acquire()
        printmsg(True, multiprocessing.current_process().name + (' (worker) finished to process group %s \n' % task_todo[0]))  
        lock_stdout.release()
        
    
    if queue_empty:
        #I tell the output processes that I'm done
        q_done.put(['WORKER DONE'])
        q_probl.put(['WORKER DONE'])
        #I tell the manager that I'm dying because the queue is empty
        q_life.put(['QUEUE EMPTY'])
        #I set a variable to skip the messages outside the loop
        lock_stdout.acquire()
        printmsg(True, multiprocessing.current_process().name + ' (worker) Queue empty: exiting \n')  
        lock_stdout.release()
    else:
        #I tell the manager that I'm dying because I reached the maximum amount of group to process
        q_life.put(['MAX LIFE REACHED'])
        lock_stdout.acquire()
        printmsg(True, multiprocessing.current_process().name + ' (worker) Maximum amount of groups of bibcodes reached: exiting \n')  
        lock_stdout.release()    
        


def done_extraction_process(q_done, num_active_workers, lock_stdout, q_life, extraction_directory, verbose):
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
                w2f = write_files.WriteFile(extraction_directory, verbose)
                w2f.write_done_bibcodes_to_file(group_done[1])
                
                lock_stdout.acquire()
                printmsg(True, multiprocessing.current_process().name + (' (done bibcodes worker) wrote done bibcodes for group %s \n' % group_done[0]))  
                lock_stdout.release()
                
            # I call the procedure to submit to invenio the process to upload the file
            filename_path = group_done[2]
            
            #invenio.bibtask.task_low_level_submission http://bit.ly/nnQZbs
            
    
    #I tell the manager that I'm done and I'm exiting
    q_life.put(['DONEBIBS DONE'])
            
    lock_stdout.acquire()
    printmsg(True, multiprocessing.current_process().name + ' (done bibcodes worker) job finished: exiting \n')  
    lock_stdout.release()
            

def problematic_extraction_process(q_probl, num_active_workers, lock_stdout, q_life, extraction_directory, verbose):
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
                w2f = write_files.WriteFile(extraction_directory, verbose)
                w2f.write_problem_bibcodes_to_file(group_probl[1])
                
                lock_stdout.acquire()
                printmsg(True, multiprocessing.current_process().name + (' (problematic bibcodes worker) wrote problematic bibcodes for group %s \n' % group_probl[0]))  
                lock_stdout.release()
    
    #I tell the manager that I'm done and I'm exiting
    q_life.put(['PROBLEMBIBS DONE'])
            
    lock_stdout.acquire()
    printmsg(True, multiprocessing.current_process().name + ' (problematic bibcodes worker) job finished: exiting \n')  
    lock_stdout.release()
        
        