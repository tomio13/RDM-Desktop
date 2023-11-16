#!/usr/bin/env python
""" Some widget extensionts used in the form builder.
    Collected here for better readability.

    Author:     tomio
    License;    MIT
    Date:       2023-02-26
    Warranty:   None
"""
import os
import time
import tkinter as tk
from tkinter import ttk
# from tkinter.filedialog import FileDialog
from tkinter.filedialog import askopenfilenames
from tkinter import StringVar


class FilePickerTextField():
    """ a small class to build a file picker in the form of
        a text field and a button. The button activates a
        file selector widget, and its results fills the text
        field. The text field is editable.
        Use possibly a relative path.

        Using a text field allows one to enter non-existent
        file names if necessary, but the file picker allows
        easy selection of existing ones with relative paths.
        The widget allows to select more than one files.
    """

    def __init__(self,
                 parent:tk.Misc= None,
                 indir:str='.',
                 extension:str= 'yaml') -> None:
        """ Generate the widget and populate its settings
        """
        if parent is None:
            self.parent = tk.Tk()
        else:
            # this can be a frame or similar, we embed into
            self.parent = parent

        frame= ttk.Frame(self.parent)
        # allow positioning after called:
        self.grid = frame.grid


        self.dir = indir
        self.content = StringVar()
        self.required= False
        self.error= False

        entry = ttk.Entry(
                frame,
                width= 30,
                textvariable= self.content
                )

        entry.grid(
                column= 0,
                row= 0
                )

        button = ttk.Button(
                frame,
                text='Select',
                command= lambda: self.get_file(
                    frame,
                    extension
                    )
                )
        button.grid(column= 1, row= 0)
    # end __init__


    def get_file(self,
                 parent:tk.Misc,
                 extension:str) -> None:
        """ bring up a file dialog and get a file name

            parameters:
            parent:     the parent widget, e.g. frame
            extension:  the file extension to be displayed
        """

        d = askopenfilenames(
                master= parent,
                title='Select file',
                defaultextension= extension,
                initialdir= self.dir
                )
        if d:
            fn = [os.path.relpath(i, self.dir) for i in d]
            # to be able to use the text field, we
            # need a comma separated list of file names
            self.content.set( ', '.join(list(fn)))
    # end get_file


    def get(self) -> str|list:
        """ get the file paht(s) out of the widget, and return
            as a string or list.
            Assumes paths are relative (the get_file above
            does convert the path to relative paths).
            It does not test if a file exists, so users can name
            files they would add later.

            Using the list allows a type check to see if
            multiple files are selected.
        """

        fn = self.content.get()
        if not fn:
            return None

        if ',' in fn:
            fn = fn.split(', ')
            # to allow only existing files we can filter:
            #fn = [f'file:{i}' for i in fn \
            #        if os.path.isfile(os.path.join(self.dir, i))]
            #
            # or the user may specify files which do not exist
            # but do not emit empty elements
            # fn = [f'file:{i.strip()}' for i in fn if i.strip()]
            fn = [i.strip() for i in fn if i.strip()]

            if not fn:
                return None

            return fn

        # return f'file:{fn}'
        return fn
    # end get

    def set(self, data:list)->None:
        """ set the content from a list of file names
        """

        if not data:
            return

        text = ', '.join(data)
        self.content.set(text)
    # end of set
# end FilePickerTextField


class MultilineText():
    """ a multiline text widget with scroll bars on it...
    """

    def __init__(self,
                 parent:tk.Misc= None
                 )-> None:
        """ A Tk text area widget coupled to scroll bars in a frame
        """

        if parent is None:
            self.parent = tk.Tk()
        else:
            # this can be a frame or similar, we embed into
            self.parent = parent

        frame= ttk.Frame(self.parent)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.text = tk.Text(frame,
                            width= 50,
                            height= 10,
                            wrap= 'word')

        self.text.grid(column=0, row=0, sticky='we')
        self.required= False
        self.error = False

        scroll_vertical= tk.Scrollbar(frame,
                                      bg= 'grey',
                                      orient= 'vertical',
                                      command= self.text.yview,
                                      takefocus= True
                                      )
        scroll_vertical.grid(row= 0,
                                   column= 1,
                                   sticky= 'ns')
        self.text.config(yscrollcommand= scroll_vertical.set)

        scroll_horizontal= tk.Scrollbar(frame,
                                        bg= 'grey',
                                        orient= 'horizontal',
                                        command= self.text.xview,
                                        takefocus= True
                                        )
        scroll_horizontal.grid(row= 1,
                                   column= 0,
                                   sticky= 'ew')
        self.text.config(xscrollcommand= scroll_horizontal.set)

        # to allow positioning
        self.grid = frame.grid
    # end __init__


    def get(self)->str:
        """ return the full content of the widget
        """
        v= self.text.get('1.0','end')
        if not v:
            return None

        return v.strip()
    # end of get

    def set(self, content)->None:
        """ set the content of the widget
        """
        if text:
            self.text.insert('END', content)
    # end set

# end of MultilineText


class CheckBox(tk.Checkbutton):
    """ an envelop to ktinter checkbox with a get() to
        read out the value.
    """

    def __init__(self, parent:tk.Misc= None, **kwargs:dict) -> None:
        """ initialize a checkbox widget
        """

        self.parent = parent
        self.error = False
        self.required= False

        if self.parent is None:
            self.parent = tk.Tk()

        self.value = tk.IntVar()
        super().__init__(self.parent,
                         variable= self.value,
                         onvalue= 1,
                         offvalue= 0,
                         **kwargs)

    def get(self)->str:
        """ return back the value of self.value
        """
        return self.value.get() == 1
# end of CheckBox


class EntryBox():
    """ an entry box which can also check its content
        to be: text, file, url, integer, numeric,
        list, numericlist
    """

    def __init__(self,
                 parent:tk.Misc,
                 vartype:str='text',
                 units:list|None= None,
                 **kwarg:dict) -> None:
        """ Initiate an entry widget, based on its type
            units: a list of usable units
        """
        # internally we use strings for any variable
        self.var = tk.StringVar()

        self.type = vartype
        self.error = False
        self.error = False

        self.required= False

        self.parent = tk.Tk() if parent is None else parent
        frame = tk.Frame(self.parent)
        self.grid = frame.grid

        self.entry = ttk.Entry(frame,
                               textvariable= self.var,
                               width= 10,
                               **kwarg)
        self.entry.grid(column=0, row=0)

        if units is not None:
            if not isinstance(units, list):
                units = [units]
            self.units = ttk.Combobox(frame, width=6)
            self.units['values'] = units
            self.units['state'] = 'readonly'
            self.units.set(units[0])
            self.units.grid(column=1, row=0)
        else:
            self.units= None
    # end __init__


    def set(self, value:str|int|float|list, unit:str|None= None) -> None:
        """ Set the internal variable from value
            Use a text tk variable, so convert the incoming
            types to it.

            For numerical fields, we should also receive the unit
            if there is one.
        """
        # since tk does not handle invalid numbers well,
        # we have to take it out of its hands...
        # that would mean that every field is a text field,
        # but if the conversion fails, we make a message and
        # return None. The main FormBuilder then refuses to close

        if value is None or value == '':
            return

        # for the case we got back a [value, unit] list:
        if isinstance(value, list)\
                and self.type  in ['integer', 'numeric', 'numericlist']\
                and isinstance(value[1], str):
            # we set the unit, and leave value as value
            # it should never be a single element list!
            self.unit = value[1]
            value = value[0]

        if self.type == 'list':
            self.var.set(', '.join(value))
        elif self.type == 'numericlist':
            self.var.set(', '.join([str(i) for i in value]))

        else:
            self.var.set(str(value))
    # end of set


    def get(self) -> str|int|float|list:
        """ return the value as a proper python variable
            Handle types:
            string      --> do nothing
            integer     --> convert to integer
            numeric     --> convert to float
            list        --> split by comma and strip
            numericlist --> split, conver to float, use N/A
            url         --> check and add missing https://

            Return
                the value obtained or None if there was no entry
                Upon conversion error, return None
                and set self.error to True

                For numeric values with unit set, return a list
                of [value, unit]
        """
        # reset the error, so it is a clear indication of
        # conversion problems
        self.error= False

        s = self.var.get()
        # no entry:
        if not s:
            return  None

        # the numeric cases:
        res = None
        try:
            if self.type == 'integer':
                res= int(self.var.get())

            elif self.type == 'numeric':
                res= float(self.var.get())

            elif self.type == 'numericlist':
                l = [i.strip() for i in s.split(',')]
                res= [float(i) for i in l]

        except ValueError:
            self.error= 1
            return None

        if res:
            return res

        # the various text cases
        if self.type == 'url':
            if not s.startswith('http://') \
            and not s.startswith('https://'):
                return f'https://{s}'

        if self.type == 'list':
            return [i.strip() for i in s.split(',')]

        # any other text types...
        return s
    # end get()


    @property
    def unit(self):
        if self.units is None:
            return None

        return self.units.get()
    # get the current unit


    @unit.setter
    def unit(self, this_unit:str=""):
        if self.units is None:
            return

        # if this unit is not yet in, we can add it
        # however, this may be not optimal for the
        # case of typos.
        if not this_unit in  self.units['values']:
            self.units.option_add(this_unit)

        self.units.set(this_unit)
    # end set unit


    def grid(self, **kwargs:dict) -> None:
        """ propagate the grid to the internal
            widget
        """
        self.entry.grid(**kwargs)
# end class EntryBox


class MultiSelect():
    """ a listbox based multiple select box
    """

    def __init__(self,
                 parent:tk.Misc,
                 options:list) -> None:
        """ Create a a widget and list up the options
            in it.
        """
        self.options = options
        self.parent = parent
        self.required= False
        self.error = False

        if self.parent is None:
            self.parent = tk.Tk()
        # end empty window
        self.select = tk.Listbox(self.parent,
                                 # selectmode='multiple')
                                 selectmode='extended')

        for i,j in enumerate(options):
            self.select.insert(i,j)
    # end __init__

    def grid(self, **kwargs):
        """ specify the grid() method for the whole calss
        """
        self.select.grid(**kwargs)
    # end grid

    def get(self) -> list:
        """ return a list of selected values
        """
        l = [self.select.get(i) for i in self.select.curselection()]

        # here is a possibility to convert to numbers
        # for later...
        if not l:
            return None

        return l
    # end get

    def set(self, selected:list)->None:
        """ Set all items in the list selected, based on
            a value returned by get before...
        """
        for i in selected:
            # this will throw a value error if the value is
            # not in the option list
            self.select.select_set(self.options.index(i))
    # end set
# end class MultiSelect


class Select():
    """ a simple class to select an item from a list.
        Basically for the sake of completedness,
        a combo box.
    """

    def __init__(self,
                 parent:tk.Misc,
                 options:list) -> None:
        """ Create a combo box with the list of options
            in it.
            Required is kind of unimportant here, since the
            selector always stands on a value... so, it is
            always set to something.
        """
        self.options = options
        self.parent = parent
        self.required= False
        self.error = False

        if self.parent is None:
            self.parent = tk.Tk()
        # end empty window
        self.select = ttk.Combobox(self.parent)
        self.select['values'] = options
        self.select['state'] = 'readonly'
        self.set(options[0])
    # end __init__

    def set(self, value):
        self.select.set(value)
    # end of set

    def get(self):
        return self.select.get()
    # end of get

    def grid(self, **kwargs):
        self.select.grid(**kwargs)


#end of class Select


class DateRoller():
    """ a simple widget to set up a date using spin boxes

        It takes year, month, day, hour and minute as integer
        numbers. It would not stop anyone typing in wrong values,
        but will invalidate the result (get returns None) and
        sets the error variable, so required check will work.

        It can be initiated with a value in:
        YYY-mm-dd HH:MM form or the set() method can do the same
        any time.
    """

    def __init__(self, parent:tk.Misc= None, value:str='') -> None:
        """ set up the widget and its initial values
        """
        self.parent = parent
        self.value = None
        # get the time tuple
        # (year, month, day, hour,
        # min, sec, wday, yday, isdst)
        now = time.localtime()
        if value != '':
            now = time.strptime(value, '%Y-%m-%d %H:%M')

        if self.parent is None:
            window= tk.Tk()
            window.geometry('200x50')
            window.grid()
            window.title('Date picker')
            frame = tk.Frame(window)
            frame.grid(column=0, row=0, sticky='news')
            self.window = window
        else:
            #window = tk.Toplevel(self.parent)
            frame = tk.Frame(self.parent)
            # make grid availeble for external adjustments
            self.grid = frame.grid

        self.fieldlist=[]
        self.varlist=[]
        mins = [now[0]-5, 1, 1, 0, 0]
        maxs = [now[0]+5, 12, 31, 23, 59]
        for i,v in enumerate(['year','month','day', 'hour', 'minute']):
            label = tk.Label(frame,
                             text= v)
            label.grid(column=i, row=0)

            newvar= tk.StringVar()
            newvar.set(str(now[i]))
            spinner = tk.Spinbox(frame,
                                 from_ = mins[i],
                                 to = maxs[i],
                                 # values= list(range(mins[i],maxs[i]+1)),
                                 textvariable= newvar,
                                 wrap= True,
                                 width= 4 if i == 0 else 2,
                                 # command= lambda event: self.changed(event, i))
                                 )
            # we can directly trace the variables:
            newvar.trace_add('write', lambda var, event, mode: self.changed(var, event, mode, i))

            spinner.grid(column= i, row=1)

            self.fieldlist.append(spinner)
            self.varlist.append(newvar)
        # done adding fields
        # to set the first value
        self.value_set()
    # end of __init__


    def set(self, value):
        """ set the values from value
            The value should be in the form YYY-mm-dd HH:MM
        """
        now = list(time.strptime(value, '%Y-%m-%d %H:%M'))[:5]

        for i,v in enumerate(now):
            self.varlist[i].set(str(v))

        # update the internal variable
        self.value_set()
    # end set


    def changed(self, var, event, mode,  index):
        """ spinner changed. If it is month, adjust the day limit
            This function is a trace method assigned to the variables.
        """
        month_max_list = [31, 28, 31, 30, 31, 30,
                          31, 31, 30, 31, 30, 31]
        try:
            self.error= False
            year = int(self.varlist[0].get())
            month = int(self.varlist[1].get())
            day = int(self.varlist[2].get())

        except ValueError:
            print('invalid value entered!')
            self.error= True
            self.value= None
            return


        if year%4 == 0 and year%100 != 0:
            month_max_list[1] = 29

        # limit the month days up to what the month allows
        self.fieldlist[2].configure(to = month_max_list[month-1])
        if day > month_max_list[month-1]:
            day = month_max_list[month-1]
        self.varlist[2].set(str(day))

        # record the curernt value
        self.value_set()
    # end changed


    def value_set(self):
        """ combine the spin boxes to a value
        """
        try:
            self.error= False
            date = (int(i.get()) for i in self.varlist)

        except ValueError:
            print('Invalid value in date!')
            self.error= True
            self.value = None
            return

        date = tuple(date) + (0,0,0,0)

        self.value = time.strftime('%Y-%m-%d %H:%M', date)
    # end of value_set


    def get(self):
        """ return the actual value
        """
        return self.value
    # end of get

# end class datePicker
