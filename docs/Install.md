# how to install
Currently the key components are in the python code.

# python part
First get python from [the Python website](https://www.python.org),
or from your Linux distribution using your package manager.

Make sure that you have:
- Tkinter
- pip
- set environmental variables

set during installation. The latest is just to play in the console 8).

## On windows
you can run the installer, then in a command terminal (win-button+R
type cmd or powershell, then ENTER), run
```
pip install pyyaml
pip install requests
```
### Role of the packages
- pyyaml to handle yaml text files we use as templates and documents
- requests is a high level HTTP(S) protocol handler used for upload

## alternatively: use the exe
An executable is generated packing together the python interpreted and
libraries with the source code, using pyinstaller.

The code is super simple, run in the python folder as:
```bash
pyinstaller -F ./rdm_project.py
```

The resulted exe file requires that the icons folder is in the same
subfolder, and the templates are one folder up. In the zip file this
is all packed up in a simple folder tree, so one can extract and use
the resulted program as is.

## On Linux
python is most probably installed by your system, just make sure you
also have the above packages installed (with pip if needed).

## get the source
simply in the main repository, get the code as a zip file, and unpack it
somewhere you can always find it.
In the python folder, start the RDMr\_project.py file, and it should
work out of the box.

That is, in a terminal you can:
```bash
cd To_your_folder
cd python
python ./RDM_project.py
```
or just convert it to a bash starter script.

# C part
this is completely experimental, and in a very early stage, most
components missing.

## dependencies:
- fltk
- libyaml
- libjson (future)

and a C++ compiler for all this...

# Configuration
After the first start, the program creates a Projects folder and
a default configuration file for the user.
On windows this is in: c:/Users/%(current user)/AppData/Local/rdm\_project
on others in: /home/${User}/.config/rdm\_desktop
and within the config.yaml file.

Why is this interesting? If the program could not create the Projects
folder, you may want to tune the projectDir entry to a folder that you can
write and use for this purpose.
You also may want to correct your user name in the userID field.

Further information [about configuration you can find here](./Configuration.md)
