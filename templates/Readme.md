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
The idea behind is that there is a very basic set defined in
the python code itself. That is updated from this file, and then
further updated with the content of the user's copy in the default
user configuration folder. If this last one is missing, then this
default file provides system wide configuration. Also useful for
an instance running from a USB drive or a central network drive,
when local copy of the configuration should not be saved.

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

```yaml
label:
  type: "text|numeric|integer|list|numericlist|file|select|checkbox|url|date|subset"
  doc: "documentation text"
  options: "list of alternate values for select fields"
  value: "optional default value"
  required: true/false -- whether this field is mandatory
  # the next two are only for numeric fields
  units: ["m", "cm", "mm"]
  unit: "m"
```

A file field can be one or more files, each a relative path from the current sample folder.

# types
Well, there is a nice list of them already, see the Readme.md in the python folder.

# description -> doc
Changed description to doc, because this way we can use 'description' in field names.
'Doc' is not probable to show up as such (it would be docs anyway).

# required
If set the form does not accept a submission until a value is provided.

# value
a default value for a field.

# units
for numeric elements we can have units defined as:
  units: ["m", "km"]
  unit: "m"

Here the unit is the default value, it has to be one in the list of units.

