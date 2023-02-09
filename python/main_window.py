#!/usr/bin/env python
""" The main window of the RDM-desktop system.
    It is a Tkinter widget that lists the content of the
    project dir, then calls itself to make changes or list
    other details.

    Author:     Tomio13
    License:    MIT
    Warranty:   None
    Date:       2023-01-20
    version:    0.1.0
    A first conceptual class to do listing hierarchy in
    the folder tree.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import simpledialog as tksd
# only absolute import works!
import project_config as pc
import project_dir as pd

# important global variables
__version__= '0.1.5'
config = pc.get_config()


class ListWidget(tk.Tk):
    """ A widget to provide a list of a folder, but in
        a controlled way. Also allow for selecting a folder,
        getting its content or get information about it
        looking into the local information file, typically a
        readme.md or similar.
    """
    def __init__(self,
                 title= '',
                 root_path='',
                 parent= None,
                 config= config,
                 level= 0
                 ):
        """ Create the window, its elements and its content.

            @param title        optional title to overwrite config
                                used when a line is clicked
            @param root_path    the current path
            @param parent       the parent object, if this is not the
                                first window
            @param config       a dictionary describing all configuration
                                parameters
                                For details, see pc.get_default_config()
            @param level        at which depth we are in the structure
            @return None
        """

        # store parameters:
        self.config = config
        self.level = level

        if 'projectsDir' not in config:
            raise ValueError('projectsDir not provided!')

        if root_path:
            self.root_path = root_path
        else:
            self.root_path = config['projectsDir']

        self.root_path = os.path.abspath(
                os.path.expanduser(
                    self.root_path
                    )
                )

        if self.level >0:
            # searchFolders should hold which subdir to use
            # in creating the content of the list box
            # in Project, we use what folders are there
            # when a project is picked, we go for its Data folder
            # This way the user can tune if we have more depth.
            # Default is nothing (like for Projects)
            #
            # root_path defines what we list out
            k = 'searchFolders'
            if k in self.config and len(self.config[k]) > self.level:
                last_element = self.config[k][self.level]
            else:
                last_element= ''

            self.root_path = os.path.join(
                    self.root_path,
                    last_element
                    )
        # this is for debugging
        print('level:', self.level)
        print(f'Path is {self.root_path}')

        # we should provide a title at clicks, but if not, use
        # the projects title:
        k = 'projectsTitle'
        if not title and k in self.config:
            self.title= self.config[k]

        self.title = title

        # at each level we may ask for a directory listing or
        # searching for files
        # why not fixed? One can decide a wiki like tree, where
        # e.g. text files are named the same way as folders, so
        # when one clicks the file, gets the folder list...
        # It is a bit vague at the moment, but keeps things flexible

        # first define what to ignore
        ignore= self.config['ignore'] if 'ignore' in self.config else []

        # search pattern should matter only for searching for files
        k= 'searchPattern'
        pattern = ''
        if k in self.config and len(self.config[k]) > self.level:
            pattern = self.config[k][self.level]
        print('pattern is set to:', pattern)

        self.target= 'dir' # default target
        k = 'searchTargets'
        if k in  self.config and len(self.config[k]) > self.level:
            self.target = self.config[k][self.level]

            if self.target == 'dir':
                print('listing directories')
                self.get_dirlist(ignore)
            else:
                print('listing files')
                self.get_filelist(pattern, ignore)

        # the window and its default parameters
        self.child_windows = []
        self.parent = parent

        # generate the window first
        if self.parent is None:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(self.parent)

        # Configure the window
        self.window.minsize(300,400)
        # transparency:
        self.window.attributes('-alpha', 0.5)
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

        # a title icon for the window manager
        # make sure the children can inherit this icon
        # If I try running the same in a child window, I am getting
        # an error, so do it only at the top level
        if self.parent is None:
            self.icon = tk.PhotoImage(file='./icons/RDM_desktop.png')
            self.window.iconphoto(True, self.icon)

        self.window.title(title)

        # Fill in content... we could have all these elements in
        # internal functions, if the user should be able to
        # redecorate the content. But it is not the case so:
        self.frame= tk.Frame(self.window, bd= 10)
        self.frame.grid(
                column=0,
                row=0,
                columnspan=10,
                rowspan=10,
                padx= 10,
                pady=10,
                sticky='snwe')
        # now, make sure the listbox in col 0, row 1 is scaled!
        # This is needed, so resizing the window will resize that
        # content with it.
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        # first row is a main label of the content
        self.label= tk.Label(self.frame, text= title)
        self.label.grid(column=0, columnspan=10, row=0)

        self.make_listbox()

        # third (last) row is the button to look up content
        self.button = tk.Button(
                self.frame,
                text='Add New',
                command= self.add_new
                )
        # make a nice, large button:
        self.button.grid(column= 7, columnspan= 3, row= 9)
    # end __init__


    def activate_item(self):
        """ what happens when one has selected an item in the
            list box, and pushed the select button?
            If we are in a project list, we get the dirs of
            the data dir (kind of repeating the listing).
            If it is a data folder, we need to list the YAML
            files in there.
        """
        indx = self.listbox.curselection()
        if not indx:
            print('Nothing was selected')
            return

        item = self.listbox.get(indx)

        full_path = os.path.join(
                self.root_path,
                item)

        if os.path.isfile(full_path):
            cmd= (config['editor'], full_path)
            subprocess.call(cmd)

        else:
            # in a data folder we look what is
            # defined already as a yaml file
            self.child_windows.append(
                ListWidget(
                title= item,
                root_path= full_path,
                parent= self.window,
                config= self.config,
                level= self.level+1
                )
            )
    # end activate item

    def get_dirlist(self, ignore= []):
        """ get a list of directories in the root_path
            Use self.root_path for the path,
            but drop those words in ignore.
            Fill upt the self.content_list list.

            @param ignore   list, list of names to ignore

            @return None    fill up the self.content_list
        """
        if not os.path.isdir(self.root_path):
            self.content_list = []
            print('Folder does not exist', self.root_path)
            return


        self.content_list = [i.name for i in os.scandir(self.root_path) \
            if i.is_dir() and i not in ignore]

        self.content_list.sort()
    # end get_dirlist


    def get_filelist(self, pattern, ignore):
        """ list up files in a folder based on a simple pattern,
            e.g. .yaml for all files ending with .yaml.
            If pattern starts with ., then use end of, else
            use starts with.

            Drop files which names are in ignore list.

            @param  pattern files to search for
            @param  ignore  a list of files to ignore

            @return None    fill up self.content_list
        """
        self.content_list = []
        if not os.path.isdir(self.root_path):
            print('Folder does not exist', self.root_path)
            return

        if pattern and pattern[-1] == '$':
            pattern = pattern[:-1]
            use_start = False
        else:
            use_start= True
        print('search for pattern:', pattern)

        for i in os.scandir(self.root_path):
            if i.is_file() or i.is_symlink():
                print('file:', i.name)

                if use_start:
                    print('check for start')
                    if i.name.startswith(pattern) and\
                        i.name not in ignore:
                        print(i, 'matches start')
                        self.content_list.append(i.name)
                else:
                    print('check for end')
                    if i.name.endswith(pattern) and\
                        i.name not in ignore:
                        print(i, 'matches end')
                        self.content_list.append(i.name)

        if self.content_list:
            self.content_list.sort()
    # end get_filelist

    def make_listbox(self):
        """ create and fill out the listbox of the GUI
            Use self.content_list to add the elements
            to the widget.

            @return: None
        """
        # next is the actual directory content (sub directories)
        # listbox with single selection
        self.listbox = tk.Listbox(self.frame, selectmode= tk.BROWSE)
        self.listbox.grid(
                column=0,
                columnspan= 9,
                row= 1,
                rowspan= 8,
                padx=1,
                pady=1,
                sticky='swne'
                )

        # make it scrollable:
        self.scrollbar= tk.Scrollbar(
                self.frame,
                bg='grey',
                orient='vertical',
                command= self.listbox.yview,
                takefocus= True
                )
        # we just make it sticky on top-bottom to expand the list box
        self.scrollbar.grid(column=9, row= 1, rowspan= 8, sticky='ns')
        self.listbox.config(yscrollcommand= self.scrollbar.set)

        self.listbox_fill()
        self.listbox.bind(
                '<Double-Button-1>',
                lambda x: self.activate_item()
                )
    # end make_listbox


    def listbox_fill(self):
        """ refresh the listbox content from self.content_list
        """
        if not self.listbox:
            print('Listbox is not defined!')
            return

        # clear the content
        self.listbox.delete(0, tk.END)
        # fill up the content (folder names)
        for i,j in enumerate(self.content_list):
            self.listbox.insert(i, j)
    # end listbox_fill


    def add_new(self):
        """ create a new item. Depending on the level and
            what we have (e.g. folders or files),
            we have to call different workers.
            Folders are created using: make_projects
            and a folder list template,
            files are created by using the form_from_yaml
        """
        # get first the name
        new_name = tksd.askstring('Name of the new object')
        if not new_name:
            return
        print('creating', new_name)

        template_file = ''
        k = 'templates'
        if k in config and len(config[k]) > self.level:
            template_file = config[k][self.level]

        if template_file and 'templateDir' in config:
            template_file = os.path.join(config['templateDir'],
                                         template_file)

        if self.target == 'dir':
            print('template file:', template_file)

            pd.make_dir(
                    os.path.join(self.root_path, new_name),
                    template_file
                    )
        else:
            print('we should call the GUI for yamls')

        # now, update the list
        self.listbox_fill()
    # end of add_new
# end of class ListWidget
