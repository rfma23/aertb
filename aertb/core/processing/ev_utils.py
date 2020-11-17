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
import math
from tqdm import tqdm
from collections import namedtuple

from aertb.core.types import event_dtype
# =============================================================================
#                   Event Frame manipulation : Flipping
# =============================================================================

def flip_vertical(events):
    """
        Modifies a set of events so that the resulting image is flipped 
        vertically 
    """
    y = max(events['y'])-events['y']
    x = events['x']
    ts = events['ts']
    p = events['p']
    return np.core.records.fromarrays([x,y,ts,p], dtype=event_dtype)

# =============================================================================

def flip_horizontal(events):
    """
        Modifies a set of events so that the resulting image is flipped 
        horizontally 
    """
    x = max(events['x'])-events['x']
    y = events['y']
    ts = events['ts']
    p = events['p']
    return np.core.records.fromarrays([x,y,ts,p], dtype=event_dtype)

# =============================================================================

def flip_diagonal(events):
    """
        Modifes a set of events so that the resulting image is flipped along the 
        main diagonal
    """
    x = events['y']
    y = events['x']
    ts = events['ts']
    p = events['p']
    return np.core.records.fromarrays([x,y,ts,p], dtype=event_dtype)

# =============================================================================
#                   Event Frame manipulation : Rotation
# =============================================================================

def rotate(events, angle, direction='ccw'):
    """ Modifes a set of events so that the resulting image is rotated 

    Parameters
    ----------
    events : np.array,
        the input event structured array
    angle : int,
        degrees to rotate: 90, 180, or 270
    direction : str, optional
        'ccw' counterclockwise or 'cw' clockwise, by default 'ccw'

    Returns
    -------
    np.array
        the input array modified so the rotation takes place
    """
   
    # Handle direction
    angle = 360 - angle if direction=='cw' else angle
    
    if angle == 270:
        # Rotate 270 counterclockwise = flip diagonal + flip horizontal
        temp = flip_diagonal(events)
        rotated = flip_horizontal(temp)
    
    elif angle == 180 :
        # Rotate 180 counterclockwise = flip vertical + flip horizontal
        temp = flip_horizontal(events)
        rotated = flip_vertical(temp)
        
    elif angle == 90 :
        # Rotate 90 counterclockwise = flip diagonal + flip vertical
        temp = flip_diagonal(events)
        rotated = flip_vertical(temp)
    
    else:
        print('Unsupported angle')
        
    return rotated

    

# =============================================================================
#                   Event Frame manipulation : Cleaning
# =============================================================================

def clean(events, tau=0.5, val=10, R=3, allow_first=200):
    """
        Removes some of the noise in an event based scenario

        Parameters
        ----------
        events : the event structured numpy array
        tau : float, optional
            regulates the decay of the memory, by default 0.5
            important to set it properly!
        val : int, optional
            Mask value threshold, by default 10
        R : int, optional
            Dimension of the neighborhood, by default 3
        allow_first : int, optional
            how many events are let through at the beginning without seeing  
            the mask value, by default first 200
            
        Returns
        -------
        np.array
            the input structured array without the noise events
    """
    
    count =  0
    camera_size = (max(events['y'])+1, max(events['x'])+1)
    mask = np.zeros((camera_size), dtype=np.float32)
    last_ts = events[0]['ts']
    
    filtered_events = []
    
    progress_bar = tqdm(events, unit="events")
    progress_bar.set_description('Cleaning')
    
    for event in progress_bar:
        count += 1
        delta_ts = event['ts']-last_ts
        mask   = np.multiply(mask, math.exp(-(delta_ts)/tau))
        
        # keep track of active regions
        x_bounds = (max(0, event['x']-R), min(camera_size[0], event['x']+R+1))
        y_bounds = (max(0, event['y']-R), min(camera_size[1], event['y']+R+1))
        mask[y_bounds[0]:y_bounds[1], x_bounds[0]:x_bounds[1]] += 1
        
        if count % 1000 == 0:
            progress_bar.set_postfix(filtered_evs=(1.-len(filtered_events)/count))
        
        if mask[event['y'], event['x']] > val or count < 200:
            filtered_events.append(event)
            
        last_ts = event['ts']
    
    return np.array(filtered_events)

# =============================================================================
#                   Event Frame manipulation : Resizing
# =============================================================================

def downscale(events, factor=2, camera_size=None):
    """
        Downscales the image by the given factor. 
        
    Parameters
    ----------
    events : np.array
        structured array with fields (x,y)
    factor : int, optional
        the downscale factor must perfectly divide the height and with of the 
        image, otherwise it will raise an error., by default 2
    camera_size : tuple, optional
        Camera size will be assumed from events, if different, it must be 
        specified with this parameter as (width, height), by default None

    Returns
    -------
    np.array
        the input structured array modified so that the resulting image from 
        events is downscaled by the given factor.
    """
   
    if camera_size is None :
        width = np.max(events['x']) + 1
        height = np.max(events['y']) + 1
        camera_size = (width, height)
    
    if camera_size[0]%factor != 0 or camera_size[1]%factor != 0:
        msg = ' the downscale factor must perfectly divide ' + \
            'the height and with of the image'
        raise ValueError(msg)

    else :
        #new_size = map(lambda x: x//factor, camera_size)
        new_x = events['x']//factor
        new_y = events['y']//factor

        return np.rec.fromarrays([new_x, new_y, events['ts'], events['p']], 
                dtype=event_dtype)
    