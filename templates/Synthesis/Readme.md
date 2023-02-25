# Synthesis
can have many forms, spreading from a simple mixing of chemicals
towards processes requiring usage of equipment, to stirr, heat,
provide gas atmosphere, illumination, etc.

# Steps
In general, it is a good idea to report a single step at a time.
Here we refer to a step as one taking one or more components at once
or in a time interval, and results some kind of combination, possibly
a new chemical.

# Chemicals
Chemicals can be collected in a Chemicals folder outside of the projects,
each describing one material boought from a company, stored in a specific
location. Often such a thing is referred as a batch.
Using pubchemTools (available via Pip) one can get a standard chemical
information from pubchem, and can save it easily as a dict. This is a
simplified version of the full pubchem record, but it is more human
readable, and can be directly exported as a YAML file.

# templates
While we can construct a generic template for wet chemistry, many
will be needed to cover all kinds of sample preparation routes.
In general, we can consider procedures such as:
- plasma activation
- coating
 - dip coating
 - spin coating
 - drop casting
- freeze-drying
- recrystalization
- milling (e.g. in achat mill)
- etc.
all as preparation /synthesis experiments.
