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
import random
import click
import h5py

from .types import Sample, event_dtype
# =============================================================================

class HDF5FileIterator:

    def __init__(self, filename, groups='all', n_samples='all', rand=-1):
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
            :param groups: the groups in the HDF5 that will be considered
                            by default all groups
            :param n_samples: the number of samples that will be considered
                              by default every sample in the group
            :param rand: if greater than zero it specifies the seed for the
                            random selection, if negative it is sequential

            Returns
            -------
            nothing

        """
        dataset = h5py.File(filename, 'r')
        self.dataset = dataset

        if groups == 'all': groups = list(dataset.keys())

        samples = []
        for group in groups:

            group_samples = list(dataset[group].keys())

            if n_samples == 'all':
                n_samples = len(group_samples)

            elif len(group_samples) < n_samples:
                err_msg = f'There are insufficient samples in group {group}'
                click.secho(err_msg, bg='yellow')
                n_samples = group_samples

            random.seed(rand)
            indices = random.sample(range(0, len(group_samples)), n_samples)

            for i in indices:
                samples.append((group_samples[i], group))

            if rand > 0:
                random.Random(rand).shuffle(samples)

        self.samples = samples
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):

        while self.index < len(self.samples):
            sample, group = self.samples[self.index]
            data = self.dataset[group][sample]
            events_np = np.array(data, dtype=event_dtype)
            self.index += 1

            return Sample(sample, group, events_np)

        else:
            self.dataset.close()
            raise StopIteration

    def reset(self):
        self.index = 0