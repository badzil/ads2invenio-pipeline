'''
File containing global functions
'''

import sys
import os
import time

def printmsg(verbose, msg):
    """function to print debug messages"""
    if verbose:
        sys.stdout.write(time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + msg)
        
def mem(size="rss"):
    """Generalization; memory sizes: rss, rsz, vsz."""
    return int(os.popen('ps -p %d -o %s | tail -1' % (os.getpid(), size)).read())