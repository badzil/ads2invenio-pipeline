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
        super(GenericError, self).__init__()
        self.field_desc = field_desc
    def __str__(self):
        message = "ERROR: %s \n" % self.field_desc
        return message
    
