'''
File containing global functions
'''

import sys

def printmsg(verbose, msg):
    """function to print debug messages"""
    if verbose:
        sys.stdout.write(msg)