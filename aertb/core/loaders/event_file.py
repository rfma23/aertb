#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"

# =============================================================================

import os

from aertb.core.loaders import BinLoader
from aertb.core.loaders import DatLoader
from aertb.core.loaders import AedatLoader
from aertb.core.loaders import MatLoader
from aertb.core.loaders import LoaderInterface
from aertb.core.loaders import get_loader
# =============================================================================
class PolarityEventFile:
    """A top level class redirecting instructions to the correct loader class 
    for the given file
    """

    def __init__(self, filename):
        """Initialises the appropriate loader attribute, this is an instance of 
        a class implementing FileInterface
        """
        self.filename = filename

        _ , file_extension = os.path.splitext(filename)

        if len(file_extension) > 1:
            extension = file_extension[1:]
        else:
            msg = 'Could not infer file extension, when processing the file' \
                  'please specify an extension after the filename'
            raise Exception(msg)

        self.loader = get_loader(extension)

    def load_events(self, polarities=[-1,1], to_secs=True):
        """
            Returns a structured event array from a supported event file

        Parameters
        ----------
        polarities : list, optional
            the polarity encoding, can be [0,1] or [-1,1], by default [-1, 1]
        to_secs : bool, optional
            determines whether to keep in microseconds (False) or convert to 
            seconds (True), by default True

        Returns
        -------
        np.array
            a numpy structured array with (x, y, ts, p) fields
        """

        return self.loader.load_events(self.filename, polarities, to_secs)

    @property
    def header(self):
        return self.get_header()

    def get_header(self):
        """ Gets the header specified in the file
        """
        return self.loader.get_header(self.filename)
    
        
# =============================================================================
# class EventFile(object):
#     """A factory class returning the correct loader class for the given file
#     """

#     def __new__(cls, filename):
#         return cls.get_file_loader(filename)
    
#     @classmethod
#     def get_file_loader(self, filename):

#         _ , file_extension = os.path.splitext(filename)

#         if len(file_extension) > 1:
#             extension = file_extension[1:]
#         else:
#             msg = 'Could not infer file extension, when processing the file' \
#                   'please specify an extension after the filename'
#             raise Exception(msg)

#         if extension in {'bin', '.bin'}:
#             return BinFile(filename)

#         elif extension in {'dat', '.dat'}:
#             return DatFile(filename)

#         elif extension in {'aedat', '.aedat'}:
#             return AedatFile(filename)

#         elif extension in {'mat', '.mat'}:
#             return MatFile(filename)

#         else:
#             raise ValueError(f'File extension: {extension} not supported')