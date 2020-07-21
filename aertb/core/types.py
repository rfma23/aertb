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
from collections import namedtuple
# =============================================================================

event_dtype = np.dtype([('x', np.uint16), ('y', np.uint16),
                        ('ts', np.float32), ('p', np.int8)])

Sample = namedtuple('Sample', ['name', 'label', 'events'])
# =============================================================================