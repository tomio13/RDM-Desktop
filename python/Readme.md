# python implementation
This is a python implementation and a workspace to develop the concepts in the RDM-desktop project. These ideas then to be transfered to C for improved performance and smaller program size. However, it is also critical here to keep things as simple as possible.

# Tkinter: Tcl/Tk
I employ Tkinter because this is typically installed in all basic python installs.
The resulted GUI is still in the few MB size (currently about 6 MB)

# Functionalities
- a project folder generator
- a widget that lists projects, samples and experiments
- configuration loader / generator / saver
- widget to turn templates to forms, save experiments --> under construction

# project\_config
basic functions to get a configuration. Default location is either:
c:\%USER%\AppData\Local\rdm\_project
or
/home/%USER%/.config/rdm\_project

It also creates a default configuration, which can be later edited by the user.
The configuration is a YAML file, it contains a description of the folder tree,
the search pattern for the yaml files, and a default editor command.

If the user has e.g. ghost\_writer on the machine, change the default editor!
Changing this file requires a restart of the program.

# form\_from\_dict
A set of widgets to operate a form editor. It takes a dict template to build
a form.
For a start, all numeric, list and text fields are the same. There is a multiline
text entry possible and a file selector for adding links.
This is not complete yet, features missing:
 - field validation (at least as numeric, date, list)
 - multiple file selection

# main\_window
the main window widget, a limited file explorer tool to list projects,
their folders and files within. The listed element type is controlled
by the searchTargets element (dir or file), the subfolders to be listed
in the searchFolders.

# RDM\_project
is the main program, it actually callst he main window.


# Installation
The program requires no special installation.
Copy the repo, and run the RDMi\_project.py file in the python folder.
The GUI should start and deploy the default configuration for the user.

# Requirements
python: 3.x (tested wtih 3.10)
pyyaml: a default python yaml library

All other libraries should be part of the standard python install.
No special environment is needed, so you can save yourself from things like
anaconda, conda, docker, etc.

# Libraries used
- os
- sys
- time
- subprocess
- yaml
- tkinter

# field types
- text          single line text
- multiline     multiline text field
- numeric       any number
- integer       only integer numbers
- url           a web URL (https://...)
- list          comma separated list of values
- numericlist   comma separated list of numbers
- file          relative link to a file
- checkbox      a true/false value as check box
- select        pick one from a list (text)
- multiselect   pick one or more from a list (text list)

# dynamic values
Template fields which are not part of the form may have some
substitution values, such as:
- %u            the userID field from the configuration
- %d            the current date in ISO-8601 format
- %D            the current date and time and time zone in ISO-8601 format
- %1, %2, %3    the part of the relative path within the project
                for a project %1 is the project name provided (short one)
                for an experiment %3 is the experiment short name provided

This substitution is also applied to the readme templates.

# configuration
The first start of the program drops a default config.yaml file
either as:
- /home/.config/rdm\_project/config.yaml
- c:/Users/%USER%/AppData/Local/rdm\_project/config.yaml

This file defines several parameters, which will affect how the
program works. Please do not alter the folder configuration except
if you really know what you are doing.

However, you should change:
- userID: the name saved to new entries
- editor: it is Notepad on Windows, nano on other systems, change it
  to something you like (I like Notepad++ for example).
  On windows, find your favorite editor, and add the full path here, but
  use '/' instead of '\'.

Do not change the version, because the software uses it to update the
missing fields if a new version comes out.
