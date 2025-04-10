#!/usr/bin/env python
""" The main window of the RDM-desktop system.
    It is a Tkinter widget that lists the content of the
    project dir, then calls itself to make changes or list
    other details.

    Author:     Tomio13
    License:    MIT
    Warranty:   None
    Date:       2024-04-06
"""

import os
import subprocess
import tkinter as tk
from tempfile import NamedTemporaryFile
from tkinter import simpledialog as tksd
from tkinter.filedialog import askopenfilename
# from tkinter import font
import yaml


# now the local elements:
from .form_from_dict import FormBuilder, SubSet
from .project_config import (replace_text, get_config, save_config)
from .project_dir import make_dir
from .rdm_uploader import rdmUploader

from .rdm_templates import (read_record, save_record)
from .rdm_widgets   import RdmWindow

# important global variables (within the package)
__version__= '0.5.0'


class ListWidget():
    """ A widget to provide a list of a folder, but in
        a controlled way. Also allow for selecting a folder,
        or a file, and open a pop-up to work with its content.
    """
    # linter is complaining, but I need these for a reasonable
    # iterative function call:
    # pylint: disable=too-many-arguments
    def __init__(self,
                 config:dict,
                 title:str = '',
                 root_path:str ='',
                 parent:tk.Misc = None,
                 level:int = 0,
                 fontsize: int=12
                 ) -> None:
        """ Create the window, its elements and its content.

            Parameters:
            title        string     optional title to overwrite config
                                    used when a line is clicked
            root_path    string     the current path
            parent       window     the parent object, if this is not the
                                    first window
            config       dict       a dictionary describing all configuration
                                    parameters
                                    For details, see pc.get_default_config()

            level        int        at which depth we are in the structure
            fontsize     int        user can set the font size here

            return None
        """

        # store parameters:
        self.config = config
        self.level = level
        self.content_list = []

        self.root_path = root_path if root_path \
                    else self.get_config_element('projectDir')

        if not self.root_path:
            raise ValueError('projectDir not provided!')

        self.root_path = os.path.abspath(
                os.path.expanduser(
                    self.root_path
                    )
                )

        # store the root path for accessing the readme:
        original_path = self.root_path

        if self.level >0:
            # searchFolders should hold which subdir to use
            # in creating the content of the list box
            # in Project, we use what folders are there
            # when a project is picked, we go for its Data folder
            # This way the user can tune if we have more depth.
            # Default is nothing (like for Projects)
            #
            # root_path defines path that we list out
            self.root_path = os.path.join(
                    self.root_path,
                    self.get_config_element(
                    'searchFolders')
                    )

        # we should provide a title at clicks, but if not,
        # use the projects title:
        if not title:
            title = self.get_config_element('projectsTitle')
        else:

            # get what is selected:
            item_name = self.get_config_element('searchNames')
            title = f'{title} - {item_name} list'

        # at each level we may ask for a directory listing or
        # searching for files
        # why not fixed? One can decide a wiki like tree, where
        # e.g. text files are named the same way as folders, so
        # when one clicks the file, gets the folder list...
        # It is a bit vague at the moment, but keeps things flexible


        # this is for debugging
        print(f'level: {self.level}, Path is {self.root_path}')

        self.target = self.get_config_element(
                'searchTargets'
                )
        if not self.target:
            self.target= 'dir' # default target

        # we have all configuration filled up,
        # generate the GUI:
        # the window first
        self.window = RdmWindow(parent, title, fontsize)

        # destruction is defined in calling the class
        # self.window.bind('<Escape>', lambda event: self.window.destroy())
        self.window.bind('<Return>', lambda event: self.activate_item())
        # attach F1 to the local read-me editor command
        readme_path = os.path.join(original_path,
                                   self.get_config_element('readme'))
        if os.path.isfile(readme_path):
            self.window.bind('<F1>',
                         lambda event:
                            self.open_editor(readme_path)
                        )

        if ('save config' in self.config
            and self.config['save config']):
            config_button = tk.Button(
                self.window.header,
                text= 'config',
                command= self.edit_config
                )
            config_button.grid(column= 1, row= 0)


        # make the content
        self.make_listbox(self.window.content)

        if self.target=='file':
            upload_icon = tk.PhotoImage(file='./icons/upload.png')
            upload_button = tk.Button(
                    self.window.command,
                    image= upload_icon,
                    text="upload",
                    command= self.upload
                    )
            upload_button.image = upload_icon
            # upload_button.grid(column=2, columnspan=2, row=9)
            upload_button.grid(column=1, columnspan= 2, row=0)

        open_icon = tk.PhotoImage(file='./icons/folder.png')
        open_button = tk.Button(
                self.window.command,
                image= open_icon,
                command= self.file_manager
                )
        # to hav the image shown, you have to set it here too
        open_button.image = open_icon
        # open_button.grid(column=4, columnspan=3, row=9)
        open_button.grid(column=4, columnspan= 2, row=0)

        # third (last) row is the button to look up content
        button = tk.Button(
                self.window.command,
                text='Add New',
                command= self.add_new
                )
        # make a nice, large button:
        # button.grid(column= 7, columnspan= 3, row= 9)
        button.grid(column= 7, columnspan= 2, row=0)
    # end __init__


    def get_config_element(self, key:str) -> str:
        """ Get a config value out of the dict.
            If it is one of the lists, then
            dig into a list within config, get the
            element at self.level.

            Parameters
            key string  a key in config

            Return
            if self.config[key] is a list return its
            self.level value or ''
        """
        if key in self.config:
            if isinstance(self.config[key], list):
                if len(self.config[key]) > self.level:
                    return self.config[key][self.level]

            # if not a list, just return it
            else:
                return self.config[key]

        return ''
    # end get_config_element


    def file_manager(self) -> None:
        """ Open the current folder in a file manager
        """
        fm = self.get_config_element('filemanager')
        if fm:
            cmd= [fm, self.root_path]
            # open in a subprocess, but do not wait for it!
            with subprocess.Popen(cmd) as pop:
                print('child started:', pop)
    # end file_manager


    def activate_item(self) -> None:
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

        # turn it to a full path:
        full_path = os.path.join(
                self.root_path,
                item)

        # a file we open with the default editor
        if os.path.isfile(full_path):
            use_form = self.get_config_element('use form')
            if use_form:
                self.edit_form(full_path)
            else:
                self.open_editor(full_path)

        else:
            # in a data folder we look what is
            # defined already as a yaml file
            new_list= ListWidget(
                            title= item,
                            root_path= full_path,
                            parent= self.window.window,
                            config= self.config,
                            level= self.level+1
                        )
            self.window.withdraw()
            new_list.window.wait_window()
            self.window.deiconify()
    # end activate item


    def get_dirlist(self, ignore:list) -> None:
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


    def get_filelist(self, pattern:str, ignore:list) -> None:
        """ list up files in a folder based on a simple pattern,
            e.g. .yaml for all files ending with .yaml.
            If pattern starts with ., then use end of, else
            use starts with.

            Drop files which names are in ignore list.

            Parameters
            pattern     string  files to search for
            ignore      list    files to be ignored

            return:
            None    fill up self.content_list
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

        # do the compact list handling way:
        if use_start:
            self.content_list = [i.name\
                    for i in os.scandir(self.root_path)\
                    if i.name.startswith(pattern)\
                    and i.name not in ignore]
        else:
            self.content_list = [i.name\
                    for i in os.scandir(self.root_path)\
                    if i.name.endswith(pattern)\
                    and i.name not in ignore]

        if self.content_list:
            self.content_list.sort()
    # end get_filelist


    def make_listbox(self,
                     parent:tk.Misc) -> None:
        """ create and fill out the listbox of the GUI
            Use self.content_list to add the elements
            to the widget.
            Parameters:
            parent   a widget    parent widget

            return: None
        """
        # next is the actual directory content (sub directories)
        # listbox with single selection
        self.listbox = tk.Listbox(parent, selectmode= tk.BROWSE)
        # we define the content filling up the frame with a narrow
        # scroll-bar on the right
        parent.columnconfigure(0, weight=10)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=10)
        self.listbox.grid(
                column=0,
                # columnspan= 10,
                row= 0,
                # rowspan= 10,
                padx=0,
                pady=0,
                sticky='swne'
                )

        # make it scrollable:
        self.scrollbar= tk.Scrollbar(
                parent,
                bg='grey',
                orient='vertical',
                command= self.listbox.yview,
                takefocus= True
                )
        # we just make it sticky on top-bottom to expand the list box
        self.scrollbar.grid(column=1, row= 0, sticky='ns')
        self.listbox.config(yscrollcommand= self.scrollbar.set)

        self.listbox_fill()
        self.listbox.bind(
                '<Double-Button-1>',
                # activate_item takes self only, needs nothing else
                # the callback also throws the object at it, so we
                # strip that:
                lambda x: self.activate_item()
                )
    # end make_listbox


    def listbox_fill(self) -> None:
        """ refresh the listbox content from self.content_list
        """
        if not self.listbox:
            print('Listbox is not defined!')
            return

        # clear the content
        print('at level:', self.level)
        self.listbox.delete('0', 'end')

        # first define what to ignore
        ignore= self.config['ignore'] if 'ignore' in self.config else []

        # load / reload folder content
        if self.target == 'dir':
            print('listing directories')
            self.get_dirlist(ignore)
        else:
            print('listing files')
            # search pattern should matter only for searching for files
            pattern = self.get_config_element(
                'searchPattern'
                )
            self.get_filelist(pattern, ignore)

        # fill up the content (folder names)
        for i,j in enumerate(self.content_list):
            self.listbox.insert(i, j)
    # end listbox_fill


    def make_readme(self, default_template:str, new_path:str) -> None:
        """ Create the readme file in a new folder
            based on information provided.

            Parameters:
            default_template    string  path to the template file
            new_path            string  the path of the new folder
        """
        if not default_template:
            return

        txt= ''
        if os.path.isfile(default_template):
            with open(default_template,
                      'rt',
                      encoding='UTF-8') as fp:
                txt = fp.read()

        if txt:
            # this file does not suppose to exist!
            txt = replace_text(
                    txt,
                    self.config,
                    os.path.join(self.root_path,
                                  new_path)
                    )

            readme_path = self.get_config_element('readme')
            if not readme_path:
                raise ValueError('Readme should be defined!')

            with open(os.path.join(
                    new_path,
                    readme_path),
                    'wt',
                    encoding='UTF-8') as fp:
                fp.write(txt)

        ed = self.get_config_element('editor')

        if ed :
            self.open_editor(os.path.join(new_path, readme_path))
    # end make_readme


    def run_form(self,
                 template_dir:str,
                 default_template:str,
                 label:str,
                 new_path:str) -> bool:
        """ run the form builder and save its result

            Parameters:
            template_dir        string  where the templates are
            default_template    string  we load first this
                                        template, appended by
                                        a user selected template
            label               string  title of new form
            new_path            string  path to the new file

            Return:
            True if we changed the list, so refresh is needed
        """
        # now, we have to get the templates,
        # put them together and call the form machine
        # then dump the result...
        template_dict= {}

        # let the user pick the template file name:
        fn = askopenfilename(title='Select template form',
                filetypes=[('yaml', '*.yaml'), ('yml', '*.yml')],
                initialdir= template_dir,
                defaultextension='yaml')

        # this is a generic reader, that takes care of
        # merging templates and data, etc...
        # returns an empty dict on any problem
        print('Default template:', default_template)
        template_dict = read_record(None, default_template, fn)
        if not template_dict:
            print('Empty template / or no template')
            return False


        form = FormBuilder(
                title= f'Form of {label}',
                root_path= self.root_path,
                parent= self.window.window,
                template= template_dict,
                config= self.config)

        # we have to get stuck here until it comes back
        # form.window.mainloop()
        self.window.withdraw()
        form.window.wait_window()
        self.window.deiconify()

        if form.result:
            full_record= ('full record' in self.config and self.config['full record'])

            print('saving file to', new_path, end=' ')
            res= save_record(form.result,
                             new_path,
                             overwrite= False,
                             full_record= full_record)
            if res:
                print('...done')
            else:
                print('...failed')

            return res

        # nothing saved, do not refresh
        return False
    # end run_form


    def edit_form(self, full_path:str) ->None:
        """ take a yaml file, and try turning it back to
            a form. Display this form then.

            parameters
            full_path:  path to the yaml file

            return:
            nothing
        """
        # the path was checked before the call...
        default_template = self.get_config_element(
            'defaultTemplate'
            )

        template_dir = self.get_config_element('templateDir')

        # this should get a full record or an empty template
        form_data = read_record(full_path,
                                os.path.join(template_dir,
                                            default_template),
                                template_dir)

        if not form_data:
            print('template not found, calling editor')
            self.open_editor(full_path)
            return

        label = self.get_config_element(
            'searchNames'
            )
        form = FormBuilder(
            title= f'Form of {label}',
            root_path= self.root_path,
            parent= self.window.window,
            template= form_data,
            config= self.config)

        # we have to get stuck here until it comes back
        # form.window.mainloop()
        if form:
            self.window.withdraw()
            form.window.wait_window()
            self.window.deiconify()

        if form.result:
            # here we do not have to refresh
            # the file list, so the return value
            # does not matter
            print('overwriting file:', full_path)
            #full_record = (('full record' in form.result
            #               and form.result['full record'])
            #               or ('full record' in self.config
            #                   and self.config['full record'])
            #               )
            # If config says to save a full record, do it.
            # But inside we do use one...
            full_record = ('full record' in self.config
                               and self.config['full record'])
            save_record(form.result,
                        full_path,
                        overwrite= True,
                        full_record= full_record)

    #end edit_form


    def edit_config(self):
        """ call an editor on the configuration content...
            For this, create a temporary file, let the user
            edit it, then reload it.
            """
        # create a temporary file, and dump the config into it
        fp = NamedTemporaryFile('wt', delete= False, encoding= 'UTF-8')
        yaml.dump(self.config, fp)
        fname = fp.name
        fp.close()

        # now, call an editor on it
        print('Temp config file to edit', fname)
        self.open_editor(fname)
        # after done:
        with open(fname,
                  'rt',
                  encoding= 'UTF-8') as fp:
           this_config= yaml.safe_load(fp)

        os.unlink(fname)
        # end loading back
        if this_config:
            if ('save config' in this_config
                and this_config['save config']):
                # we write the config
                save_config(this_config)
                # then load it back, ensuring
                # that defaults are in place
                self.config = get_config()

    # end edit_config

    def open_editor(self, full_path):
        """ Open a yaml file using the editor in config
        """
        ed = self.get_config_element('editor')
        if ed:
            cmd = ed.split(' ')
            print('calling editor as:', cmd + [full_path])
            subprocess.call(ed.split(' ') + [full_path])
    # end open_editor


    def add_new(self) -> None:
        """ create a new item. Depending on the level and
            what we have (e.g. folders or files),
            we have to call different workers.

            Folders are created using: make_projects
            and a folder list template,

            Files are created by using the form_from_yaml
        """
        # get first the name
        label = self.get_config_element(
                'searchNames'
                )

        # get the name of the new item:
        new_name = tksd.askstring(f'Add {label}',
                                  f'Name of the new {label}')
        if not new_name:
            return

        print('creating', new_name)

        template_dir = self.get_config_element('templateDir')

        default_template = self.get_config_element(
                'defaultTemplate'
                )

        # this is a text file containing either yaml
        # or plain text
        if default_template and template_dir:
            default_template= os.path.join(template_dir,
                                            default_template)

        # now, make the path
        new_path = os.path.join(
                self.root_path,
                new_name
                )

        if self.target == 'dir':
            # do no work if it were in vain:
            if os.path.isdir(new_path):
                print('folder already exists!')
                return

            # this is the subfolder structure:
            template_file = self.get_config_element(
                'templates'
                )

            if template_file and template_dir:
                template_file = os.path.join(template_dir,
                                         template_file)

            print('template file:', template_file)

            make_dir(
                    new_path,
                    os.path.abspath(template_file)
                    )

            # we should add a readme, and we may have
            # templates for it:
            self.make_readme(default_template, new_path)

        else:
            if os.path.isfile(new_path):
                print('file already exists!')
                return

        # now, update the list. If nothing changed, just go back.
            if not self.run_form(template_dir,
                                 default_template,
                                 label,
                                 new_path):
                return
        self.listbox_fill()
    # end of add_new


    def upload(self) -> None:
        """ pick the selected file, and try an upload to
            a server.
        """
        if not self.target == 'file':
             return

        indx = self.listbox.curselection()
        if not indx:
            print('Nothing was selected')
            return

        # get what is selected:
        item = self.listbox.get(indx)
        if not item.endswith('yaml'):
            item = f'{item}.yaml'
        # turn it to a full path:
        record = os.path.join(
                self.root_path,
                item)

        rdmUploader(
                record,
                self.config,
                self.level,
                self.window.window
                )
    # end upload
# end of class ListWidget
