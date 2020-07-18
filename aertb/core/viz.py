#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__      = "Rafael Mosca"
__email__       = "rafael.mosca@mail.polimi.it"
__copyright__   = "Copyright 2020 - Rafael Mosca"
__license__     = "MIT"
__version__     = "1.0"

# =============================================================================

import gif
import math
import click
import logging
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================

def make_gif(events, filename='my_gif.gif', n_frames=8, tau=None,
             camera_size=(34,34),clean=False, R=1, val=2, clean_tau=0.005,
             gtype='decay'):

    @gif.frame
    def get_frame(frame_events, clean, gtype):

        if gtype == 'decay':
            if clean:
                mask = np.zeros(camera_size, dtype=np.float32)
                canvas = np.zeros(camera_size, dtype=np.float32)
                last_ts = 0

                for event in frame_events:
                    mask   = np.multiply(mask, math.exp(-(event['ts']-last_ts)/clean_tau))
                    canvas = np.multiply(canvas, math.exp(-(event['ts']-last_ts)/tau))

                    # keep track of active regions
                    x_bounds = (max(0, event['x']-R), min(camera_size[0], event['x']+R+1))
                    y_bounds = (max(0, event['y']-R), min(camera_size[1], event['y']+R+1))
                    mask[y_bounds[0]:y_bounds[1], x_bounds[0]:x_bounds[1]] += 1

                    canvas[event['y'], event['x']] += 1

                    canvas = np.multiply(canvas, (mask > val).astype(int))

                    last_ts = event['ts']

            else:
                canvas = np.zeros((camera_size), dtype=np.float32)
                last_ts = 0

                for event in frame_events:
                    canvas = np.multiply(canvas, math.exp(-(event['ts']-last_ts)/tau))
                    canvas[event['y'], event['x']] += 1
                    last_ts = event['ts']

            plt.imshow(canvas, cmap='hot')

        elif gtype == 'std':
            polarity_mapper = {0: -1, -1: -1, 1:1}

            canvas = np.zeros(camera_size, dtype=np.float32)
            for event in frame_events:
                canvas[event['y'], event['x']] = polarity_mapper[event['p']]

            plt.imshow(canvas, cmap='gray', vmin=-1, vmax=1)

        else:
            raise ValueError('Not a valid visualisation type')



    duration = events[-1]['ts'] - events[0]['ts']
    min_ts = events[0]['ts']
    delta = duration / n_frames
    if tau is None: tau = delta

    logging.info(f'Duration {duration:6f}, Delta {delta} Tau {tau}')
    
    frames = []
    for i in range(n_frames):
        time_filter = (min_ts + delta*(i) <= events['ts'])*(events['ts'] < min_ts + delta*(i+1))
        filtered_events = events[time_filter]
        frame = get_frame(filtered_events, clean, gtype)
        frames.append(frame)

    gif.save(frames, filename, duration=200)

# =============================================================================