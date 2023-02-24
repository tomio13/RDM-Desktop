#!/usr/bin/env python
""" a dialog to ask metadata from a user based on a template dict
    Author:     tomio
    License;    MIT
    Date:       2023-02-08
    Warranty:   None
"""
import os
import tkinter as tk
import tkinter.ttk as ttk
# from tkinter.filedialog import FileDialog
from tkinter.filedialog import askopenfilenames
from tkinter.messagebox import showerror
from tkinter import StringVar
import yaml

from project_config import replace_text
# import project_config as pc


class FormBuilder():
    """ a GUI window form dynamically built from a template
    """
    def __init__(self,
                 title:str ='Template form',
                 root_path:str ='',
                 parent:tk.Misc= None,
                 template:dict= None,
                 config:dict={}
                 ) -> None:
        """ Create a window, and populate it with input fields from
            template.
            At submittion, save a YAML file of the results.
        """
        if not config or not template:
            print('Not enough information to proceed')
            return

        self.config = config
        self.parent = parent
        self.template = template

        if root_path:
            self.root_path = root_path
        else:
            self.root_path = config['projectDir']

        self.root_path = os.path.abspath(
                os.path.expanduser(
                    self.root_path
                    )
                )
        if not title:
            title='Form'

        if self.parent is None:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(self.parent)

        self.window.minsize(300,400)
        # leave the size automatic
        self.window.geometry('')
        self.window.grid()
        # to make the frame at 0,0 stick and scale with the window:
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        # bring the window to top as a start
        self.window.lift()
        # but do not force it to the top
        # stacking order ==> always on top
        # window.attributes('-topmost', 1)

        self.window.title(title)
        # with this, we have a nice, empty window with a title
        #
        # We need a scrollable container with flexible content
        #
        # Let us use the example at:
        # https://blog.teclado.com/tkinter-scrollable-frames/
        # well, a bit modified 8)
        canvas = tk.Canvas(self.window)
        canvas.grid(
                column= 0,
                row= 0,
                padx= 10,
                pady= 10,
                sticky='snwe'
                )
        canvas.grid_columnconfigure(0, weight=10)
        canvas.grid_rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(self.window,
                                  orient='vertical',
                                  command= canvas.yview,
                                  takefocus= True)

        scrollbar.grid(column=1, row=0, padx=5, pady=5,  sticky='nse')
        scrollbar.grid_columnconfigure(0, weight=1)
        scrollbar.grid_rowconfigure(0, weight=1)
        # add a frame

        # autoupdate the scrollable size as soon as
        # the area changed because we added sg.

        self.scroll_frame= ttk.Frame(canvas)
        canvas.create_window((0,0),
                                  window= self.scroll_frame,
                                  anchor='nw')

        self.scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion= canvas.bbox("all")
                    )
            )

        canvas.configure(yscrollcommand= scrollbar.set)
        # self.scroll_frame.grid(column=0, row=0, sticky='nsw')
        # with this, we have a window, containing a canvas,
        # in which we have frame
        # We can pack content into the frame, and it can be scrolled

        # Let us define some containers:
        # frames will contain labels and entries
        # collect them dynamically
        self.framelist= []
        # these are the entries we will have to collect
        self.entrydict= {}
        # and we have a result dict:
        self.result = {}
        self.default_result = {}
        # add a lot of frames into the frame
        self.add_content()
    # end init()


    def add_content(self) -> None:
        """ parse the template dict, and add elements to the
            main window accordingly.
        """

        keys = list(self.template.keys())
        N = len(keys)

        for j,i in enumerate(keys):
            v = self.template[i]

            if not isinstance(v, dict) or 'type' not in v:
                # print('not a form element!', i, v)

                if isinstance(v, str):
                    self.default_result[i] = replace_text(v, self.config, self.root_path)
                else:
                    self.default_result[i] = v

                continue

            # a local frame is used to pack everything in
            # the specific line
            frame = ttk.Frame(self.scroll_frame, pad= 5)

            txt_label = str(i)
            label = ttk.Label(frame, text= txt_label, pad= 10)
            label.grid(column= 0,
                       row= 0,
                       padx=(2,5),
                       pady=(2,2),
                       sticky='w')

            if v['type'] in ['text', 'url', 'numeric', 'integer', 'list', 'numericlist']:
                # entry = ttk.Entry(frame, textvariable= var)
                entry = EntryBox(frame, v['type'])
                if 'value' in v:
                    entry.set(v['value'])

                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'select':
                entry = ttk.Combobox(frame)
                # two parameters we need, they do not have:
                entry.required = False
                entry.error= False

                entry['values'] = v['options']
                # make it read only, so user cannot insert new values
                # alternative would be state 'normal'
                entry['state'] = 'readonly'
                if 'value' in v:
                    entry.set(v['value'])
                else:
                    entry.set(v['options'][0])

                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'multiselect':
                entry = MultiSelect(frame, v['options'])
                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'multiline':
                # another text widget
                entry = MultilineText(frame)
                if 'value' in v:
                    entry.text.insert(v['value'])

                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'file':
                # files we are seeking contain other
                # experiments in the root_path
                # experiments are typically yaml files
                ext = v['extension'] if 'extension' in v else 'yaml'
                entry = FilePickerTextField(
                        parent= frame,
                        indir= self.root_path,
                        extension= ext
                        )
                if 'value' in v:
                    entry.content.set(v['value'])

                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'checkbox':
                entry = CheckBox(frame)
                entry.required= False
                entry.error = False

                if 'value' in v and v['value']==True:
                    entry.select()

            elif v['type'] == 'subset'\
                and 'value' in v \
                and isinstance(v['value'], dict):
                if not v['value']:
                    print('Calling subset with empty value!')

                entry= SubSet(
                    title= i,
                    root_path= self.root_path,
                    parent= frame,
                    form= v['value'],
                    config= self.config
                    )

                if 'required' in v and v['required']:
                    entry.required = True
            # end enumerating possible types

            # put the new entry in place
            entry.grid(column= 1,
                       row= 0,
                       padx= (5,2),
                       pady=(2,2),
                       sticky='e')

            # create a dict of text label:entry
            # archive the result
            self.entrydict[txt_label] = entry
            frame.grid(column=0, row= j)
        # end looping for content
        #
        # we need a last button to submit the lot
        self.submit_button = ttk.Button(
                frame,
                text= 'Submit',
                command= self.collect_results
                )

        # now, stick it to the bottom
        self.submit_button.grid(column=0, row=j+1)
        # last thing to add: a submit button
    # end of add_content


    def collect_results(self) -> None:
        """ fill up the results with this
        """
        # if the process was cancelled in any way,
        # self.result should be empty
        # now, that we have a submission, we fill it up
        self.result = self.default_result.copy()

        for i,v in self.entrydict.items():
            # we have the chance to insert the
            # keys from a subset to the whole
            # this means keys should not be repeated
            # within the subset vs. main tree
            val = v.get()
            typ = self.template[i]['type']

            # If we have a problem, do not close the
            # widget, inform the user
            if val is None:
                if v.error:
                    showerror(master= self.window,
                          title='Invalid value!',
                          message=f'Invalid value in {i} {typ}')
                    # erase our content
                    self.result = {}
                    return

                if v.required:
                    showerror(master= self.window,
                          title='Error',
                          message=f'{i} is required!')
                    # erase our content
                    self.result = {}
                    return

            if typ == 'subset':
                self.result.update(val)
            else:
                self.result[i] = val
        # end pulling results
        # here comes some validity checking....
        #
        # if all good, close:
        self.quit()

    # enf collect_results

    def quit(self) -> None:
        self.window.destroy()
    # end quit
# end of class FormBuilder


class FilePickerTextField():
    """ a small class to build a file picker in the form of
        a text field and a button. The button activates a
        file selector widget, and its results fills the text
        field. The text field is editable.
        Use possibly a relative path.
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

        self.frame= ttk.Frame(self.parent)
        # allow positioning after called:
        self.grid = self.frame.grid


        self.dir = indir
        self.extension = extension
        self.content = StringVar()
        self.required= False
        self.error= False

        self.entry = ttk.Entry(
                self.frame,
                width= 30,
                textvariable= self.content
                )

        self.entry.grid(
                column= 0,
                row= 0
                )

        self.button = ttk.Button(self.frame,
                                text='Select',
                                command= self.get_file
                                )
        self.button.grid(column= 1, row= 0)
    # end __init__


    def get_file(self) -> None:
        """ bring up a file dialog and get a file name
        """

        # d = FileDialog(
        d = askopenfilenames(
                master= self.frame,
                title='Select file',
                defaultextension= self.extension,
                initialdir= self.dir
                )
        #fn = d.go(
        #        dir_or_file= os.path.join(self.dir,
        #                     self.content.get()),
        #        pattern= self.pattern
        #          )
        if d:
           fn = [os.path.relpath(i, self.dir) for i in d]
           # this is our 'return' value:
           self.content.set( ', '.join(list(fn)))
    # end get_file


    def get(self) -> str|list:
        fn = self.content.get()
        if not fn:
            return None

        if ',' in fn:
            fn = fn.split(', ')
            print('start with:', fn)
            fn = [f'file:{i}' for i in fn \
                    if os.path.isfile(os.path.join(self.dir, i))]
            print('result:', fn)
            return fn

        elif os.path.isfile(fn):
            fn = os.path.relpath(
                    fn,
                    self.dir
                    )

            return f'file:{fn}'

        else:
            # we still return, to allow for non-existent files
            return fn

    # end get
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

        self.frame= ttk.Frame(self.parent)

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.text = tk.Text(self.frame, width= 50, height= 10)
        self.text.grid(column=0, row=0, sticky='we')
        self.required= False
        self.error = False

        self.scroll_vertical= tk.Scrollbar(self.frame,
                                           bg= 'grey',
                                           orient= 'vertical',
                                           command= self.text.yview,
                                           takefocus= True
                                           )
        self.scroll_vertical.grid(row= 0,
                                   column= 1,
                                   sticky= 'ns')
        self.text.config(yscrollcommand= self.scroll_vertical.set)

        self.scroll_horizontal= tk.Scrollbar(self.frame,
                                           bg= 'grey',
                                           orient= 'horizontal',
                                           command= self.text.xview,
                                           takefocus= True
                                           )
        self.scroll_horizontal.grid(row= 1,
                                   column= 0,
                                   sticky= 'ew')
        self.text.config(xscrollcommand= self.scroll_horizontal.set)

        # to allow positioning
        self.grid = self.frame.grid
    # end __init__


    def get(self)->str:
        """ return the full content of the widget
        """
        v= self.text.get('1.0','end')
        if not v:
            return None

        return v
    # end of get

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
        to be: text, file, url, integer, numeric
    """

    def __init__(self,
                 parent:tk.Misc,
                 vartype:str='text',
                 **kwarg:dict) -> None:
        """ Initiate an entry widget, based on its type
        """
        # internally we use strings for any variable
        self.var = tk.StringVar()

        self.type = vartype
        self.error = False
        self.error = False

        self.parent = parent
        self.required= False

        if self.parent is None:
            self.parent = tk.Tk()

        self.entry = ttk.Entry(self.parent, textvariable= self.var)
    # end __init__

    def set(self, value:str|int|float|list|None) -> None:
        """ Set the internal variable from value
            Use a text tk variable, so convert the incoming
            types to it.
        """
        # since tk does not handle invalid numbers well,
        # we have to take it out of its hands...
        # that would mean that every field is a text field,
        # but if the conversion fails, we make a message and
        # return None. The main FormBuilder then refuses to close
        if value is None:
            return

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
        """
        # reset the error, so it is a clear indication of
        # conversion problems
        self.error= False

        s = self.var.get()
        # no entry:
        if not s:
            return  None

        # the numeric cases:
        try:
            if self.type == 'integer':
                return int(self.var.get())

            if self.type == 'numeric':
                return float(self.var.get())

            if self.type == 'numericlist':
                l = [i.strip() for i in s.split(',')]
                return [float(i) for i in l]

        except ValueError:
            # print('invalid value in entry')
            self.error= 1
            return None

        # the various text cases
        if self.type == 'url':
            if not s.startswith('http://') \
            and not s.startswith('https://'):
                return f'https://{s}'

        if self.type == 'list':
            return [i.strip() for i in s.split(',')]

        else:
            # any other text types...
            return s

    # end get()

    def grid(self, **kwargs:dict) -> None:
        self.entry.grid(**kwargs)
# end class EntryBox


class MultiSelect():
    """ a listbox based multiple select box
    """

    def __init__(self,
                 parent:tk.Misc,
                 options:list=[]) -> None:
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
                                 selectmode='multiple')

        for i,j in enumerate(options):
            self.select.insert(i,j)
    # end __init__

    def grid(self, **kwargs):
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
# end class MultiSelect


class SubSet():
    """ Handle a block of entries to form a table. In the original
        GUI show only the title, number of columns and rows.
        Provide an entry form for new values, a table view for
        the whole, means to delete and edit rows.
        Return a dict with the keys from the field names and
        lists for the values. This can be reassembled to a table
        easily.
    """

    def __init__(self,
                 title:str,
                 root_path:str,
                 parent:tk.Misc,
                 form:dict,
                 config:dict) -> None:
        """ create a frame inside the parent widget with
            information about the current status of the subset,
            and buttons to:
            - view the data
            - add new values

            Use the FormBuilder to add new values

            Parameters:
            title:      a title string
            root_path:  the path wer are currently working in
            parent:     the parent widget or None
            form:       what fields to be collected
            config:     the configuration dict
        """
        if not form:
            print('Nothing to do here!')
            return

#        self.root_path = root_path
#        self.title= title
#        self.config = config
        self.required= False
        self.error = False
        self.form = form
        self.parent = tk.Tk() if parent is None else parent

        # about the data:
        self.content = []
        self.label_fields= []

        self.frame = ttk.Frame(self.parent)
#        self.frame.grid(column= 0, row= 0, sticky= 'nsew')
        label = tk.Label(self.frame, text= title)
        label.grid(column= 0, row= 0)
        # now, we need some content...
        self.create_content(title= title,
                            root_path= root_path,
                            config= config)
    # end __init__



    def add_labels(self):
        """ create the labels with row and column
            numbers
        """
        nrow = len(self.content)
        ncol = len(self.form)
        label1 = tk.Label(self.frame,
                          text= f'Fields: {ncol}')
        label2 = tk.Label(self.frame,
                          text= f'Items: {nrow}')
        label1.grid(column = 0, row= 1, ipadx= 5, ipady= 5, sticky= 'news')
        label2.grid(column = 0, row= 2, ipadx= 5, ipady= 5, sticky= 'news')

        self.label_fields = [label1, label2]
    # end add_labels


    def create_content(self,
                       title:str,
                       root_path:str,
                       config:dict) -> None:
        """ fill up the frame content the first time
            The parameters coming from __init__ and get sent to be
            used in the subsequent pop-up windows...
        """
        self.add_labels()

        # now, add the buttons:
        button_new = tk.Button(self.frame,
                               text='+',
                               command= lambda: self.add_new(
                                   title= title,
                                   root_path= root_path,
                                   config= config
                                   ))

        button_new.grid(column=2, row= 1)

        button_show= tk.Button(self.frame,
                               text='show',
                               command= lambda: self.show(
                                   title= title,
                                   root_path= root_path,
                                   config= config
                                   ))

        button_show.grid(column=2, row= 2)
    # end create_content


    def update_content(self):
        """ update the content in the frame showing
            - label
            - number of columns
            - number of rows
        """

        # clear the frame
        for widget in self.label_fields:
            widget.destroy()

        self.label_fields = []

        # now, add them again
        self.add_labels()
    # end update_content

    def add_new(self,
                title:str,
                root_path:str,
                config:dict
                )->None:
        """ add values to the lists
        """
        this_template = self.form.copy()
        if self.content:
            row = self.content[-1]


            keylist = list(this_template.keys())
            for i,j in enumerate(keylist):
                this_template[j]['value'] = row[i]

        input_form = FormBuilder(
                title= f'Add new {title}',
                root_path= root_path,
                parent= self.parent,
                template= this_template,
                config= config
                )
        input_form.window.wait_window()

        if input_form.result:
            self.content.append(
                    list(input_form.result.values())
                    )
            self.update_content()
    # end add_new


    def show(self,
             title:str,
             root_path:str,
             config:dict
             ):
        """ make a tabulated list of the existing entries
        """

        window= tk.Toplevel(self.parent)
        window.title(title)
        window.minsize(300,400)
        window.grid()
        window.columnconfigure(0, weight= 1)
        window.rowconfigure(0, weight= 1)
        window.lift()
        frame= ttk.Frame(window)
        frame.grid(column=0, row=0, sticky='news')
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # print('columns:', tuple(self.form.keys()))
        cols = tuple(self.form.keys())
        tree_view = ttk.Treeview(frame,
                                 columns = cols,
                                 show= 'headings')
        for head in cols:
            tree_view.heading(head, text= head)

        for line in self.content:
            tree_view.insert('','end', values= line)

        tree_view.grid(column=0,
                       row=0,
                       columnspan=2,
                       sticky='news')

        button_delete= ttk.Button(
                frame,
                text= 'Delete',
                command= lambda: self.delete_selected(tree_view)
                )

        button_delete.grid(column= 0, row= 1, sticky='sw')

        button_edit= ttk.Button(
                frame,
                text= 'Edit',
                command= lambda: self.edit_selected(
                    tree_view,
                    title,
                    root_path,
                    config
                    )
                )
        button_edit.grid(column= 1, row= 1, sticky='se')

        window.wait_window()

    # end show


    def delete_selected(self, tree_widget) -> None:
        """ delete selected rows
            parameters

            tree_widget:    the parent widget we are working in
        """
        for i in tree_widget.selection():
            # delete the root content:
            self.content.pop(tree_widget.index(i))
            # delete from the widget
            tree_widget.delete(i)

        # since the list changed:
        self.update_content()
    # end delete_selected


    def edit_selected(self,
                      tree_widget:ttk.Treeview,
                      title:str,
                      root_path:str,
                      config:dict) -> None:
        """ edit selected row
            Edit only the first of the selection, so it may
            cause problems if the user is not watching...

            parameters:
            tree_widget     the tree widget we are working on
            title:          to pass to the form editor
            root_path:      to pass to the form editor
            config:         to pass to the form editor
        """
        element = tree_widget.selection()
        if not element:
            print('Nothing to edit')
            return

        element = element[0]
        # we need an index to see the content part
        index = tree_widget.index(element)
        row = self.content[index]

        # to use the form builder, we have to change
        # the form to have values set
        this_template = self.form.copy()
        keylist = list(this_template.keys())
        for i,j in enumerate(keylist):
            this_template[j]['value'] = row[i]

        # now, we can call an editing form
        input_form = FormBuilder(
                title= f'edit {title}',
                root_path= root_path,
                parent= tree_widget,
                template= this_template,
                config= config
                )
        input_form.window.wait_window()

        if input_form.result:
            # update both the tree widget and the content:
            self.content[index] = list(input_form.result.values())
            tree_widget.item(element,
                            value= tuple(input_form.result.values()))
        # since the number of rows did not change,
        # we need no other update on content
    # end edit

    def get(self) -> None:
        """ return the results as a dict
        """
        keys = list(self.form.keys())
        vals = list(zip(*self.content))
        if not any(vals):
            return None

        return {i:v for i,v in zip(keys, vals)}
    # end of get


    def grid(self, **kwargs:dict) -> None:
        self.frame.grid(**kwargs)
    # grid for rendering
# end of class SubSet
