#!/usr/bin/env python
""" Generic uploader tool for experiments.
    Author:     Tomio
    License:    MIT
    Date:       2023-03-17
    Warranty:   None
"""

import json
import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from rdm_modules.rdm_widgets import (EntryBox, CheckBox, RdmWindow)
from rdm_modules.rdm_templates import (read_record, save_record)

from rdm_modules.rdm_converters import convert_record_to_JSON

# List here all uploaders for the various ELNs
from rdm_modules.uploaders.ElabFTW import upload_record as elabFTW

# and yaml:
import yaml

# In this dict we combine the name of ELNs and the functions
# to do the upload
# Every function receives a dict for the record to be processed
# the server URL and the security token as:
#
#   title:str,
#   record:dict,
#   record_path:str,
#   server:str,
#   token:str,
#   verify= True
#
# It is the job of the functions to tune the format to the actual ELN.
# The functions return a dict containing:
# server:   link to server (https...)
# id:       the ID of the new record on the server
# date:     date and time of the upload
uploader_dict = {
        "ElabFTW":elabFTW
        }


class rdmUploader():
    """ a GUI window with elements to manage an upload
    """

    def __init__(
            self,
        record:str,
        config:dict,
        level:int,
        parent:tk.Misc = None
        )->None:
        """ A GUI coordinating the upload of an experiment
            to the server.
            It uses the generic converters to form a JSON
            ready dict from the experiment and its templates,
            then takes a selected uploader to do the transfer.
            Every ELN or srevice can have its own uploader function.
            (These functions also do internal conversion of the record
            to match the requirements of the DB.)
        """
        if parent is None:
            window = RdmWindow(parent, title='Upload record')
        else:
            window = tk.Toplevel(parent)
        window.lift()
        window.title('Upload record')
        window.grid()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        self.window = window

        frame = tk.Frame(window)
        frame.grid(column= 0, row= 0)
        frame.columnconfigure(0, weight=1)
        global uploader_dict

        # the frame content is:
        # 1. record
        # 2. server address
        # 3. sec. token
        # 4. ELN type
        txt = os.path.split(record)[-1]
        record_label = tk.Label(frame,
                                text= f'Selected: {txt}'
                                )
        record_label.grid(column=0, row=0, sticky='news')

        label = tk.Label(frame, text='Server address')
        label.grid(column=0, row=1, sticky='w')
        self.server_address = EntryBox(frame,
                                       vartype='text',
                                       )
        if 'server' in config and 'server' in config['server']:
            if config['server']['server']:
                self.server_address.set(config['server']['server'])

        self.server_address.grid(column= 1,
                                 row= 1,
                                 sticky='ew')

        # now, the secutiry token
        label = tk.Label(frame, text='Server token')
        label.grid(column=0, row=2, sticky='w')
        self.server_token = EntryBox(frame,
                                     vartype='text',
                                     )

        if 'server' in config and 'token' in config['server']:
            if config['server']['token']:
                self.server_token.set(config['server']['token'])

        self.server_token.grid(column= 1,
                               row= 2,
                               sticky='we'
                               )

        # the ELN type (right now only ElabFTW
        label = tk.Label(frame, text='ELN type')
        label.grid(column=0, row=3, sticky='w')
        self.eln_type = ttk.Combobox(frame)
        eln_list = list(uploader_dict.keys())
        self.eln_type['values'] = eln_list
        self.eln_type.set(eln_list[0])

        self.eln_type.grid(column= 1,
                           row= 3,
                           sticky='we'
                           )

        for i in range(4):
            frame.rowconfigure(i, weight=1)
        # end setting widgets scaling

        button = ttk.Button(frame,
                            text= 'Upload',
                            command= lambda: self.upload(
                                                    record,
                                                    config,
                                                    level
                                                    )
                            )

        button.grid(column=1, row=4, sticky='se')
    # end __init__


    def upload(self,
               record_path:str,
               config:dict,
               level:int,
               )->None:
        """ Manage the upload by:
            - getting the metadata content
            - merging it with the template to a full record
            - invoke the selected uploader
            - append upload information to the record

            Check the 'Uploaded' field for the server, and
            avoid double uploading.

            The 'Uploaded' field should contain at least:
            'server':   the https... link to the server
            'link':     the actual link to the current record
            It also may have: 'id' for the record and a 'date' of upload
        """

        global uploader_dict
        print('upload was requested')

        k = 'templateDir'
        if (config and k in config):
            template_dir = config[k]
        k = 'defaultTemplate'
        if (config and k in config):
            default_template = os.path.join(template_dir, config[k][level])

        record = read_record(record_path,
                             default_template,
                             template_dir)
        if not record:
            errorshow('error', f'File not found: {record_path}')
            return

        # clean up somewhat

        if 'Uploaded' in record:
            uploaded = record.pop('Uploaded')
        else:
            uploaded = {}

        record_converted = convert_record_to_JSON(record)
        print('record:\n', record_converted)

        title = os.path.splitext(os.path.basename(record_path))[0]
        title = title.replace('_', ' ')

        # collect the info of the form:
        # server link, token, eln
        server = self.server_address.get()
        token = self.server_token.get()
        uploader_key = self.eln_type.get()

        if uploader_key in uploader_dict:
            up_func = uploader_dict[uploader_key]
        else:
            showerror('error', 'Uploader not found!')
            return

        # locally we allow self-signed certs
        if '127.0.0.1' in server:
            verify= False
        else:
            verify = True

        if uploaded:
            if isinstance(uploaded, dict) and 'server' in uploaded:
                if server == uploaded['server']:
                    showerror('exists',
                              f'Record is already uploaded at: {uploaded["link"]}')
                    return
            else:
                for i in uploaded:
                    if 'server' in i and server == i['server']:
                        showerror('exists',
                                  f'Record is already uploaded at {i["link"]}')
                        return
        # end checking if record is uploaded to this server

        # we upload the JSON safe version, record_converted
        upload_result= up_func(
                        title,
                        record_converted,
                        os.path.dirname(record_path),
                        server,
                        token,
                        verify= verify)

        if uploaded:
            if isinstance(uploaded, list):
                uploaded.append(upload_result)
            else:
                uploaded = [upload_result]
        else:
            uploaded = upload_result
        # now, write back the record

        # update the record with upload information
        record['Uploaded'] = uploaded

        # dump the record back
        # if one had comments in this YAML, those are gone...
        # If the record has 'full record', then is is a full record
        # else, we may be switching to full records in config, so we allow that too
        full_record = (('full record' in record and record['full record'])
                       or ('full record' in config and config['full record'])
                       )

        save_record(record, record_path, overwrite=True, full_record= full_record)
        self.window.destroy()
    # end of upload
# end rdmUpload

