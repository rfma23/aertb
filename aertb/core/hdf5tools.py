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
import random
import click
import h5py

from .types import Sample, EvSample, event_dtype

import h5py
import numpy as np
import random
from collections import namedtuple




# =============================================================================
class HDF5FileIterator:

    def __init__(self, file, samples):
        """
            Returns an iterator over an HDF5 file
            Suggested usage is:
                ```
                    iterator = HDF5FileIterator(..)
                    for elem in iterator:
                        # do something ...
                ```
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
            a recarray of events
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

        return HDF5FileIterator(self.file, train_samples), HDF5FileIterator(self.file, test_samples)

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