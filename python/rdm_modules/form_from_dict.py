#!/usr/bin/env python
""" a dialog to ask metadata from a user based on a template dict
    Author:     tomio
    License;    MIT
    Date:       2023-02-08 -
    Warranty:   None
"""
# from dictDigUtils import dict_disp
import os

import tkinter as tk
from  tkinter import ttk
# from tkinter.filedialog import FileDialog
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

from .project_config import replace_text

from .rdm_help import rdmHelp
from .rdm_widgets import (EntryBox, MultilineText,
                          FilePickerTextField, CheckBox, MultiSelect,
                          Select, DateRoller, RdmWindow)


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

            Parameters:
            title:      title displayed for the window
            root_path:  where the data shall be saved (data folder)
            parent:     parent window object or None
            template:   template dict to base the work on
            config:     configuration settings

            Return;
                At submittion, save a YAML file of the results.
        """
        if not config or not template:
            print('Not enough information to proceed')
            return

        self.config = config
        self.parent = parent
        self.template = template

        self.root_path = root_path if root_path\
                            else config['projectDir']

        self.root_path = os.path.abspath(
                os.path.expanduser(
                    self.root_path
                    )
                )

        if not title:
            title='Form'
        self.window = RdmWindow(self.parent, title, with_scrollbar= True)


        # to destroy, we have to unbind the canvas first
        self.window.bind('<Control-Return>', lambda event: self.collect_results())
        self.window.bind('<F1>',
                         lambda event: rdmHelp(self.window.window,
                                                       self.template))
        # with this, we have a window, containing a canvas,
        # in which we have frame (actually two: content and command)
        # We can pack content into the frame, and it can be scrolled

        # Let us define some containers:
        # frames will contain labels and entries
        # frames are not that important, they may contain a label
        # for groupping entries, but nothing more
        # however, entries contain the user input!
        # collect them dynamically
        self.entrydict= {}
        # and we have a result dict filled in from
        # the entries when collect_results() run
        # it is available even when the window is destroyed
        self.result = {}
        self.default_result = {}
        # add a lot of frames into the frame
        self.add_content()
    # end init()


    def add_content(self) -> None:
        """ parse the template dict, and add elements to the
            main window accordingly.
        """

        # dict_disp(self.template)
        frame= self.window.content
        # frame= tk.Frame(self.window.content)
        # frame.rowconfigure(0, weight=20)
        # frame.columnconfigure(0, weight=20)
        # frame.grid(column= 0, row= 0, sticky='nsew')
        # if we have group labels, we add frames in a grid
        # this grid needs to go one by one
        group_level = 0

        # make a static copy of keys,
        # so not problem comes if we change them
        keys = list(self.template.keys())

        # go through the template
        for j,i in enumerate(keys):
            v = self.template[i]
            txt_label= str(i)

            # no type field means it is not editable part of the form,
            # but we take it over
            # Texts may have substituted parts (e.g. user ID)
            if not isinstance(v, dict) or 'type' not in v:
                # if the dict is a keyword and value: group or group_id,
                # then make it a new label on the form
                #
                # also store it, so we can propagate it for future edition
                # or for uploads

                if isinstance(v, str):
                    if v.lower() in ['group', 'group_id']:
                        # print('found group', txt_label)

                        frame = tk.LabelFrame(self.window.content,
                                              text= txt_label,
                                              padx= 10,
                                              pady= 10,
                                              labelanchor='nw')
                        frame.columnconfigure(0, weight=20)
                        frame.rowconfigure(group_level, weight=20)
                        frame.grid(column=0,
                                   row= group_level,
                                   sticky='nsew')
                        group_level += 1
                    # end if new group

                    self.default_result[i] = replace_text(v, self.config, self.root_path)
                else:
                    self.default_result[i] = v

                # too lazy to indent everything below within the loop?
                # then use continue to skip the rest:
                continue

            # a local frame is used to pack everything in
            # the specific line
            # turn to using a match structure with all its
            # complex possibilities
            # this should make the whole procedure somewhat simpler looking
            # testing match:
            #match v:
            #    case {'type':'text'|'url'|'numeric'|'integer'|'list'|'numericlist'}:
            #        print ('found a field!', v['type'])
            #
            # problem: python < 3.10 does not support match / case
            # and python > 3.10 cannot run on older windows

            # end if not a dict or has no type...
            # handle those which have type and are dicts
            if v['type'] in ['text', 'url',
                             'numeric', 'integer',
                             'list', 'numericlist']:
                # entry = ttk.Entry(frame, textvariable= var)
                entry = EntryBox(frame,
                                 txt_label,
                                 v['type'],
                                 units=(v['units'] if 'units' in v else None))

                # set is managed for all later
                if 'unit' in v:
                    entry.unit= v['unit']


            elif v['type'] == 'date':
                entry = DateRoller(frame, label= txt_label)

            elif v['type'] == 'select':
                entry = Select(frame, txt_label, v['options'])

                # make it read only, so user cannot insert new values
                # alternative would be state 'normal'

            elif v['type'] == 'multiselect':
                entry = MultiSelect(frame, txt_label, v['options'])

            elif v['type'] == 'multiline':
                # another text widget, with multiple lines
                # if confit['editor'] is set, it has an edit button
                # to allow for external editing
                editor = self.config['editor'] if ('editor' in self.config
                                    and self.config['editor']) else None

                entry = MultilineText(frame, label= txt_label, editor= editor)

            elif v['type'] == 'file':
                # files we are seeking contain other
                # experiments in the root_path
                # experiments are typically yaml files
                ext = v['extension'] if 'extension' in v else 'yaml'
                entry = FilePickerTextField(
                        parent= frame,
                        label= txt_label,
                        indir= self.root_path,
                        extension= ext
                        )

            elif v['type'] == 'checkbox':
                entry = CheckBox(frame, label= txt_label)

            elif v['type'] == 'subset' \
                    and 'form' in v \
                    and isinstance(v['form'], dict):

                entry= SubSet(
                    title= txt_label,
                    root_path= self.root_path,
                    parent= frame,
                    form= v['form'],
                    config= self.config
                    )
            # end enumerating possible types

            # error and required should be initialized for
            # every widget as false
            # we run this, though not every widget will
            # have it (e.g. in a selection or a radio button
            # it has no meaning)
            if 'required' in v and v['required']:
                entry.required = True

            # is there a default value requested,
            # and can the widget take it?
            if 'value' in v and v['value'] is not None:
                # print(v)
                entry.set(v['value'])

            # put the new entry in place
            entry.grid(column= 0,
                       row= j,
                       padx= (5,2),
                       pady=(2,2),
                       sticky='ew')

            # create a dict of text label:entry
            # archive the result
            self.entrydict[txt_label] = entry
            # frame.grid(column=0, row= j)
        # end looping for content

        # we need a last button to submit the lot
        # it goes outside of the above frames, to the end
        # of the window content frame
        self.submit_button = ttk.Button(
                self.window.content,
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

        self.result = self.template.copy()
        self.result.update(self.default_result)

        # print(self.result)
        for i,v in self.entrydict.items():
            # we have the chance to insert the
            # keys from a subset to the whole
            # this means keys should not be repeated
            # within the subset vs. main tree
            val = v.get()
            typ = self.template[i]['type']
            print('getting:', i,'/', typ, ':', val)

            # If we have a problem, do not close the
            # widget, inform the user
            if val is None:
                if v.error:
                    showerror(master= self.window.window,
                          title='Invalid value!',
                          message=f'Invalid value in {i} {typ}')
                    # erase our content
                    self.result = {}
                    self.window.lift()
                    return

                if v.required:
                    showerror(master= self.window.window,
                          title='Error',
                          message=f'{i} is required!')
                    # erase our content
                    self.result = {}
                    self.window.lift()
                    return
            # add even if val is None

            self.result[i]['value'] = val

            if 'units' in self.template[i]:
                self.result[i]['unit'] = v.unit
            # print('resulting in:', i, ':', self.result[i])

        # end pulling results
        # print('Resulted in:\n', self.result)
        # if all good, close:
        self.window.destroy()
    # end collect_results


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
            Information: how many columns (fields) are defined,
            and how many rows (records) already exist.

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

        # to minimize internal variables, leave
        # root_path, title and config as only passed on variables

        # internals as for every other widgets in RDM we need
        # required and error
        self.required= False
        self.error = False
        # we need form to create the form when needed
        self.form = form
        # if called out of context, it should still work:
        self.parent = tk.Tk() if parent is None else parent

        # about the data:
        self.content = []
        self.label_fields= []

        self.frame = ttk.Frame(self.parent)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=10)
        self.frame.columnconfigure(0, weight= 5)
        self.frame.columnconfigure(1, weight= 5)
        self.frame.columnconfigure(2, weight= 5)
        self.frame.columnconfigure(3, weight= 5)
        # the placing of this frame is managed by the form builder
        # normally...

        # to position the overview widget, use:
        self.grid = self.frame.grid

        # within this frame we have a label and then
        # the content: buttons and row/column information
        label = tk.Label(self.frame, text= title)
        label.grid(column= 0, row= 0, padx= 10)
        # now, we need some content...
        self.create_content(title= title,
                            root_path= root_path,
                            config= config)
    # end __init__



    def add_labels(self):
        """ create the labels with row and column numbers
            These belong within the frame as dynamic content.
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
        # since python 3.11 dict copy is a shallow copy
        # so we make a full copy for protecting the original
        this_template = self.form.copy()
        if self.content:
            row = self.content[-1]

            keylist = list(this_template.keys())
            for i,j in enumerate(keylist):
                # subsets have their own value handling for the
                # whole form
                # all the others receive their default / preset value
                # from the value field in the dict, so set it
                # For fields with unit, the list [value, unit] is also recognized
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
            next_row= []
            for v in input_form.result.values():
                if 'value' in v:
                    next_row.append(
                            [v['value'],v['unit']] if 'unit' in v else v['value']
                                    )
            # end for making the line
            self.content.append(next_row)
            #            self.content.append(
            #        [v['value'] for v in input_form.result.values() if 'value' in v]
            #        #list(input_form.result.values())
            #        )
            self.update_content()
    # end add_new


    def to_str(self, data) -> str:
        """ just call str, but return '' for None
        """
        if data is None:
            return ''
        else:
            return str(data)
    # end to_str


    def show(self,
             title:str,
             root_path:str,
             config:dict
             ):
        """ make a tabulated list of the existing entries
        """

        window= RdmWindow(self.parent,
                          title,
                          with_scrollbar= True,
                          min_size=(300, 400)
                          )
        # ESC will close the window

        cols = tuple(self.form.keys())
        tree_view = ttk.Treeview(window.content,
                                 columns = cols,
                                 show= 'headings')
        tree_view.columnconfigure(0, weight=10)
        tree_view.rowconfigure(0, weight=10)

        for head in cols:
            tree_view.heading(head, text= head)

        for line in self.content:
            # the str() originall has the annoying property to fill up None
            # values with 'None' as text...
            show_line = tuple((self.to_str(i) for i in line))
            tree_view.insert('','end', values= show_line)

        tree_view.grid(column=0,
                       row=0,
                       #columnspan=2,
                       sticky='news')

        # csv_icon = tk.PhotoImage(file='./icons/csv.png')
        button_csv = ttk.Button(
                window.command,
                text= 'to csv',
                # image= csv_icon,
                command= lambda: self.write_csv(folder= root_path)
                )
        button_csv.grid(column=0, row=1, sticky='sw')

        button_delete= ttk.Button(
                window.command,
                text= 'Delete',
                command= lambda: self.delete_selected(tree_view)
                )

        button_delete.grid(column= 1, row= 1, sticky='sw')

        button_edit= ttk.Button(
                window.command,
                text= 'Edit',
                command= lambda: self.edit_selected(
                    tree_view,
                    title,
                    root_path,
                    config
                    )
                )

        button_edit.grid(column= 2, row= 1, sticky='se')

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


        window.wait_window()
    # end show


    def write_csv(self, folder) -> None:
        """ get a file name, and dump the content to a CSV file.
            For elements containing comma, quote them as strings.
            Do a simple job, so we can live without the CSV class.
            It is not really nice when one has many lists and subsets
            to use this, but useful for simple subset tables.

            Delimiter: ','
            New line: '\n'
            quote:      simple, when ',' is in the string
        """

        # get a file pointer in the current project folder
        fn= asksaveasfilename(parent= self.parent,
                      initialdir= folder,
                      filetypes= [('.csv', '*.csv')],
                      defaultextension= '.csv',
                      )

        # for simple quoting:
        def to_str(x):
            if isinstance(x, str):
                t = f'{x}'
            else:
                t = repr(x)
            if ',' in t:
                return f'"{x}"'
            return t
        # end define to_str

        with open(fn, 'wt', encoding='UTF-8') as fp:
            # create a header
            txt = ', '.join([to_str(i) for i in self.form.keys()])
            print('header:\n', txt)
            fp.write(f'{txt}\n')

            for row in self.content:
                txt = ', '.join([to_str(i) for i in row])
                # print(txt)
                fp.write(f'{txt}\n')
            # with takes care of this
            # fp.close()

        print('writing csv file is complete')
    # end wirte_csv


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

        # debug:
        # print('calling form with:')
        # print(this_template)

        # now, we can call an editing form
        # print('calling FormBuilder with:\n', this_template)
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
            # .... we changed, not the form result is a full dict
            # self.content[index] = list(input_form.result.values())
            # ... thus we extract as:
            # self.content[index] = [v['value'] for k,v in input_form.result.items() if 'value' in v]
            # self.content[index] = [v['value'] for v in input_form.result.values() if 'value' in v]
            next_row= []
            for v in input_form.result.values():
                if 'value' in v:
                    next_row.append(
                            [v['value'],v['unit']] if 'unit' in v else v['value']
                                    )
            # end for making the line
            self.content[index] = next_row
            # problem: here the values come back flattened for
            # subsets... How can we put them back? The keys
            # do not match
            tree_widget.item(element,
                            value= tuple(self.content[index]))
                                #[v['value'] for k,v in input_form.result.items() if 'value' in v]
        # since the number of rows did not change,
        # we need no other update on content
    # end edit


    def get(self) -> None:
        """ return the results as a dict
            Go through the collected content, and form a list of
            dicts as the result. This is a special output for
            subsets.
            However, every field contains its last value and unit,
            which we clean out on the fly.
        """
        keys = list(self.form.keys())
        vals = list(zip(*self.content))

        # vals can be false even when it is not fully empty
        # we need None only if no value was ever set...
        # Internal 0 and None values are controlled in the form
        #pylint: disable=use-implicit-booleaness-not-comparison
        if vals == []:
            return None

        # do some cleaning: value and unit are in the content,
        # those in the local fields are not needed
        # this occurs because in python 3.11 dict copies are shallow copies,
        # thus only link to the original
        for k in keys:
            if 'value' in self.form[k]:
                self.form[k].pop('value')
            if 'unit' in self.form[k]:
                self.form[k].pop('unit')

        # column based, kind of flattened:
        # return {i:list(v) for i,v in zip(keys, vals)}

        # make it row based return
        res = []
        for val_row in self.content:
            row = dict(zip(*list([keys, val_row])))
            res.append(row)

        # print('\nContent:', res)
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
        # print('subset keys:', keys)
        # print('vs:', list(self.form.keys()))

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
        # print('Updating content:', self.content)

        self.update_content()
    # end set
# end of class SubSet
