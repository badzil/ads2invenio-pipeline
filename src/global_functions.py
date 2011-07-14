'''
File containing global functions
'''

import sys
import os

def printmsg(verbose, msg):
    """function to print debug messages"""
    if verbose:
        sys.stdout.write(msg)
        
def mem(size="rss"):
    """Generalization; memory sizes: rss, rsz, vsz."""
    return int(os.popen('ps -p %d -o %s | tail -1' % (os.getpid(), size)).read())