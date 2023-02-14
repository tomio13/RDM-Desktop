#!/usr/bin/env python
""" a dialog to ask metadata from a user based on a template dict
    Author:     tomio
    License;    MIT
    Date:       2023-02-08
    Warranty:   None
"""
import yaml
import os
import tkinter as tk
import tkinter.ttk as ttk
import project_config as pc
from tkinter.filedialog import FileDialog
from tkinter import StringVar


class FormBuilder(object):
    """ a GUI window form dynamically built from a template
    """
    def __init__(self,
                 title='Template form',
                 root_path='',
                 parent= None,
                 template= None,
                 config= {}
                 ):
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
        self.canvas = tk.Canvas(self.window)
        self.canvas.grid(
                column= 0,
                row= 0,
                padx= 10,
                pady= 10,
                sticky='snwe'
                )
        self.canvas.grid_columnconfigure(0, weight=1)
        self.canvas.grid_rowconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(self.window,
                                      orient='vertical',
                                      command= self.canvas.yview)
        self.scrollbar.grid(column=1, row=0, sticky='ns')
        # add a frame
        self.scroll_frame= ttk.Frame(self.canvas)

        # autoupdate the scrollable size as soon as
        # the area changed because we added sg.
        self.scroll_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion= self.canvas.bbox("all")
                    )
            )
        self.canvas.create_window((0,0),
                                  window= self.scroll_frame,
                                  anchor='nw')
        self.canvas.configure(yscrollcommand= self.scrollbar.set)
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
        # add a lot of frames into the frame
        self.add_content()
    # end init()


    def add_content(self):
        """ parse the template dict, and add elements to the
            main window accordingly.
        """

        keys = list(self.template.keys())
        N = len(keys)

        for j,i in enumerate(keys):
            v = self.template[i]
            if 'type' not in v:
                print('not a form element!', i, v)
                self.result[i] = v
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
                       stick='w')

            if v['type'] in ['text', 'numeric', 'integer', 'list']:
                entry = ttk.Entry(frame)

            elif v['type'] == 'select':
                entry = ttk.Combobox(frame)
                entry['values'] = v['options']
                # make it read only, so user cannot insert new values
                # alternative would be state 'normal'
                entry['state'] = 'readonly'
                entry.set(v['options'][0])

            elif v['type'] == 'multiline':
                # another text widget
                entry = MultilineText(frame)

            elif v['type'] == 'file':
                # files we are seeking contain other
                # experiments in the root_path
                # experiments are typically yaml files
                entry = FilePickerTextField(
                        parent= frame,
                        indir= self.root_path,
                        pattern='*.yaml'
                        )

            # put the new entry in place
            entry.grid(column= 1,
                       row= 0,
                       padx= (5,2),
                       pady=(2,2),
                       stick='e')

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


    def collect_results(self):
        """ fill up the results with this
        """
        for i,v in self.entrydict.items():
            self.result[i] = v.get()
        # end pulling results
        # here comes some validity checking....
        #
        # if all good, close:
        self.quit()

    # enf collect_results

    def quit(self):
        self.window.destroy()
    # end quit

# end of class FormBuilder


class FilePickerTextField(object):
    """ a small class to build a file picker in the form of
        a text field and a button. The button activates a
        file selector widget, and its results fills the text
        field. The text field is editable.
        Use possibly a relative path.
    """

    def __init__(self, parent= None, indir='.', pattern= '*.yaml'):
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
        self.pattern = pattern
        self.content = StringVar()

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


    def get_file(self):
        """ bring up a file dialog and get a file name
        """

        d = FileDialog(
                self.frame,
                title='Select file')
        fn = d.go(
                dir_or_file= os.path.join(self.dir,
                             self.content.get()),
                pattern= self.pattern
                  )
        if fn:
           self.content.set(fn)
    # end get_file


    def get(self):
        return os.path.relpath(
                self.content.get(),
                self.dir
                )
    # end get
# end FilePickerTextField


class MultilineText(object):
    """ a multiline text widget with scroll bars on it...
    """

    def __init__(self,
                 parent= None
                 ):
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


    def get(self):
        """ return the full content of the widget
        """
        return self.text.get('1.0','end')
    # end of get

# end of MultilineText

