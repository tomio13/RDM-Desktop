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
import yaml
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
            if 'value' in v:
                data[k]['type'] = guess_type(v['value'])
            else:
                print('Unknown dict type', v)
        else:
            data[k] = dict()
            data['value'] = v
            data['type'] = guess_type(v)

    return data
# end off guess_template
