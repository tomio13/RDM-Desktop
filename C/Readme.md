# C sources for the RDM-Desktop project
The aim is to write relatively small, fast and simple elements to handle problems
related to research data management.

# Data model behind
Every configuration file is written in plain text, possibly in a simplified
YAML system. Traditionally such files translate very well to python dict
structures, which natuarlly do not exist in C.
But can be reasonably easily done.

## Key structures
the following structures allow building up records and record trees.
They are defined in the lists.h file:

### r\_string\_t
a simple string structure composed of a char\* pointer and an integer length.
Proper function allocate and free up the content.
At this point it is safe to plan every value being string, not caring much
about numbers. If a number is used, we can translate using float().

### record\_t
A record element is
* a key string
* a value.
  * The value can be either a string
  * a list of records
* previous and next are pointers to other records (forming a list)
* record type, an enum indicating what type value is

This way we have the versatile branching ability of python dicts. The trick
is to use a void pointer and a type variable.

There are convenience functions to:
* go to the first element of a list
* go to the last element of a list
* find a key in a list, starting from a given point
  * this can be used in iterations to find all hits
* find the length of a list (not going into branches)
* find an index of the current element
* clear and delete records
* delete lists (freeing up memory)


### record\_type\_t
An enum listing the possible values of the record. Possibilities are:
* empty
* numeric
* string
* multiline string (for longer content)
* child list


The whole project can build around these structures, since this can be any entry to
the ELN, information to the GUI, etc.

## Functions on records and strings
are defined in the lists.c file, declared in lists.h.
Allocation is done by the new... functions, freeing up memory and erasing structures
by the delete... functions.

### clearing up content
The delete\_string, delete\_record, delete\_list functions erase the content of the
given object and free up the memory.

### array functions
It is possible to list up the pointer to the list elements or even strings within those
using the array functions. These allocate the pointer arrays, fill them up, or erase them.
However, these do not erase the content of the records indicated by the poitners, or change
the content of the lists.
They are intended for the case when one has to sweep through the list element multiple times,
and especially when elements randomly have to be accessed based on their position in the list.
The list array ends with a NULL pointer to make sure one can detect the end. The key or value
arrays have the problem that they may contain NULL pointers (e.g. if a value is not a string
but another list). To check their length, use the length of the list.
The list should not be changed while you are using the arrays on that list.

