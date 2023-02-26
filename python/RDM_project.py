#!/usr/bin/env python
""" The main executable of the project, using all elements here.
    This way the main ListWidget can be reused if needed in
    other projects.

    Author:     Tomio
    License;    MIT
    Date:       2023-01-31
    Warranty:   None
"""

import main_window as mw
from project_config import get_config


if __name__ == '__main__':
    print('Starting RDM-desktop GUI')
    GUI = mw.ListWidget(config = get_config())
    GUI.window.mainloop()

