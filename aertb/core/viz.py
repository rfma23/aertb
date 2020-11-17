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
from tqdm import tqdm
import matplotlib.pyplot as plt

# =============================================================================

def make_gif(events, filename='my_gif.gif', n_frames=8, f_type='decay', axis=False, **kwargs):
    """Creates a GIF from the passed events with the specified number of frames. 
        additional paramters such as 'tau' for the exponential decay 'duration' 
        for the length of the GIF (default 200), etc. are specified as keyword 
        arguments (**kwargs)

    Parameters
    ----------
    events : np.array
        the events to be used for the GIF
    filename : str, optional
        the path+name for the gif file, by default 'my_gif.gif'
    n_frames : int, optional
        the number of frames that will be computed, by default 8
    f_type : str, optional
        the type of frame used:
        'nop' - no polarity, 
        'decay' - nop+exponential decay,
        'std' - pos/neg polarity, 
        by default 'decay'
    axis : bool, optional
        determines whether the GIF should show axis labels, by default False

    Raises
    ------
    ValueError
        When an invalid frame type is selected
    """
    
    @gif.frame
    def get_frame(frame_events, f_type):

        if f_type == 'decay':
            canvas = np.zeros((camera_size), dtype=np.float32)
            last_ts = 0

            for event in frame_events:
                canvas = np.multiply(canvas, math.exp(-(event['ts']-last_ts)/tau))
                canvas[event['y'], event['x']] += 1
                last_ts = event['ts']

            plt.imshow(canvas, cmap='hot')

        elif f_type == 'std':
            polarity_mapper = {0: -1, -1: -1, 1:1}

            canvas = np.zeros(camera_size, dtype=np.float32)
            for event in frame_events:
                canvas[event['y'], event['x']] = polarity_mapper[event['p']]
            
            if axis is False:
                plt.xticks([])
                plt.yticks([])
                
            plt.imshow(canvas, cmap='gray', vmin=-1, vmax=1)
        
        elif f_type == 'nop':
            polarity_mapper = {0: 1, -1: 1, 1:1}

            canvas = np.zeros(camera_size, dtype=np.float32)
            for event in frame_events:
                canvas[event['y'], event['x']] = polarity_mapper[event['p']]
            
            if axis is False:
                plt.xticks([])
                plt.yticks([])
                
            plt.imshow(canvas, cmap='gray', vmin=0, vmax=1)
            
        else:
            raise ValueError('Not a valid visualisation type')
    
    # create frame slice
    duration = events[-1]['ts'] - events[0]['ts']
    min_ts = events[0]['ts']
    delta = duration / n_frames
    
    camera_size = (max(events['x'])+1, max(events['y'])+1)
    
    if f_type == 'decay':
        tau = kwargs.get('tau', delta)
        
    frames = []
    
    for i in tqdm(range(n_frames), desc='GIF Frames', unit='frame'):
        time_filter = (min_ts + delta*(i) <= events['ts'])*(events['ts'] < min_ts + delta*(i+1))
        filtered_events = events[time_filter]
        frame = get_frame(filtered_events, f_type)
        frames.append(frame)
    
    duration = kwargs.get('duration', 2)
    gif.save(frames, filename, duration=200)