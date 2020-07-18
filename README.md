# AER-toolbox
This library intends to be a minimal tool for loading events from files with common event-camera file extensions into
Python.

```py
from aertb import FileLoader

datLoader = FileLoader('dat')
datLoader.load_events('../example_data/dat/cars/obj_004414_td.dat')
```

The library also includes a command line interface for converting files from a given extension to hdf5, as well as gif
making capabilities for easy visualisation of the files.

The file extensions supported are:
   - `'aedat'` : AER 2.0 (Delbruck et Al.)
   - `'dat'` : Prophesee
   - `'bin'` : Orchard et Al. 

### Opening the CLI
  1. In order to open it, navigate to path where the library is installed, in case of problems download you should 
  download the project from github (`git clone https://github.com/rfma23/aertb.git`) and follow the following instructions:
     - Create a virual environment (if not installed run `pip install virtualenv`)
              by typing `python3 -m venv aertb_env`
     - On Linux/MacOS run `source aertb_env/bin/activate`
     - Run the following command: 'pip install -r requirements.txt'

  3. Run `python3 .` or execute the `__main__.py` file

### Using the CLI
  1. Once the CLI is open you get a a similar output on your terminal:

  2. type `help` to see supported commands and `help <topic>` to get more info of the command

#### Examples:

##### Creating an HDF5 out of a directory
```
tohdf5 -f 'example_data/dat' -e 'dat' -o 'mytest.h5'
```
Directory should be structured:

    |--Parent (given as parameter)
        |-- A
            |-- File1
            |-- File2
            |-- ....
        |-- B
            |-- File1
            |-- File2
            |-- ....
        |-- ...
##### Creating an HDF5 out of a single file
```
tohdf5 -f 'example_data/bin/one/03263.bin' -o 'mytest2.h5'
```

##### Creating a gif out of a given file
```
makegif -f 'example_data/dat/cars/obj_004416_td.dat' -o 'decay.gif' -nfr 12 -g 'decay'
```
there are two possible modes selected with the `-g` flag:
 - `'decay'` to achieve a temporal context with exponential decay
 - `'std'` to get the standard black (negative events) and white (positive events) representation
### Exiting the CLI:

1. type `quit` on the CLI
2. Exit virtual environment, from terminal type `deactivate`
