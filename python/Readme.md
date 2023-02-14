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

