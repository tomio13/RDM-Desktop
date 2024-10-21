# Design and internal structure

## RDM data
The RDM-desktop builds on using python dicts (like PHP arrays) as RDM records.
These are the forms created from templates, filled out then sent to upload.

Every keyword in the form represents a field. Either as a direct key:value
pair, or a sub-dict with all information related, such as:

|   field   |               meaning                                 |
|-----------|-------------------------------------------------------|
| key       | name of the field (dict key)                          |
| type      | type of the field (e.g. text)                         |
| doc       | documentation of the field                            |
| units     | list of possible units for numeric values             |
| value     | default value or filled out value                     |
| :::       | can be a sub-dict with key: value pairs for subsets   |
| unit      | the default unit, one of units                        |
| required  | is this field mandatory?                              |
| options   | list of optional values for select                    |
| form      | a sub-dict defining fields for a subset               |

Other keys are not checked for, and not interpreted, but possible.

## form elements
these are TK-widget based classes to define form elements. Every element
is defined by calling a constructor and providing:
| variable  |                       meaning                      |
|-----------|----------------------------------------------------|
| parent    | parent class, a frame                              |
| label     | title of the widget, the key of the dict field     |
| others... | optional parameters specific to the widget         |

Others can be like a subdir for a file picker, or fle type, but an editor
for a multiline text...

All widgets have:
- required: a Boolean field to be set or unsed
- grid(): to position them in the TCL/TK window structure
- get(): to receive their final value
- set(value): to set their default value

Even for cases where it is not really reasonable, like a radio-button.


## generic window class
To have a uniform and relatively easy to handle window, make a window class.
It is a generic class, which invokes a Tk.window, and adds three frames into it.
The top frame is for label and some buttons if needed.
The middle one is the acual content, e.g. list of files, or all kinds of form
elements.
The middle frame can have a scroll-bar, in which case it is placed within a canvas
widget, with mouse wheel bound for scrolling.

The last one is for action buttons, like edit, submit, etc.

This way I can spare some typing and it is enought to decorate these.


