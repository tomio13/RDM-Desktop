# configuring the RDM-desktop
The default location is either:
c:\%USER%\AppData\Local\rdm\_project
or
/home/%USER%/.config/rdm\_project

It also creates a default configuration, which can be later edited by the user.
The configuration is a YAML file, it contains a description of the folder tree,
the search pattern for the yaml files, and a default editor command.

# Editing
This file is a standard yaml file, one can edit with any text editors.
It is UTF-8 encoded, most modern systems have no problem with it. It also means
that international characters are accepted.

# save config
This sets whether the user profile is saved. If not set or set to false,
it would not get saved, Such may be a good idea when running a mobile version
on an external storage.

# userID
here you can add the user name that can be also used in templates.

# projectDir
the location of all projects. Possibly an empty folder to start with,
here you will find every experiment / sample you have created. Make sure this
folder is backed up regularly.

# projectsTitle
What to display as a title for Projects.

# readme
the name of the read-me file generated for every new folder.

# editor
Notepad ++ works excellent on Windows, Vim, SciTE or anything similar on
Linux. If you find something small and fast with YAML capabiltity, it will
help you editing or checking your records.

## use form
if set to true, the program tries putting together the full record,
just like for uploads, and calls the form maker to provide a nice GUI.
This way one cannot edit fields which are not forms (have no type element).

# filemanager
On windows this is explorer, on Linux it pulls the default, but you
can change it to what you like. The 'Open' button in the folder view
calls this that you can have direct access to the underlying folder.

# chemicals and equipment
These folders are for future use. Users can store here files describing
chemicals and equipment, which are across projecst. Then link them to experiments.

# Folder sturcture
Within projects, several folders can be placed in a hierarchy.
Every project has a subfolder, where the actual samples are stored,
within which then experiment descriptions are placed in YAML files.

To make this flexible, a set of variables contain lists, addressing
the levels of this structure.

# searhTargets
defines what we find on the levels. The bottom one should be 'file', meaning
here we use the form builder to make the yaml files.
The others are set to 'dir', so the folder listing window will work on them.

# searchNames
defines how these levels are called. Currently it is project, then sample, then
experiment.

# searchFolders
defines if we want to use a specific subfolder for the next level.
This folder must be defined in the corresponding folder list template one
level higher, or we have a problem.

Currently every project is loaded from the folder defined in projectDir,
then every sample is looked for in the Data folder under a given project.
The experiments files written into the sample folders directly.
This is why the default set is:
- ''
- Data
- ''

# searchPattern
the pattern used to find what to display. For folders, it is not used,
but for files you can specify either the beginning of file names, or the end.
Default is 'yaml$' meaning any files ending with a yaml extension are picked.
(This is no regex for speed and simplicity, but s simple string match either
at the start of end of a file name.)

# ignore
A list of folder names, which will not be listed in a folder view.
This allows to have extra information among the projects for example,
which will be not used for projects themselves.

# templateDir
where are the templates? It is relative to the folder where the python
code resides. By default a set of tempaltes are available, which may/should
be extended for your own needs.

# default template
In the defaultTemplate field we have the templates for the readme files
for the folders, and a default template for experiments.
This latter is appended before the selected template for every experiment.

# templates
is another set of templates for folders, defining what subfolders to be
created. This is a simple list of a relative path tree. Every folder is
created with all intermediate folders needed.

# server
Variables as default for upload to servers.

## server
the https link to thes server

## token
the token string of the user to access the server

# version
It is used to check if there was a change in the template design,
and the template fields shuold be updated.
Such an update will add new fields, but not change existing ones.

If you need to reset the configuration, simply delete or rename the file.
It will be recreated at next start of the program.

# If you ever need a different default
you have to edit the [project_config.py](../python/rdm_modules/project_config.py) file
in the get_default_config() function.
However, do not change field names, because they are used in various functions
of the code.

# example content of config
on a Linux box

``` yaml
chemicals: /home/john/Projects/Chemicals
defaultTemplate:
- readmeProject
- readmeSample
- defaultForm
editor: scite
equipment: /home/john/Projects/Equipment
filemanager: xdg-open
ignore:
- References
projectDir: /home/john/Projects
projectsTitle: Projects
readme: readme.md
searchFolders:
- ''
- Data
- ''
searchNames:
- project
- sample
- experiment
searchPattern:
- ''
- ''
- yaml$
searchTargets:
- dir
- dir
- file
server:
  server: ''
  token: ''
templateDir: ../templates
templates:
- folderlist
- ''
- ''
userID: J. Doe
version: 0.3
```
