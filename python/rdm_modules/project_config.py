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
import time
import yaml


def get_config_dir() -> str:
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


def get_default_config() -> dict:
    """ Read some system variables to set some default values
        for the configuration.

        Read the ../templates/default_configuration if possible,
        or go for default values.

        return value
        a dict containing the configuration parameters.
    """
    version = 0.90

    if os.name == 'posix':
        home_dir = os.getenv('HOME')
        editor='nano'
        filemanager='xdg-open'
    else:
        # let us try come up with a preference list
        # for default location:
        # we can default to:
        # os.getenv('HOMEDRIVE')
        # os.getenv('HOMEDPATH')
        home_dir = 'd:/' if os.path.isdir('d:/')\
                else os.path.join(os.getenv('HOMEPATH'), 'Documents')
        editor= 'notepad'
        filemanager= 'explorer'

    #template_dir = os.path.join(config_dir, 'Templates')
    template_dir = '../templates'
    # now, get the YAML file if it exists:
    template_path = os.path.join(template_dir,
                         'default_configuration')
    if os.path.isfile(template_path):
        with open(template_path, 'rt', encoding='UTF-8') as fp:
            custom_config= yaml.safe_load(fp)

    # projects_dir = os.path.join(home_dir, 'Projects')

    userID = os.getlogin()

    # we may still need:
    # - readme template (MD files)
    # - default template for forms
    default_config= {
            'homeDir': home_dir,
            'save config': True,
            'userID': userID,
            'templateDir':  template_dir,
            'projectDir':   'Projects',
            'readme':       'readme.md',
            'filemanager':  filemanager,
            'version':      version,
            'use form':     True,
            'editor':       editor,
            'chemicals':    'Chemicals',
            'equipment':    'Equipment',
            'ignore':       ['References', 'Chemicals', 'Equipment'],
            # for connecting to an existing upload source,
            # we may have a default configuration here
            # first server link, then the token
            'server':       {'server':'', 'token':''},
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

    # take over the custom settings, if there is any:
    if custom_config:
        default_config.update(custom_config)

    # now, clean up:
    home_dir = default_config.pop('homeDir')

    default_config['projectDir'] = os.path.join(
             home_dir,
             default_config['projectDir']
                )
    for k in ['chemicals', 'equipment']:
        dck = default_config[k]
        if not (dck.startswith('/')
            or dck[1:].startswith(':/')
            or dck[1:].startswith(':\\')):
            # relative path is specified
            default_config[k] = os.path.join(
                    default_config['projectDir'],
                    dck)
    # end cleaning up paths

    return(default_config)
# end get_default_config


def get_config() -> dict:
    """ Find the config folder, and try pulling up the configuration.
        Substitute non-existing values with their default counterpart.

        Read the ../templates/default_configuration if possible,
        or go for default values.

        return
        a dict with the configuration
    """
    # is there a configuration already saved?
    config_dir= get_config_dir()
    config_path = os.path.join(config_dir, 'config.yaml')

    if not os.path.isfile(config_path):
        print('Configuration not found')
        conf = get_default_config()
        if ('save config' in conf
            and conf['save config']):
            print('Saving default configuration')
            save_config(conf)
        else:
            print('configuration is not saved')

        return conf

    with open(config_path,
              'rt',
              encoding='utf8') as fp:
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


def load_config() -> dict:
    """ it is get_config, just for making sure we do not
        miss the name
    """
    return get_config()
# end load_config


def save_config(config: dict) -> None:
    """ take a dict, and write it to the default config
        location as YAML file made by pyyaml.
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


def replace_text(text: str, config: dict, root_path: str) -> str:
    """ search for specific replacement characters and fill them up
        with dynamic content.

        Current spacers:
        %1, %2, %3:         project name, Data, sample name from the
                            folder name
        %u                  userID from config
        %d                  current date in ISO 8601 format
        %D                  current date, time and time zone in ISO
                            8601 format.

        Parameters:
        text        string  the text to be scanned
        config      dict    configuration dict, we use the project
                            path, userID from it
        root_path   string  the path of the current object
                            splitting it up, we get names of the
                            current project and sample (typically)
        return:
        string with spacers substituted
    """

    if '%' not in text:
        return text

    relpath = os.path.relpath(root_path, config['projectDir'])

    # windows may have '\\' instead of '/'
    if '\\' in relpath:
        relpath = relpath.split('\\')
    else:
        relpath = relpath.split('/')

    rep = {f'%{i+1}':j for i,j in enumerate(relpath)}

    rep['%u'] = config['userID']
    rep['%d'] = time.strftime('%Y-%m-%d', time.localtime())
    rep['%D'] = time.strftime('%Y-%m-%d %H:%M %z', time.localtime())

    for i,v in rep.items():
        text= text.replace(i, v)

    return text
# end of replace_text
