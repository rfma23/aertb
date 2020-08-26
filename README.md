# AER-toolbox
This library intends to be a minimal tool for loading events from files with common event-camera file extensions into
Python.

See the project on [PyPI](https://pypi.org/project/aertb/) or do `pip3 install aertb`

### Usage
```py
from aertb.core import FileLoader

datLoader = FileLoader('dat') # 'bin', or 'aedat'
datLoader.load_events('../example_data/dat/cars/obj_004414_td.dat')
```

Supported extensions:

 - `.dat`: N-Cars / Prophesee Cameras
 - `.bin`: N-MNIST, N-Caltech101
 - `.aedat`: PokerDVS
 - `.mat`: DVS-Barrel
 
It also make the process of loading and iterating HDF5 files easier.
```py
from aertb.core import HDF5File

dataset_train = HDF5File('TRAIN.h5')
train_iterator = dataset_train.iterator(n_samples_group=10, rand=23)

for sample in tqdm(train_iterator):
    # do something with sample.events, sample.label or sample.name
```

Example: making a GIF
```py
from aertb.core import HDF5File, make_gif

file = HDF5File('../DVS_Barrel.hdf5')
sample = file.load_events(group='moving', name='11')
make_gif(sample, filename='sample_moving.gif', camera_size=(128, 128), n_frames=480, gtype='std')
```

The library also includes a command line interface for converting files from a given extension to hdf5, as well as gif
making capabilities for easy visualisation of the files.

### Opening the CLI
  1. If the install with pip worked perfectly, you can now type `aertb` in a terminal window and the CLI will open.
  
  2. If you are installing it from Github: download you should download the project from github and follow the following
  instructions:
        - a) `git clone ...`
        - b)  Create a virual environment, if venv is not installed run `pip install virtualenv`,
                  then `python3 -m venv aertb_env`
        - c)  Run `source aertb_env/bin/activate`
        - d)  Run the following command: `pip install -r requirements.txt`
        - e)  Open the cli with `python3 .` or with the `__main__.py` file

### Using the CLI
  1. Once the CLI is open you get a a similar output on your terminal:
    ![Cli Animation](https://github.com/rfma23/aertb/raw/master/images/aertb_cli_shell.gif)
  2. type `help` to see supported commands and `help <topic>` to get more info of the command

### Examples:

#### Creating an HDF5 out of a directory
```
tohdf5 -f 'example_data/dat' -e 'dat' -o 'mytest.h5'
```
The recommended directory shape is  :

     |--Parent (given as parameter)
          |-- LabelClass1
              |-- SampleName1
              |-- SampleName2
              |-- ....
          |-- LabelClass2
              |-- SampleName1
              |-- SampleName2
              |-- ....
          |-- ...

And we suggest that train and test are kept as separate folders so they translate 
to two different files
####  Creating an HDF5 out of a single file
```
tohdf5 -f 'example_data/bin/one/03263.bin' -o 'mytest2.h5'
```


####  Creating a gif out of a given file
```
makegif -f 'example_data/prophesee_dat/test_23l_td.dat' -o 'myGif.gif' -nfr 240 -g 'std'
```

 ![Gif Animation](https://github.com/rfma23/aertb/raw/master/images/myGif.gif)


### Exiting the CLI:

1. type `quit`
2. Exit virtual environment: `$ deactivate`
