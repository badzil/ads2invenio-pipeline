'''
Module for managing errors
'''

class Error(Exception):
    """Base class for custom exceptions"""
    pass

class GenericError(Error):
    """Generic error to raise with a custom message"""
    def __init__(self, field_desc):
        """ Constructor: initialize the variable containing the \
        description of the field with errors"""
        self.field_desc = field_desc
    def __str__(self):
        message = "ERROR: %s \n" % self.field_desc
        return message
    
