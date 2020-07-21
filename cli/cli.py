#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================

__author__      = "Rafael Mosca"
__email__       = "rafael.mosca@mail.polimi.it"
__copyright__   = "Copyright 2020 - Rafael Mosca"
__license__     = "MIT"
__version__     = "1.0"

# =============================================================================

from click_shell import shell
import numpy as np
import logging
import click
import os

from aertb.core import FileLoader
from aertb.core import make_gif

# =============================================================================
#                     SHELL
# =============================================================================
@shell(prompt='[AER-TB] $ ', intro=click.style("""
 █████╗ ███████╗██████╗    ████████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗   ╚══██╔══╝██╔══██╗
███████║█████╗  ██████╔╝█████╗██║   ██████╔╝
██╔══██║██╔══╝  ██╔══██╗╚════╝██║   ██╔══██╗
██║  ██║███████╗██║  ██║      ██║   ██████╔╝
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      ╚═╝   ╚═════╝ 
                                            
> An Address Event Representation toolbox for different file extensions.
> Type 'help' to see supported commands.
> Project by Rafael Mosca - https://rfma23.github.io
"""))
def aertb_shell():
    pass


# =============================================================================
#                     GLOBALS
# =============================================================================

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.FileHandler("../aer_toolbox.log")])

# =============================================================================
#                     COMMANDS
# =============================================================================
@aertb_shell.command()
@click.option("-f", "--file", type=str, default='/',
              help="Defines the location of the parent directory")
@click.option("-e", "--ext", type=str, default=None,
              help="Defines the file extension")
@click.option("-o", "--out", type=str, default='my_dataset.hdf5',
              help="Defines the path and name of the output file")
@click.option("-p", "--polarities", type=list, default=[0,1],
              help="Defines how the polarities are encoded")
def tohdf5(file, ext, out, polarities):

    logging.info(f'Calling tohdf5 with params {[file, ext, out, polarities]}')

    if ext is None:
        path_plus_filename, file_extension = os.path.splitext(file)
        if len(file_extension) > 1:
            ext = file_extension[1:]
        else:
            msg = 'Could not infer file extension, when processing directories ' \
                  'please specify an extension with the -e flag'
            click.secho(msg, bg='yellow')
            return

    fl = FileLoader(ext)
    fl.create_hdf5_dataset(out, file, polarities)
    click.secho('HDF5 file created successfully', bg='green')


# ------------------------------------------------------------------------------
@aertb_shell.command()
@click.option("-f", "--file", type=str, default='/',
              help="Defines the location of the parent directory")
@click.option("-o", "--out", type=str, default='my_dataset.hdf5',
              help="Defines the path and name of the output file")
@click.option("-e", "--ext", type=str, default=None,
              help="Defines the file extension to process. Should not include a "
                   "leading dot")
@click.option("-p", "--polarities", type=str, default='both',
              help="Defines the polarities considered {pos, neg, both}")
@click.option("-g", "--gtype", type=str, default='decay',
              help="Defines the type of gif visualization considered {decay, std}")
@click.option("-nfr", "--nframes", type=int, default=8,
              help="Defines the number of frames produced for the gif")
def makegif(file, out, ext,  polarities, gtype, nframes):

    logging.info(f'Calling makegif with params {[file, ext, out, polarities, gtype]}')

    if ext is None:
        path_plus_filename, file_extension = os.path.splitext(file)
        if len(file_extension) > 1:
            ext = file_extension[1:]
        else:
            msg = 'Could not infer file extension, when processing directories ' \
                  'please specify an extension with the -e flag'
            click.secho(msg, bg='yellow')
            return

    fl = FileLoader(ext)
    events = fl.load_events(file, [0, 1], to_secs=True)

    x_max = np.max(events['x']) + 1
    y_max = np.max(events['y']) + 1

    polarity_map = {'pos': {1}, 'neg': {0}, 'both': {0,1}}

    viz_events = np.array([ev for ev in events if ev['p'] in polarity_map[polarities]])
    make_gif(viz_events, out, camera_size=(y_max, x_max), gtype=gtype, n_frames=nframes)

    click.secho('GIF file created successfully', bg='green')


# =============================================================================
if __name__ == '__main__':
    aertb_shell()