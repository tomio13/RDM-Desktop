# Templates
There are three types of templates used in the RDM-desktop:
- one describing folder trees
- one for read-me documents
- yaml documents for generating forms and their outputs (yaml)

All templates are in the templates folder, but the files
are stored without extension, so the template opening GUI will
not pick them up when one is working on new experiments.

# folder tree
These files are simple text files, with a relative path in each line
For example:
```
Data
# usage:
# Data/Example_sample
# Data/Example_sample/Example_analysis_0
# Data/Example_sample/Example_analysis_1
Figures
Organizational
Publications
...
```
The # allows for comments between the lines to make the template
more readable.

# read-me templates
These documents are MD documents, used as they are.
Field substitution is performed on them before they are saved
to the output.

# field substitution
A simple function in project_config, called replace_text() can replace the following:
- %u    user ID from the configuration data
- %d    current date in ISO 8601 format as YYYY-mm-dd
- %D    current date and time (YYYY-mm-dd HH:MM)
- %1 - 4:   elements of the path, getting as:
  - %1      name of the project folder
  - %2      'Data' according to the configuration
  - %3      name of the sample folder

These substitutions apply to the read-me templates and to fields
without type (form element) definition in the experiment templates.

# experiment templates
These YAML files may contain several entries. There are two main groups:
key-value pairs without a subtree are taken over as is, and the substitution
applies to the values.

## form elements
These are small trees themselves, constructed as:

```YAML
field name, unit:
  type: textd$|numeric|int|list|numericlist|select|checkbox|file|url|subset
  doc:  documentation / description of this field
  value: optional default value
  required: true/false
```

The type can be one of:
- text              a line of text (usually short)
- multiline         a multiline text area where enter allows for line breaks
- numeric           a number
- integer           an integer number
- list              a comma delimited list of text values
- numericlist       a comma delimited list of numbers
- select            a selection menu, with a single choice. The options
                    subfield contains a list of possible values to select from
- multiselect      the same as select, but multiple selection
- checkbox          a simple yes/no (true/false) selector
- file              a file picker for one or more files;
                    If the file name is typed as a comma separated list,
                    the file does not have to exist (user can add them later this way)
- url               a text field for an url
- subset            a subset: grouping a new list of menu items to be
                    added dynamically. In the main window only the number
                    of fields and the number of entries are displayed,
                    with a button '+' to add new entries, and 'show'
                    to see the existing ones.
- date              a date time spin button widget starting with the current time.

The value fiels allows usually to add a default value. (not for the
subset)

The required field sets if a field is requited, thus empty value will not
be accepted.

# examples
A couple of example templates are available in the templates folder,
you can copy them for starting a new one.
