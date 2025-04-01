#!/usr/bin/env python
""" The main executable of the project, using all elements here.
    This way the main ListWidget can be reused if needed in
    other projects.

    Author:     Tomio
    License;    CC-BY(4)
    Date:       2023-01-31
    Warranty:   None
"""

import rdm_modules.main_window as mw
from rdm_modules.project_config import get_config

print(get_config())

if __name__ == '__main__':
    print('Starting RDM-desktop GUI')
    GUI = mw.ListWidget(config = get_config())
    GUI.window.mainloop()

