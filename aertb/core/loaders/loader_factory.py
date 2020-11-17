#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__ = "Rafael Mosca"
__email__ = "rafael.mosca@mail.polimi.it"
__copyright__ = "Copyright 2020 - Rafael Mosca"
__license__ = "MIT"
__version__ = "1.0"

# =============================================================================

import os

from aertb.core.loaders import BinLoader
from aertb.core.loaders import DatLoader
from aertb.core.loaders import AedatLoader
from aertb.core.loaders import MatLoader

# =============================================================================
def get_loader(extension):
    """
        Acts as a factory method for File loaders
    """

    if extension in {'bin', '.bin'}:
        return BinLoader()

    elif extension in {'dat', '.dat'}:
        return DatLoader()

    elif extension in {'aedat', '.aedat'}:
        return AedatLoader()

    elif extension in {'mat', '.mat'}:
        return MatLoader()

    else:
        raise ValueError(f'File extension: "{extension}" not supported')