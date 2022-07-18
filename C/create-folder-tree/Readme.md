# create a folder tree
based on an input project name, and the subfolder names defined in the folder.txt
file.
It takes an argument -c to set that file name to anything else, but pops up
a widget for the project name.

# TODO
add some folder name consolidation to remove '/' or '\' from the string, and also
quotation marks, etc.

# compile
at this level, use:
```bash
fltk-config --compile project_dir_cmd.cxx
```
