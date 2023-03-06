# problem: here the values come back flattened for
# subsets... How can we put them back? The keys
# do not match
#!/usr/bin/env python
""" a dialog to ask metadata from a user based on a template dict
    Author:     tomio
    License;    MIT
    Date:       2023-02-08
    Warranty:   None
"""
import os

import tkinter as tk
from  tkinter import ttk
# from tkinter.filedialog import FileDialog
from tkinter.messagebox import showerror

from project_config import replace_text

from rdm_help import rdmHelp
from rdm_widgets import (EntryBox, MultilineText,
    FilePickerTextField, CheckBox, MultiSelect, DateRoller)


class FormBuilder():
    """ a GUI window form dynamically built from a template
    """
    # This is a complex dynamic widget, which needs
    # several stirring parameters
    #pylint: disable=too-many-instance-attributes
    #pylint: disable=too-many-arguments
    def __init__(self,
                 title:str,
                 root_path:str,
                 parent:tk.Misc,
                 template:dict,
                 config:dict
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

        self.window.minsize(600,600)
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

        self.scroll_frame.bind(
                '<Enter>',
                lambda event: self.bind_mousewheel(canvas)
                )
        self.scroll_frame.bind(
                '<Leave>',
                lambda event: self.unbind_mousewheel(canvas)
                )

        canvas.configure(yscrollcommand= scrollbar.set)
        # to destroy, we have to unbind the canvas first
        self.window.bind('<Escape>', lambda event: self.destroy(canvas))
        self.window.bind('<Return>', lambda event: self.collect_results())
        self.window.bind('<F1>',
                         lambda event: rdmHelp(self.window,
                                                       self.template))
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


    def bind_mousewheel(self, canvas):
        """ bind the mouse wheel to the frame
        """
        canvas.bind_all('<MouseWheel>',
                        lambda event: self.roll(event, canvas)
                        )
        canvas.bind_all('<4>',
                        lambda event: self.roll(event, canvas),
                        add='+')
        canvas.bind_all('<5>',
                        lambda event: self.roll(event, canvas),
                        add='+')
    # end of bind_mousewheel


    def unbind_mousewheel(self, canvas):
        """ release the binding
        """
        canvas.unbind_all('<MouseWheel>')
        canvas.unbind_all('<4>')
        canvas.unbind_all('<5>')
    # end unbind_mousewheel


    def roll(self, event, canvas):
        """ what to do if scroll is done
            From event we can figure out where it moved,
            on canvas we can apply
        """
        # in windows, delta is nonzero
        if event.delta != 0:
            canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

        # on Linux, it is 0 but button 4/5 work
        else:
            sign = 1 if event.num == 5 else -1
            canvas.yview_scroll(sign*2, 'units')


    def add_content(self) -> None:
        """ parse the template dict, and add elements to the
            main window accordingly.
        """

        keys = list(self.template.keys())

        for j,i in enumerate(keys):
            v = self.template[i]

            if not isinstance(v, dict) or 'type' not in v:
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

            elif v['type'] == 'date':
                entry = DateRoller(frame)
                if 'value' in v:
                    entry.set(v['value'])

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
                    # for some reason we can have some spaces...
                    vv = v['value'].strip()
                    if vv:
                        # the first point is a position as 'line.column'
                        entry.text.insert('1.0', v['value'])

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
                if 'value' in v and v['value'] is not None:
                    this_value = v['value']
                    if isinstance(this_value, list):
                        this_value = ', '.join([i.split('file:',1)[-1]\
                                for i in this_value if i != 'file:None'])

                    else:
                        this_value = this_value.split('file:', 1)[-1]

                    entry.content.set(this_value)

                if 'required' in v and v['required']:
                    entry.required = True

            elif v['type'] == 'checkbox':
                entry = CheckBox(frame)
                entry.required= False
                entry.error = False

                if 'value' in v and v['value'] is True:
                    entry.select()

            elif v['type'] == 'subset' \
                    and 'form' in v \
                    and isinstance(v['form'], dict):

                entry= SubSet(
                    title= i,
                    root_path= self.root_path,
                    parent= frame,
                    form= v['form'],
                    config= self.config
                    )

                if 'value' in v\
                        and v['value'] is not None:
                    # set gives messges if there is
                    # a trivial mismatch, but no single
                    # point tests are done
                    entry.set(v['value'])

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
                command = self.collect_results
                )

        # now, stick it to the bottom

        # j is defined in the enumerate of the for loop,
        # indicating the last row added
        #pylint: disable=undefined-loop-variable
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

#            if typ == 'subset' and isinstance(val, dict):
#                for i,j in val.items():
#                    self.result[i] = j

            # add even if val is None
            self.result[i] = val
        # end pulling results
        # if all good, close:
        self.window.destroy()
    # end collect_results

    def destroy(self, canvas):
        """ destroy the widget, but make sure the events are
            freed from the canvas
        """
        self.unbind_mousewheel(canvas)
        self.window.destroy()
    # end destroy

# end of class FormBuilder


class SubSet():
    """ Handle a block of entries to form a table. In the original
        GUI show only the title, number of columns and rows.
        Provide an entry form for new values, a table view for
        the whole, means to delete and edit rows.
        Return a dict with the keys from the field names and
        lists for the values. This can be reassembled to a table
        easily.
    """

    # we need all these parameters, because subset can
    # handle the full form again...
    #pylint: disable=too-many-arguments
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

        # to position the overview widget, use:
        self.grid = self.frame.grid

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
                # subsets may go too deep, it is better
                # to keep those empty (reset)
                # inherit the values of the rest
                if this_template[j]['type'] != 'subset':
                    # print('setting up values for', this_template[j]['type'])
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
        # ESC will close the window
        window.bind('<Escape>', lambda event: window.destroy())
        # add double click to edit:
        window.bind('<Double-Button-1>', lambda event: self.edit_selected(
                                        tree_view,
                                        title,
                                        root_path,
                                        config
                                        )
                    )
        # pressing enter also edits
        window.bind('<Return>', lambda event: self.edit_selected(
                                        tree_view,
                                        title,
                                        root_path,
                                        config
                                        )
                    )

        frame= ttk.Frame(window)
        frame.grid(column=0, row=0, sticky='news')
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

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
            # problem: here the values come back flattened for
            # subsets... How can we put them back? The keys
            # do not match
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

        # vals can be false even when it is not fully empty
        # we need None only if no value was ever set...
        # Internal 0 and None values are controlled in the form
        #pylint: disable=use-implicit-booleaness-not-comparison
        if vals == []:
            return None

        # column based, kind of flattened:
        # return {i:list(v) for i,v in zip(keys, vals)}

        # make it row based return
        res = []
        for val_row in self.content:
            row = dict(zip(*list([keys, val_row])))
            res.append(row)

        return res
    # end of get


    def set(self, values:list) -> None:
        """ take a list of dicts where the values are lists,
            and put it into the content lists.

            The user has to make sure the dict contains
            the current form keys, and the length match
            one another.

        """

        if not values or not isinstance(values[0], dict):
            return

        # we go an extra circle to set the values
        keys = list(values[0].keys())

        # this_set = {i:j for i,j in values.items() if i in self.form}

        # if len(this_set) != len(self.form):
        #    print('size mismatch, cannot set values for subset!')

        # self.content = [tuple(i) for i in zip(*list(this_set.values()))]

        # we have two options:
        # we can go blind, assuming the keys match
        # or we can just assume the first line matches all others

        for i in keys:
            if i not in self.form:
                print('key', i, 'not found')
                return

        if len(keys) != len(self.form):
            print('length mismatch!', len(keys), 'vs', length(self.form))
            return

        self.content = [tuple(i.values()) for i in values]

        self.update_content()
    # end set
# end of class SubSet
