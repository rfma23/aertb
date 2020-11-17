#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"


# =============================================================================

from os.path import join, isfile, splitext
from tqdm import tqdm
import logging
import h5py
import os

from aertb.core.loaders import BinLoader, DatLoader, AedatLoader, MatLoader

# =============================================================================

extensions = {'hdf5': ['.h5', '.hdf5', '.hdf', '.H5'],
              'dat': ['.dat', '.Dat'],
              'aedat': ['.aedat', '.Aedat'],
              'bin': ['.bin', '.Bin'],
              #'jaer': ['.jaer']
              }
# =============================================================================

class FileLoader:
    '''
        A File loader for a given file extension

        :param extension: the file extension of the file
    '''

    def __init__(self, extension):

        self.ext = extension

        if extension in {'bin', '.bin'}:
            self._loader = BinLoader()

        elif extension in {'dat', '.dat'}:
            self._loader = DatLoader()

        elif extension in {'aedat', '.aedat'}:
            self._loader = AedatLoader()

        elif extension in {'mat', '.mat'}:
            self._loader = MatLoader()

        else:
            raise ValueError(f'File extension: {extension} not supported')

    # -------------------------------------------------------------------------
    def load_events(self, filename, polarities=[0, 1], to_secs=True):
        return self._loader.load_events(filename, polarities, to_secs)

    # -------------------------------------------------------------------------
    def create_hdf5_dataset(self, dataset_name, file_or_dir, polarities=[0, 1],
                            to_secs=True):
        """
            Creates an HDF5 file with the specified name, for a parent
            directory containing .dat files. It will create a different
            group for each subdirectory

            Params
            ------
            :param dataset_name: the name of the HDF5 file with file extension
            :param parent_dir: the path pointing to the parent directory
                               where the dat files reside
            :param polarities: indicates the polarity encoding for the
                               data, it can be [0,1] or [-1,1]

        """

        with h5py.File(dataset_name, 'w') as fp:

            # if we are dealing with only one file, if it matches the extension
            if isfile(file_or_dir) and splitext(file_or_dir)[1] in extensions[self.ext]:
                    fname = os.path.split(file_or_dir)[1].split('.')[0]
                    g = fp.create_group('root')
                    events = self._loader.load_events(file_or_dir, polarities, to_secs)
                    g.create_dataset(f'{fname}', data=events, compression=8)

            # else we are dealing with directories
            else:

                self._add_all_files(fp, file_or_dir, 'root', polarities, to_secs)

                # Navigate subdirectories
                sub_dirs = [f.name for f in os.scandir(file_or_dir) if f.is_dir()]
                if '.Ds_Store' in sub_dirs: sub_dirs.remove('.Ds_Store')

                logging.info(f'Processing directories: {sub_dirs} ')

                # for each subdirectory add all_files
                for folder in sub_dirs:
                    self._add_all_files(fp, join(file_or_dir, folder), folder, polarities, to_secs)

    # -------------------------------------------------------------------------
    def _add_all_files(self, fp, dir_path, dir_name, polarities, to_secs):
        """
            Supporting function for creating a dataset
        """

        logging.info(f'Processing {dir_path}')

        # Get all file names
        all_files = [f for f in os.scandir(dir_path)]
        valid_files = [f.name for f in all_files if splitext(f)[1] in extensions[self.ext]]

        logging.info(f'Files: {valid_files}')

        if len(valid_files) > 0:

            group = fp.create_group(dir_name)
            logging.info(f'Found the following valid files {valid_files} in {dir_path}')

            for file in tqdm(valid_files, desc=f'Dir: {dir_name}'):

                events = self._loader.load_events(join(dir_path, file), polarities, to_secs)

                group.create_dataset(f"{file.split('.')[0]}", data=events, compression=8)
# =============================================================================
