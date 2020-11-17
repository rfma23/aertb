#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"

# =============================================================================

from abc import ABC, abstractmethod

# =============================================================================

class LoaderInterface(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def load_events(self, filename, polarities, to_secs):
        pass

    @abstractmethod
    def get_header(self, filename):
        pass
