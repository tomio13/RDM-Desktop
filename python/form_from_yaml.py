#!/usr/bin/env python
""" Create a GUI to load information based on a yaml file and emmit another yaml with
    the resulted content.
    A standalone version and testibed of the FormBuilder class.

    Author:     Tomio
    License:    MIT
    Date:       2023-01
    Warranty:   None
"""

import yaml
import os
import sys
import rdm_modules.project_config as pc
import tkinter as tk
from tkinter.filedialog import askopenfile
import rdm_modules.form_from_dict as ffd

config = pc.get_config()

output_file= ''

# now, we have a dict describing what to load
template = {}

with open(
        os.path.join(
            config['templateDir'],
            config['defaultForm'][-1]
            ),
        'rt') as fp:
    template = yaml.safe_load(fp)

with askopenfile(title='Select template form',
                        mode='r',
                        filetypes=[('yaml', '*.yaml'), ('yml', '*.yml')],
                        initialdir= config['templateDir'],
                 defaultextension='yaml') as fp:
    template_2 = yaml.safe_load(fp)

if template and template_2:
    template.update(template_2)
elif template_2:
    template = template_2

form = ffd.FormBuilder(root_path='./',
                   template= template,
                   config= config)

form.window.mainloop()

res = form.result

