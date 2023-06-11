#!/usr/bin/env python
""" Converter functions to turn a template and a data set dict to something
    which can be exported to JSON and to be uploaded to various ELNs.
    For a start, using ElabFTW.

    JSON is a little more restricted than YAML, thus these restrictions
    have to be handled deep in the dicts.

    Author:     Tomio
    License:    MIT
    Date:       2023-03-05
    Warranty:   None
"""

import datetime
import os
import yaml
from yaml.scanner import ScannerError

from rdm_modules.project_config import get_config, replace_text
from rdm_modules.rdm_templates import (merge_templates,
                           list_to_dict,
                           combine_template_data)


def convert_record_to_JSON(data:dict)->dict:
    """ take a record, which may contain already data
        merged with its template, and clean it up such
        that we can save it to a JSON file for upload.

        JSON cannot handle all data types, like 'date', which
        needs to be turned to string.

        parameters:
        data:       dict to be converted

        return:
        dict converted
    """
    if not data:
        return {}

    res = data.copy()

    # currently the datetime is the only problem
    # in our system... this we dig out

    for k,v in data.items():
        if isinstance(v, datetime.date):
            res[k] = str(v)

#        elif isinstance(v, bool):
#            res[k] = int(v)

        elif isinstance(v, dict):
            res[k] = convert_record_to_JSON(v)

    return res
# end convert_record_to_JSON


def guess_type(value)->str:
    """ take a variable and guess its type from the common
        RDM types
        This method cannot find a select type, since for those
        it should see the options. A value of a select type is
        a string.

        parameters
        value:   any python variable

        return:
        string with the type, or None if not found
    """
    type_dict={
            "text":     str,
            "numeric":  float,
            "integer":  int,
            "list":     list,
            "checkbox": bool,
            }

    this_type= None
    for k,v in type_dict.items():
        if isinstance(value, v):
            this_type = k
    # end for

    if this_type == 'text' and '\n' in value:
        this_type='multiline'
    elif this_type == 'list' and isinstance(value[0], (int, float)):
        this_type= 'numericlist'
    elif this_type == 'list' and isinstance(value[0], dict):
        this_type= 'subset'

    return this_type
# end of guess_type


def guess_template(data:dict)->dict:
    """ Take a record, and try guessing the types of fields where
        type is not available.

        parameters:
        data:   a record

        return:
        the same dict complemented with type fields
    """
    if not data:
        return data

    for k,v in data.items():
        if isinstance(v, dict) and 'type' not in v:
            # guess a type independent of value
            this_type = guess_type(v['value'])
        else:
            data[k] = dict()
            data['value'] = v
            this_type = guess_type(v)

        if this_type is None:
            print('Unknown type for:', k,':', v)
            print('set default to text')
            this_type= 'text'

            if 'value' in v:
                v['value'] = str(v['value'])

        data[k]['type'] = this_type

    return data
# end off guess_template


def is_record(full_path:str,
              key_list:list = ['template', 'template version', 'user', 'created']
              )->bool:
    """ Take a file content, try loading it as yaml,
        and check if it can be assumed to be an experiment record
        If the file is not a .yaml or .yml or does not exist, return False.

        parameters
        full_path:      path to the file
        key_list:       a list of keys to check for a valid record

        return:
        True if the file is:
        - a YAML file
        - contains a dict of dicts
        - and has all keys in the list
    """

    if not os.path.isfile(full_path):
        return False

    if not (full_path.endswith('.yaml')
            or full_path.endswith('.yml')):
        return False

    try:
        with open(full_path, 'rt', encoding='UTF-8') as fp:
            a = yaml.safe_load(fp)

    except ScannerError:
        print(full_path, 'is not YAML file')
        return False

    if isinstance(a, dict):
        all_dicts = [isinstance(a[i], dict) for i in a]
        all_match = [i in a for i in key_list]

        if all(all_dicts) and all(all_match):
            return True

    return False
# end is_record
