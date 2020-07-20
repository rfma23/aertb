#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__      = "Rafael Mosca"
__email__       = "rafael.mosca@mail.polimi.it"
__copyright__   = "Copyright 2020 - Rafael Mosca"
__license__     = "MIT"
__version__     = "1.0"

# =============================================================================

import numpy as np
import logging

from aertb.core.types import event_dtype
from aertb.core.loaders.interface import FileLoaderInterface

# =============================================================================

class DatLoader(FileLoaderInterface):

    # override
    def load_events(self, filename, polarities=[-1,1], to_secs=True):
        """
            Returns events from a dat file. Each dat file is a binary file in which events
            are encoded using 4 bytes (unsigned int32) for the timestamps and 4 bytes
            (unsigned int32) for the data, encoding is little-endian ordering. The data is
            composed of 14 bits for the x position, 14 bits for the y position and 1 bit for
            the polarity (encoded as -1/1).

            Params
            ------
            :param filename: the filename/path to the .dat file
            :param polarities: the polarity encoding, can be [0,1] or [-1,1] (default)

            Returns
            -------
            :returns: a recarray with (x, y, ts, p)

        """

        # Some useful defs
        prophesee_event_dtype = [('ts', np.uint32), ('xyp', np.uint32)]
        HEX = 16

        # Open file in binary mode
        f = open(filename, "rb")

        # Read Header
        parsedHeader = False
        header = []

        while parsedHeader is False:

            two_bytes = f.read(2)
            # if they match a comment syntax
            if (two_bytes==b'% '): 
                # reset file cursor
                f.seek(-2, 1) 
                # read whole line
                header.append(f.readline()) # 
            else:
                # signal header is parsed
                parsedHeader = True

        # Compute number of events
        start = f.tell()
        end = f.seek(0, 2)
        n_events = (end-start)/8
        logging.info(f'Processing {n_events} events')

        # Reposition file cursor
        f.seek(-(end-start), 1)

        prophesee_events = np.fromfile(f, dtype=prophesee_event_dtype, count=-1)

        f.close()

        x = np.bitwise_and(prophesee_events['xyp'], int('00003FFF', HEX))
        y = np.right_shift(np.bitwise_and(prophesee_events['xyp'], int('0FFFC000', HEX)), 14)
        p = np.right_shift(np.bitwise_and(prophesee_events['xyp'], int('10000000', HEX)), 28)
        ts = prophesee_events['ts']

        # Transform from us to secs
        if to_secs:
            ts = ts / 1e6

        # transform to -1,1
        if polarities[0] == -1:
            p = -1 + 2 * p


        recarray = np.rec.fromarrays([x,y,ts,p], dtype=event_dtype)

        return recarray

