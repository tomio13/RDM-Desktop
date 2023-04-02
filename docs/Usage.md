# Main concept
The GUI provides two main elements:
- a window with listing for seeing project content at various levels
- a form to describe experiments

# Main window
The main window opens into the projects folder, listing all projects
(folders themselves) to the user. Double clicking on any of them will
open a new window with its content.

The listing is restricted to folders or YAML files only, except those
listed as exception in the configuration.

Each project contains folders for samples or processes depending on
how the user is utilizing this tool (see the [configuration](Configuration.md)
as well).

There are two icons on the bottom of the window:
- one with a folder symbol to invoke the file manager in the current folder
- one to add new elements to the folder

# opening the file manager
will call the default file manager of the system (e.g. explorer in Windows)
so the user can browse and work on the content of the files.

# adding new element
First a name is requested for the new folder, then a read-me is created
based on the corresponding template. This file is opened in the default editor
for being filled out by the user.

# working on YAML files
If a new YAML file is created (on the bottom level of the folder tree),
a template has to be selected after defining the name of the new file.
The form editor is opened with this template, and once the content is
submitted, the YAML file is created. The user can open it in the default
editor double clicking on its name.

# upload
On the level of YAML files, a new icon appears at the bottom of the window,
indicating upload to a server.
This brings up a small menu for defining the server URL (e.g. https://server:port/)
and the security token provided for the current user.
Currently ElabFTW is supported, but in the future the user can select
from the supported server types.
At the end of the upload, an uploaded field is added to the record,
describing the new record in the ELN.
