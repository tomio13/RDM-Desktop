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
(nano for non Windows, Notepad for Windows) for being filled out by the user.
The template only defines some kind of initial value and form.
The user is free to edit thie file and use it in any sinful way.

# working on YAML files
If a new YAML file is to be created (on the bottom level of the folder tree),
a template has to be selected after defining the name of the new file.
The form editor is opened with this template, and once the content is
submitted, the YAML file is created.
If the configuration is set so, the resulted YAML file does not contain the
field definition and documentation, in order to minimize storage.
However, these are needed for future editing or uploading / publishing, to
provide there a full record, which can be tested against expectations (standards).

If the configuration setting 'full record' exists and is set to true,
then every detail is saved in the file, and it can be used without the template.
The resulted file is more complicated looking, but more self-standing, so this setting
is set by default.
The same setting gets saved into the file as well, to ensure the program recognizes
this state even when the configuraiton is changed later.

## help
if F1 is pressed when working with the form widget, a help window will pop up,
containing every read-only field (not displayed in the form) and all doc-strings
from the template to help understanding the form.

## Opening a recorded experiment
The configuration file contains a field: 'use form' set true. This instructs
the program to regenerate the form GUI widget opening the file. If the editing
is interrupted using e.g. escape [ESC], then nothing is done.
If the form is resubmitted, the original file is overwritten.

If there the setting is false, or there is a mismatch of the template
(different version date or file not found), then the text editor set in
the configuration is called up with the file.

# upload
On the level of YAML files, a new icon appears at the bottom of the window,
indicating upload to a server.
This brings up a small menu for defining the server URL (e.g. https://server:port/)
and the security token provided for the current user.
Currently ElabFTW is supported, but in the future the user can select
from the supported server types.
At the end of the upload, an uploaded field is added to the record,
describing the new record in the ELN.

## attachments
The uploader can also take the files specified in the record and upload
them as attachments. The example ElabFTW uploader does this, but in
the case of more than 10 files, it recommends doing a manual upload using
a zip archive.
RDM record YAML files will not be uploaded, they should be linked within the system.
These are detected based on being:
- a file with yaml or yml extension
- and an existing file
- and a valid YAML file that contains:
 - a dict of dicts (all field is a dict)
 - fields with the name:
  - user
  - created
  - template
  - template version
If any of these is missing, the file gets attached.
