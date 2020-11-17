#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__      = "Rafael Mosca"
__email__       = "rafael.mosca@mail.polimi.it"
__copyright__   = "Copyright 2020 - Rafael Mosca"
__license__     = "MIT"
__version__     = "1.0"

# =============================================================================

from pprint import pprint
import numpy as np
import logging

from aertb.core.types import event_dtype, stereo_event_dtype
from aertb.core.loaders.interface import LoaderInterface
from aertb.core.const import HEX
# =============================================================================

class DatLoader(LoaderInterface):

    # ------------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------------
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance
        
    # override
    # ------------------------------------------------------------------------
    def load_events(self, filename, polarities=[-1,1], to_secs=False):
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

        # Open file in binary mode
        f = open(filename, "rb")

        # Read Header (this advances file cursor)
        _ = self.parse_header(f)

        # Get Dat type and size
        ev_type = np.frombuffer(f.read(1), np.uint8)[0]
        ev_size = np.frombuffer(f.read(1), np.uint8)[0]

        logging.info(f'Event type {ev_type} Ev size {ev_size}')

        # Compute number of events
        start = f.tell()
        end = f.seek(0, 2)
        n_events = (end - start) / ev_size

        logging.info(f'Processing {n_events} events')

        # Reposition file cursor
        f.seek(-(end-start), 1)

        recarray = self.dat_events(f, ev_type, polarities, to_secs)

        return recarray

    # ------------------------------------------------------------------------
    def parse_header(self, f):

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

        f.seek(-2, 1)

        return header

    # ------------------------------------------------------------------------
    # override
    def get_header(self, filename):

        # Open file in binary mode
        f = open(filename, "rb")

        # print parsed header
        pprint(self.parse_header(f))

        f.close()
    
    # ------------------------------------------------------------------------
    def dat_events(self, f, ev_type, polarities, to_secs):
        """
            Load the events with the appropriate file extension

            Params
            ------
            :param f: the file pointer
            :param ev_type: the DAT event type
            :param polarities: how the polarities hould be encoded
            :param to_secs: if we should encode TS in secs
        """
        if ev_type == 12:
            return self.load_cd_events(f, polarities, to_secs)
        elif ev_type == 10:
            return self.load_stereo_cd_events(f, polarities, to_secs)
        else:
            raise ValueError(f'Event Type {ev_type} not supported')

    # ------------------------------------------------------------------------
    def load_cd_events(self, f, polarities, to_secs):
        prophesee_event_dtype = [('ts', np.uint32), ('xyp', np.uint32)]

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

        return np.rec.fromarrays([x, y, ts, p], dtype=event_dtype)

    # ------------------------------------------------------------------------
    def load_stereo_cd_events(self, f, polarities, to_secs):
        prophesee_stereo_event_dtype = [('ts', np.uint32), ('xyp', np.uint32),
                                        ('x_', np.float32), ('y_', np.float32),
                                        ('z_', np.float32), ('d_', np.float32)]

        prophesee_events = np.fromfile(f, dtype=prophesee_stereo_event_dtype, count=-1)

        f.close()

        x = np.bitwise_and(prophesee_events['xyp'], int('00003FFF', HEX))
        y = np.right_shift(np.bitwise_and(prophesee_events['xyp'], int('0FFFC000', HEX)), 14)
        p = np.right_shift(np.bitwise_and(prophesee_events['xyp'], int('F0000000', HEX)), 28)
        ts = prophesee_events['ts']
        x_ = prophesee_events['x_']
        y_ = prophesee_events['y_']
        d_ = prophesee_events['d_']
        z_ = prophesee_events['z_']

        # Transform from us to secs
        if to_secs:
            ts = ts / 1e6

        # transform to -1,1
        if polarities[0] == -1:
            p = -1 + 2 * p
        return np.rec.fromarrays([x, y, ts, p, x_, y_, d_, z_], dtype=stereo_event_dtype)
