#!/usr/bin/env python
""" Create a folder tree based on a configuration file and the main folder
    provided by the call.

    Author:     Tomio
    License:    MIT
    Warranty:   None
    Date:       2023-01
"""

import os
import sys
__all__ = ['make_project']

list_file = 'templates/folder.txt'

def make_dir(folder_name, list_file_path):
    """ Create a folder directory and all its subdirectories.

        Parameters:
        @parameter folder_name  name of the new project folder
        @parameter list_file_path   a file where the subfolders are
                                    listed.
        @return None
    """
    folder_name = os.path.abspath(
            os.path.expanduser(folder_name)
            )

    # create the main directory
    # use 'brute force', thus make all intermediates in the path,
    # and do nothing if it exists
    os.makedirs(folder_name, exist_ok= True)

    if os.path.exists(list_file):
        with open(list_file, 'rt', encoding='utf-8') as fp:
            txt_list = fp.readlines()

        if txt_list:
            print('Read:', len(txt_list),'lines')
            # each line should be a folder name
            # or starts with #, meaning comment
            for line in txt_list:
                # readlines leaves the end newline character
                # so cut it off:
                line = line[:-1]
                # count what we create:
                i = 1
                if line.startswith('#'):
                    print(line)
                    continue
                # make the dirs
                fn = os.path.join(main_folder, line)
                print('creating folder:', fn)
                os.makedirs(fn, exist_ok= True)
                i += 1
            print('Created', i, 'folders')
    # all is done
# end make_project

if __name__ == '__main__':
    main_folder= './'
    args = sys.argv[1:]
    if args:
        # first argument is the new project folder
        main_folder = args.pop(0)
        if args:
            # file name of the folder list
            if args[0] == '-c' and len(args) > 1:
                list_file = args[1]
            else:
                print('Invalid parameter:', txt)
                sys.exit(0)

    # do the job
    make_dir(main_folder, list_file)

