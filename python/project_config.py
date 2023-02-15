#!/usr/bin/env python
""" Functions to get/save configuration information for the program.
    Intended to be used on YAML configuraiton files for all kinds
    of OS-es.

    Author:     Tomio
    Date:       2023-01
    License:    MIT
    Warranty:   None
"""
import os
import sys
import yaml


def get_config_dir():
    """ Based on the OS, get the /home/$user/.config/rdm_project
        or the c:/users/%user%/AppData/Local folder.
    """
    uname = sys.platform
    if uname.startswith('win'):
        homedir = os.getenv('localAppData')
        dirname = os.path.join(homedir, 'rdm_project')
    else:
        # 'linux', 'darwin' or anything similar
        homedir = os.getenv('HOME')
        dirname = os.path.join(homedir, '.config/rdm_project')

    return dirname
# end get_config_dir


def get_default_config():
    """ Read some system variables to set some default values
        for the configuration.
    """
    version = 0.2
    config_dir = get_config_dir()

    if os.name == 'posix':
        home_dir = os.getenv('HOME')
        editor='nano'
        filemanager='xdg-open'
    else:
        home_dir = 'd:/' if os.path.isdir('d:/') else 'c:/'
        editor= 'notepad'
        filemanager= 'explorer'

    #template_dir = os.path.join(config_dir, 'Templates')
    template_dir = '../templates'
    projects_dir = os.path.join(home_dir, 'Projects')

    userID = os.getlogin()

    # we may still need:
    # - readme template (MD files)
    # - default template for forms
    return {'userID': userID,
            'templateDir':  template_dir,
            'projectDir':   projects_dir,
            'readme':       'readme.md',
            'filemanager':  filemanager,
            'version':      version,
            'editor':       editor,
            'ignore':       ['References'],
            'projectsTitle': 'Projects',

            # the search fields specify how to
            # handle the folder tree...
            # top is the projects, then samples,
            # then experiments
            # we start with 'projectDir' within:
            'searchFolders': [
                '',
                'Data',
                ''],
            'searchNames': [
                'project',
                'sample',
                'experiment'],

            'searchTargets': [
                'dir',
                'dir',
                'file'],

            'searchPattern': [
                '',
                '',
                'yaml$'],

            'templates':    [
                'folderlist',
                '',
                ''],

            # default template is loaded for any
            # experiment,
            # for directories it is a default Readme.md
            # content to start with
            'defaultTemplate':  [
                'readmeProject',
                'readmeSample',
                'defaultForm']
            }
# end get_default_config


def get_config():
    """ Find the config folder, and try pulling up the configuration.
        Substitute non-existing values with their default counterpart.
    """
    # is there a configuration already saved?
    config_dir= get_config_dir()
    if not os.path.isdir(config_dir):
        print('Configuration not found')
        conf = get_default_config()
        print('Creating default configuration')
        save_config(conf)
        return conf

    with open(os.path.join(config_dir, 'config.yaml'),
              'rt', encoding='utf8') as fp:
        conf = yaml.safe_load(fp)
    # we got a config

    # get the default and check out what is missing
    def_conf = get_default_config()

    # if there was a version change, we must
    # update the cofiguration
    if 'version' not in conf\
        or conf['version'] != def_conf['version']:
        must_save = True
        # update the version!
        conf['version'] = def_conf['version']

    else:
        must_save = False

    for k,v in def_conf.items():
        if k not in conf:
            conf[k] = v

    if must_save:
        save_config(conf)

    return conf
# end get_config


def load_config():
    """ it is get_config, just for making sure we do not
        miss the name
    """
    return get_config()
# end load_config


def save_config(config):
    """ take a dict, and write it to the default config
        location.
    """
    if not config:
        return

    config_dir = get_config_dir()

    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    with open(os.path.join(config_dir, 'config.yaml'),
                   'wt',
                   encoding='utf8') as fp:
        yaml.dump(config, fp)
# end save_config
