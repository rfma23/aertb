#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__      = "Rafael Mosca"
__email__       = "rafael.mosca@mail.polimi.it"
__copyright__   = "Copyright 2020 - Rafael Mosca"
__license__     = "MIT"
__version__     = "1.0"

# =============================================================================

import re
import logging
import numpy as np
from pprint import pprint

from aertb.core.types import event_dtype
from aertb.core.loaders.interface import LoaderInterface
from aertb.core.const import HEX

# =============================================================================

class AedatLoader:
    """ Finds the appropriate version to load the file ... """

    # ------------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------------
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    # ------------------------------------------------------------------------
    def load_events(self, filename, polarities, to_secs):

        version = self.get_version(filename)

        if version == '2.0':
            return self.load_events_v2(filename, polarities, to_secs)

        else:
            msg = 'This file version is currently not supported' + \
                'feel free to raise an issue on the Github repo'
            raise NotImplementedError(msg)
    
    # ------------------------------------------------------------------------
    @classmethod
    def get_version(self, filename):
        """ Gets the version of the AEDAT file in format (DIGIT.DIGIT)
        """
        # open file
        f = open(filename, "rb")

        _ = f.read(1)
        first_line = f.readline()

        # Rewind file
        f.seek(0)

        # Regex matching
        m = re.search(r'(\d\.\d)', str(first_line))
        return m.group(0)

    # ------------------------------------------------------------------------
    def load_events_v2(self, filename, polarities, to_secs):
        """
            Returns events from an aedat file. Each dat file is a binary file  
            in which events are encoded using 4 bytes (unsigned int32) for the 
            timestamps and 4 bytes (unsigned int32) for the data. The data is 
            composed of 7 bits for the x position, 7 bits for the y position 
            and 1 bit for the polarity.

        Parameters
        ----------
        filename : str,
            the name of the file to load
        polarities : list, 
            the polarity encoding, can be [0,1] or [-1,1], by default [-1, 1]
        to_secs : bool,
            determines whether to keep in microseconds (False) or convert to 
            seconds (True), by default True

        Returns
        -------
        np.array
            a numpy structured array with (x, y, ts, p) fields
        """

        # Some useful defs '> stands for Big Endian '
        aedat_event_dtype = [('pad', '>u2'),('data', '>u2'), ('ts', '>u4')]

        # Open file in binary mode
        f = open(filename, "rb")

        # Read Header (this advances file cursor)
        _ = self.parse_header(f)
        
        # Compute number of events
        start = f.tell()
        end = f.seek(0, 2)
        n_events = (end-start)/8

        logging.info(f'Processing {n_events} events')

        # Reposition file cursor
        f.seek(-(end-start), 1)

        jaer_events = np.fromfile(f, dtype=aedat_event_dtype, count=-1)

        # Close file
        f.close()

        # Do bit logic with appropriate masks
        p = np.right_shift(np.bitwise_and(jaer_events['data'], int('8000', HEX)), 15)
        x = np.right_shift(np.bitwise_and(jaer_events['data'], int('7F00', HEX)), 8)
        y = np.bitwise_and(jaer_events['data'], int('007F', HEX))
        ts = jaer_events['ts']
        
        # Transform from us to secs
        if to_secs:
            ts = ts / 1e6

        # transform to -1,1
        if polarities[0] == -1:
            p = -1 + 2 * p

        return np.rec.fromarrays([x,y,ts,p], dtype=event_dtype)

    # ------------------------------------------------------------------------
    def parse_header(self, f):

        # Read Header
        parsedHeader = False
        header = []

        while parsedHeader is False:

            a_byte = f.read(1)
            # if they match a comment syntax
            if a_byte==b'#': 
                # reposition file cursor beginning of line
                f.seek(-1, 1) 
                # read whole line
                header.append(f.readline()) # 
            else:
                # signal header is parsed
                parsedHeader = True
        
        f.seek(-1, 1)

        return header
    
    # ------------------------------------------------------------------------
    # override
    def get_header(self, filename):

        # Open file in binary mode
        f = open(filename, "rb")

        # print parsed header
        pprint(self.parse_header(f))

        f.close()



# =============================================================================

# class AedatV1File(FileInterface):

#     # override
#     def load_events(self, filename, polarities=[-1,1], to_secs=True):
#         """
#             Returns events from a dat file. Each dat file is a binary file in which events
#             are encoded using 4 bytes (unsigned int32) for the timestamps and 4 bytes
#             (unsigned int32) for the data. The data is composed of 7 bits for the x position,
#             7 bits for the y position and 1 bit for the polarity.

#             Params
#             ------
#             :param filename: the filename/path to the .aedat file
#             :param polarities: the polarity encoding, can be [0,1] or [-1,1] (default)

#             Returns
#             -------
#             :returns: a recarray with (x, y, ts, p)

#         """

#         # Some useful defs
#         aedat_event_dtype = [('data', np.uint32), ('ts1', np.uint8), ('ts2', np.uint8),
#                              ('ts3', np.uint8), ('ts4', np.uint8)]

#         # Open file in binary mode
#         f = open(filename, "rb")

#         # Read Header
#         parsedHeader = False
#         header = []

#         while parsedHeader is False:

#             a_byte = f.read(1)
#             # if they match a comment syntax
#             if a_byte==b'#': 
#                 # reset file cursor
#                 f.seek(-1, 1) 
#                 # read whole line
#                 header.append(f.readline()) # 
#             else:
#                 # signal header is parsed
#                 parsedHeader = True

#         f.seek(-1, 1)

#         # Compute number of events
#         start = f.tell()
#         end = f.seek(0, 2)
#         n_events = (end-start)/8

#         logging.info(f'Processing {n_events} events')

#         # Reposition file cursor
#         f.seek(-(end-start), 1)

#         jaer_events = np.fromfile(f, dtype=aedat_event_dtype, count=-1)

#         y = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('007F0000', HEX)), 16)
#         x = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('FE000000', HEX)), 25)
#         p = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('01000000', HEX)), 24)

#         ts1 = np.left_shift(jaer_events['ts4'].astype(np.uint32), 0)
#         ts2 = np.left_shift(jaer_events['ts3'].astype(np.uint32), 8)
#         ts3 = np.left_shift(jaer_events['ts2'].astype(np.uint32), 16)
#         ts4 = np.left_shift(jaer_events['ts1'].astype(np.uint32), 24)

#         ts = ts1 + ts2 + ts3 + ts4

#         # Transform from us to secs
#         if to_secs:
#             ts = ts / 1e6

#         # transform to -1,1
#         if polarities[0] == -1:
#             p = -1 + 2 * p

#         recarray = np.rec.fromarrays([x,y,ts,p], dtype=event_dtype)

#         return recarray

    
