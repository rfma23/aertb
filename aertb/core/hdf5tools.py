#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"

# =============================================================================
import numpy as np
import logging
import random
import click
import h5py
import os

from os.path import join, isfile, splitext
from collections import namedtuple
from tqdm import tqdm

from aertb.core.types import Sample, EvSample, event_dtype
from aertb.core.const import SUPPORTED_EXT
from aertb.core.loaders import get_loader
# =============================================================================
class HDF5FileIterator:
    """ Returns an iterator over an HDF5 file, suggested usage is:
        
                iterator = HDF5FileIterator(..)
                for elem in iterator:
                    # do something ...
        
    """

    def __init__(self, file, samples):
        """
            
            Params
            ------
            :param samples: the samples that will be included in the iteration

        """
        self.file = file
        self.samples = samples
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):

        while self.index < len(self.samples):
            sample = self.samples[self.index]
            data = self.file[sample.group][sample.name]
            events_np = np.array(data)
            self.index += 1

            return EvSample(sample.group, sample.name, events_np)

        else:
            self.index = 0
            raise StopIteration

    def __getitem__(self, x):
        if isinstance(x, slice):
            start = x.start
            stop = x.stop
            step = x.step
            return HDF5FileIterator(self.file, self.samples[start:stop:step])

    def reset(self):
        """ Resets the iterator"""
        self.index = 0

    def __len__(self):
        return len(self.samples)


# =============================================================================
class HDF5File:
    """
        A wrapper offering useful methods over an HDF5 file, to access
        the original file use the .file attribute
    """

    # ------------------------------------------------------------------------
    def __init__(self, filename, groups='all'):
        """
            Params
            ------
            :param filename: the name of the HDF5 file
            :param groups: the groups in the HDF5 that will be considered
                           by default all groups
            :param n_samples_group: the number of samples that will be considered
                                    by default every sample in the group

        """
        self.file = h5py.File(filename, 'r')
        self.groups = groups
        self.file_stats = self.get_file_stats()

    # ------------------------------------------------------------------------
    def get_file_stats(self):
        """
            Returns a dictionary with key: group and value: sample count
        """
        file_stats = {}
        groups = list(self.file.keys())
        for group in groups:
            group_samples = list(self.file[group].keys())
            file_stats[group] = len(group_samples)
        return file_stats

    # ------------------------------------------------------------------------
    def load_events(self, group, name):
        """
            Params
            ------
            :param group: the group/label of the sample to load
            :param name: the name of the sample to load

            Returns
            -------
            np.array
                a structured array of events
        """
        data = self.file[group][name]
        return np.array(data)

    # ------------------------------------------------------------------------
    def get_sample_names(self, n_samples_group='all', rand=-1):
        """
            Returns the samples contained in the file

            Params
            ------
            :param rand: if greater than zero it specifies the seed for the
                            random selection, if negative it is sequential

        """

        groups = list(self.file.keys()) if self.groups == 'all' else self.groups

        samples = []
        for group in groups:

            group_samples = list(self.file[group].keys())

            if n_samples_group == 'all':
                to_sample = len(group_samples)

            elif len(group_samples) < n_samples_group:
                err_msg = f'There are insufficient samples in group {group}'
                click.secho(err_msg, bg='yellow')
                to_sample = len(group_samples)

            else:
                to_sample = n_samples_group

            # Within group selection
            if rand < 0:
                indices = range(0, to_sample)
            else:
                random.seed(rand)
                indices = random.sample(range(0, len(group_samples)), to_sample)

            # Add samples to container
            for i in indices:
                samples.append(Sample(group, group_samples[i]))

        # Shuffle between groups
        if rand > 0:
            random.Random(rand).shuffle(samples)

        return samples

    # ------------------------------------------------------------------------
    def iterator(self, n_samples_group='all', rand=23):
        """returns an iterator over the file samples

        Parameters
        ----------
        n_samples_group : str, optional
            the samples to consider for each label group, by default 'all'
        rand : int, optional
            a seed for shuffling, by default 23

        Returns
        -------
        iterator
            it can be iterated with next() or a for loop
        """

        samples = self.get_sample_names(n_samples_group, rand)
        iterator = HDF5FileIterator(self.file, samples)
        return iterator

    # ------------------------------------------------------------------------
    def train_test_split(self, test_percentage, stratify=True, rand=23):
        """
            creates a train/test split from a single HDF5 file,

            :param test_percentage: specifies in a float [0.0, 1) how big should be
                                    the test set
            :param groups: specify the groups as a list of strings from where the samples
                            should be taken, all other groups will be ignored

            :param statify: if stratify=True the percentages will be relative to the
                            class count and therefore the test set will have the same
                            distribution as the class count, otherwise the test samples
                            are taken randomly regardless of their class, in some scenarios
                            this may cause that some classes may not be in the test set

            :param rand: specifies the random seed for shuffling the samples, use negative
                         numbers or None to return samples in a sequential order

        """

        train_samples = []
        test_samples = []

        groups = list(self.file.keys()) if self.groups == 'all' else self.groups

        if stratify:
            for group in groups:

                group_samples = list(self.file[group].keys())

                n_test_samples = round(len(group_samples) * test_percentage)
                n_train_samples = len(group_samples) - n_test_samples

                # Within group selection
                if rand < 0:
                    indices = range(0, len(group_samples))
                else:
                    random.seed(rand)
                    indices = random.sample(range(0, len(group_samples)), len(group_samples))

                train_indices = indices[0:n_train_samples]
                test_indices = indices[-n_test_samples:-1]

                for i in train_indices:
                    train_samples.append(Sample(group, group_samples[i]))

                for j in test_indices:
                    test_samples.append(Sample(group, group_samples[j]))

            # Shuffle between groups
            if rand > 0:
                random.Random(rand).shuffle(train_samples)
                random.Random(rand).shuffle(test_samples)

        else:
            all_samples = self.get_sample_names(rand)
            n_test_samples = round(len(all_samples) * test_percentage)
            n_train_samples = len(all_samples) - n_test_samples

            train_samples = all_samples[0:n_train_samples]
            test_samples = all_samples[-n_test_samples:-1]

        return (HDF5FileIterator(self.file, train_samples), HDF5FileIterator(self.file, test_samples))

    # ------------------------------------------------------------------------
    def fixed_train_test_split(self, n_train, n_test, rand=23):
        """
            :param n_train: number of train samples per group
            :param n_test: number of test samples per group
        """

        groups = list(self.file.keys()) if self.groups == 'all' else self.groups

        n_all_samples = sum(self.file_stats.values())
        train_samples = []
        test_samples = []

        for group in groups:
            group_samples = list(self.file[group].keys())

            for i, sample in enumerate(group_samples[:n_train + n_test]):
                if i < n_train:
                    train_samples.append(Sample(group, group_samples[i]))
                else:
                    test_samples.append(Sample(group, group_samples[i]))

        if rand > 0:
            random.Random(rand).shuffle(train_samples)
            random.Random(rand + 1).shuffle(test_samples)

        return HDF5FileIterator(self.file, train_samples), HDF5FileIterator(self.file, test_samples)

# =============================================================================
# Conversion code
# =============================================================================

def create_hdf5_dataset(dataset_name, file_or_dir, ext, polarities=[0, 1],
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

        # if we are dealing with only one file
        if isfile(file_or_dir):
            fname = os.path.split(file_or_dir)[1].split('.')[0]
            g = fp.create_group('root')
            loader = get_loader(ext)
            events = loader.load_events(file_or_dir, polarities, to_secs)
            g.create_dataset(f'{fname}', data=events, compression=8)

        # else we are dealing with directories
        else:
            _add_all_files(fp, file_or_dir, 'root', polarities, to_secs, ext)

            # Navigate subdirectories
            sub_dirs = [f.name for f in os.scandir(file_or_dir) if f.is_dir()]
            if '.Ds_Store' in sub_dirs: sub_dirs.remove('.Ds_Store')

            logging.info(f'Processing directories: {sub_dirs} ')
            # for each subdirectory add all_files
            for folder in sub_dirs:
                _add_all_files(fp, join(file_or_dir, folder), folder, polarities, to_secs, ext)

# -------------------------------------------------------------------------
def _add_all_files(fp, dir_path, dir_name, polarities, to_secs, ext):
    """
        Supporting function for creating a dataset
    """

    logging.info(f'Processing {dir_path}')

    # Get all file names
    all_files = [f for f in os.scandir(dir_path)]
    valid_files = [f.name for f in all_files if splitext(f)[1] == f'.{ext}']

    logging.info(f'Files: {valid_files}')

    if len(valid_files) > 0:

        group = fp.create_group(dir_name)
        logging.info(f'Found the following valid files {valid_files} in {dir_path}')

        for file in tqdm(valid_files, desc=f'Dir: {dir_name}', unit='file'):
            
            loader = get_loader(ext)
            events = loader.load_events(join(dir_path, file),polarities, to_secs)

            group.create_dataset(f"{file.split('.')[0]}", data=events, compression=8)
# =============================================================================
