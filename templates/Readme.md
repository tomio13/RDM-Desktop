# tempaltes
These files define the content of the forms to generate
reports of specific experiments.
There are three main sets of files here:
- readme templates
- default template
- experiment templates

# default_configuration
is a well commented configuration file, where administrators
can customize the settings for an installation.
It contains all default fields either as they are or commented
out.

# readme templates
These are to template the Readme.md files for new projects or
samples.

# default template
The defaultTemplate is a YAML file with fields which will be
appended to the beginning of every experiment form.
Typical content is like the sample ID, sample descriptin, link
to the sample file, which is common for each experiment.
Or the user ID and creation date/time.

# experiment templates
These are a YAML file, defining every field to be added.
Practially every field starts with its name or key, which is
also the label of the entry.
If only a value provided after this, it is taken over to the
result automatically.
Some fields can be substituted in here automatically, such as
%u to user ID from the configuration.

Otherwise every entry has the following structure:

label [unit]:
  type: "text|numeric|integer|list|numericlist|file|select|checkbox|url|date|subset"
  doc: "documentation text"
  options: "list of alternate values for select fields"
  value: "optional default value"
  required: true/false -- whether this field is mandatory

A file field can be one or more files, each a relative path from the current sample folder.

# types
Well, there is a nice list of them already, see the Readme.md in the python folder.

# description -> doc
Changed description to doc, because this way we can use 'description' in field names.
'Doc' is not probable to show up as such (it would be docs anyway).

# units
Now, indicate units in the name of the fields at the end in (), like:
'test element (m):'

