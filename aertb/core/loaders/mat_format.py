#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"

# =============================================================================

from scipy.io import loadmat
import numpy as np
import logging

from aertb.core.types import event_dtype
from aertb.core.loaders.interface import LoaderInterface



# =============================================================================

class MatLoader(LoaderInterface):

    # ------------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------------
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance
        
    # ------------------------------------------------------------------------
    # override
    def load_events(self, filename, polarities=[-1, 1], to_secs=False):
        """
            Returns events from a mat file. Each mat file is a MATLAB file containing an
            object with the TD events.

            Works on DVS-BARREL 'Original.mat'

            Params
            ------
            :param filename: the filename/path to the .mat file
            :param polarities: the polarity encoding, can be [0,1] or [-1,1] (default)

            Returns
            -------
            :returns: a recarray with (x, y, ts, p)

        """

        mat_file = loadmat(filename)

        x = mat_file['TD'][0][0][0][0] - 1
        y = mat_file['TD'][0][0][1][0] - 1
        p = mat_file['TD'][0][0][2][0]
        ts = mat_file['TD'][0][0][3][0]

        if polarities[0] == 0:
            p = (p + 1) // 2
        if to_secs:
            ts = ts / 1e6

        return np.rec.fromarrays([x, y, ts, p], dtype=event_dtype)
    
    # ------------------------------------------------------------------------
    # override
    def get_header(self, filename):
        print('No header defined')

    # ------------------------------------------------------------------------
    def load_sample_events(self, filename, object_name='ROI', sample=0, polarities=[-1, 1], to_secs=False):
        """
            Returns events from a mat file. Each mat file is a MATLAB file containing an
            object with the TD events.

            Works on DVS-BARREL 'Stabilized.mat / Moving.mat'

            Params
            ------
            :param filename: the filename/path to the .mat file
            :param object_name: the name of the MATLAB object saved in the file
            :param sample: an integer specifying the sample to load
            :param polarities: the polarity encoding, can be [0,1] or [-1,1] (default)

            Returns
            -------
            :returns: a recarray with (x, y, ts, p)

        """
        mat_file = loadmat(filename)

        x = mat_file[object_name][0][sample][0][0][0][0] - 1
        y = mat_file[object_name][0][sample][0][0][1][0] - 1
        p = mat_file[object_name][0][sample][0][0][2][0]
        ts = mat_file[object_name][0][sample][0][0][3][0]

        if polarities[0] == 0:
            p = (p + 1) // 2

        if to_secs:
            ts = ts / 1e6

        return np.rec.fromarrays([x,y,ts,p], dtype=event_dtype)
