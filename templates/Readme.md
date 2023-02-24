# tempaltes
These files define the content of the forms to generate
reports of specific experiments.
There are three main sets of files here:
- readme templates
- default template
- experiment templates

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

label, unit:
  type: "text|numeric|integer|list|numericlist|file|select|checkbox|url|date|subset"
  description: "documentation text"
  options: "a help description about the field"
  value: "optional default value"
  required: true/false -- whether this field is mandatory

A file field can be one or more files, each a relative path from the current sample folder.

# types
Well, there is a nice list of them already, see the Readme.md in the python folder.

