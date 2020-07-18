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

class AedatLoader(FileLoaderInterface):

    # override
    def load_events(self, filename, polarities=[-1,1], to_secs=True):
        """
            Returns events from a dat file. Each dat file is a binary file in which events
            are encoded using 4 bytes (unsigned int32) for the timestamps and 4 bytes
            (unsigned int32) for the data. The data is composed of 7 bits for the x position,
            7 bits for the y position and 1 bit for the polarity.

            Params
            ------
            :param filename: the filename/path to the .aedat file
            :param polarities: the polarity encoding, can be [0,1] or [-1,1] (default)

            Returns
            -------
            :returns: a recarray with (x, y, ts, p)

        """

        # Some useful defs
        aedat_event_dtype = [('data', np.uint32), ('ts1', np.uint8), ('ts2', np.uint8),
                             ('ts3', np.uint8), ('ts4', np.uint8)]
        HEX = 16

        # Open file in binary mode
        f = open(filename, "rb")

        # Read Header
        f.readline()  # Version
        f.readline()  # Description 1
        f.readline()  # Description 2
        f.readline()  # Description 3
        f.readline()  # Date

        # Compute number of events
        start = f.tell()
        end = f.seek(0, 2)
        n_events = (end-start)/8

        logging.info(f'Processing {n_events} events')

        # Reposition file cursor
        f.seek(-(end-start), 1)

        jaer_events = np.fromfile(f, dtype=aedat_event_dtype, count=-1)

        y = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('007F0000', HEX)), 16)
        x = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('FE000000', HEX)), 25)
        p = np.right_shift(np.bitwise_and(jaer_events['data'].astype(np.uint32), int('01000000', HEX)), 24)

        ts1 = np.left_shift(jaer_events['ts4'].astype(np.uint32), 0)
        ts2 = np.left_shift(jaer_events['ts3'].astype(np.uint32), 8)
        ts3 = np.left_shift(jaer_events['ts2'].astype(np.uint32), 16)
        ts4 = np.left_shift(jaer_events['ts1'].astype(np.uint32), 24)

        ts = ts1 + ts2 + ts3 + ts4

        # Transform from us to secs
        if to_secs:
            ts = ts / 1e6

        # transform to -1,1
        if polarities[0] == -1:
            p = -1 + 2 * p

        recarray = np.rec.fromarrays([x,y,ts,p], dtype=event_dtype)

        return recarray