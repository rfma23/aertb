The Library
==================

Description
---------------

This library intends to be a minimal tool for loading and manipulating events in Python from 
files with common event-camera file extensions .

See the project on `PyPI <https://pypi.org/project/aertb/>`_ or do :code:`pip3 install aertb`

Usage
---------------
.. code-block:: python

   from aertb.core.loaders import PolarityEventFile
   file = PolarityEventFile('../myFile.myext') 
   # handle every supported file extension
   # then file.header, file.get_events() ...

Supported extensions:

 - :code:`.dat`: N-Cars / Prophesee Cameras
 - :code:`.bin`: N-MNIST, N-Caltech101
 - :code:`.aedat`: PokerDVS, PostureDVS
 - :code:`.mat`: DVS-Barrel
 
It also make the process of loading and iterating HDF5 files easier.

.. code-block:: 

    from aertb.core import HDF5File
    dataset_train = HDF5File('TRAIN.h5')
    train_iterator = dataset_train.iterator(n_samples_group=10, rand=23)
    for sample in tqdm(train_iterator):
        # do something with sample.events, sample.label or sample.name


Example: making a GIF

.. code-block::

    from aertb.core import HDF5File, make_gif
    file = HDF5File('../DVS_Barrel.hdf5')
    sample = file.load_events(group='moving', name='11')
    make_gif(sample, filename='sample_moving.gif', camera_size=(128, 128), n_frames=480, gtype='std')


The library also includes a command line interface for converting files from a given extension to hdf5, as well as gif
making capabilities for easy visualisation of the files.

Notebook Examples
---------------