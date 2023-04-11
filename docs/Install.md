# how to install
Currently the key components are in the python code.

# python part
First get python from [the Python website](https://www.python.org).
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

## On Linux
python is most probably installed by your system, just make sure you
also have pyyaml installed.

## get the source
simply in the main repository, get the code as a zip file, and unpack it
somewhere you can always find it.
In the python folder, start the RDM-project.py file, and it should
work out of the box.

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
