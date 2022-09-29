# create a folder tree
based on an input project name, and the subfolder names defined in the folder.txt
file.
It takes an argument -c to set that file name to anything else, but pops up
a widget for the project name.

usage:
```
    project_dir project_short_name -c folder_list.txt
```
# Makefile
a short make file is made after using malloc() and free() started making
trouble during running the program.
Set a bit of optimization and especially checking for memory leaks. This has
a small code incorporated that throws some information about potential
memory leaks during execution.

This helps cleaning the code.

The output goes into the ../bin folder.

# tested it working
from various paths, with files etc...

# current usage idea
call it as an external process with path to the folder and the list file.
