#!/usr/bin/env python
""" Functions to handle templates, then merge values into templates
    to produce publishable records.

    There is a default template and a selected one which must be merged.

    JSON is a little more restricted than YAML, thus these restrictions
    have to be handled deep in the dicts.

    Author:     Tomio
    License:    MIT
    Date:       2023-03-05
    Warranty:   None
"""

import os
import yaml


def merge_templates(filename:str, default_file:str)->dict:
    """ Based on configuration and a template path, merge
        the default template and the requested template to
        a single dict.

        paramters:
        filename:   the path to the template
        default_file:   the path to the default template

        return:
        dict containing the template
    """
    if not os.path.isfile(default_file):
        print('Default template not found')
        default_template = {}
    else:
        with open(default_file, 'rt', encoding='UTF-8') as fp:
            default_template = yaml.safe_load(fp)

    if not os.path.isfile(filename):
        print('template not found!')
        return {}

    with open(filename, 'rt', encoding='UTF-8') as fp:
        template = yaml.safe_load(fp)

    default_template.update(template)

    return default_template
# end merge_templates


def list_to_dict(data:list,
                 simple:bool = True) -> dict:
    """ In results we have subsets, which are recorded
        as lits of dicts with the keys repeating.
        These can be turned back to a dict with the
        same keys, but lists as their values.

        Since it is possible that we have subsets within
        the values, it has to be handled recursively.

        This algorithm is goes the slower way, checking
        that every key is the apropriate one.
        (In the form_to_dict system, we go blindly adding
        the values.)
        However, keys are generated from the first entry,
        so if something is missing there, it gets dropped.

        parameters:
        data    the list of dicts, typically a subset
        simple  if True, check in the list, if any of
                the values in the dicts is a dict, just
                turn the list to a dict with keys as
                numbers from 0 to len(data)-1

        return:
        a dict containing the results
    """

    if not data:
        return {}

    if not isinstance(data, list):
        print('cannot convert non list to dict!')
        return data


    keys = []
    for element in data:
        if element and isinstance(element, dict):
            keys = list(element.keys())
            break

    # we want it simplified, if necessary,
    # thus when any of the values are lists
    # of dicts,
    # meaning it was a subset in subset
    # (We already have a nice dict tree
    # from the form builder...)
    if simple:
        # we can have a list of numbers, strings, or dicts
        # only the last one is a subset...
        # however, it can also be None
        for i in element.values():
            if isinstance(i, list):
                if any([isinstance(j, dict) for j in i]):
                    return {k:v for k,v in enumerate(data)}

    # else, we go on, and fold the tree
    # into a list of lists if needed
    values = [list() for i in keys]

    for line in data:
        if line is None:
            print('empty line found')
            for i in range(len(keys)):
                values[i].append(None)
            continue

        for i,k in enumerate(keys):
            # if we have a dict inside, we have
            # a subset in subset.
            # We unfold it running recursively
            # At this point we do not simplify anymore
            if isinstance(line[k], list) \
                and isinstance(line[k][0], dict):
                values[i].append(list_to_dict(line[k], False))
            else:
                values[i].append(line[k])
    # looping through data

    return {k:v for k,v in zip(keys, values)}
# end of list_to_dict


def combine_template_data(template:dict,
                          data:dict,
                          simple:bool= True)->dict:
    """ Combine a template with the values from the data.
        If a field in the template has no type defined,
        its value gets overwritten from the one in the data.
        If there is a type, then a 'value' subfield gets
        added or gets overwritten.

        All structure of value is preserved.

        parameters:
        template:   a dict, possibly default template merged
        data:       a dict of keys filled out with values
        simple:     if we have subsets in subsets, keep their
                    record list structure in value instead of
                    diving into them recursively

        return:
        the merged dict
    """

    if not template or not data:
        return {}

    res = template.copy()
    for k,v in template.items():
        if isinstance(v, dict)\
                and 'type' in v\
                and k in data:
            # how do we combine subsets?
            if v['type'] == 'subset':
                # in the template, a form defines
                # the details of the subset
                # In the data, here comes a list
                # of values, which themselves are
                # dicts.
                # The content there can be further subsets...
                if 'form' in v:
                    if simple:
                        res[k]['value'] = list_to_dict(data[k],
                                                       simple= simple)
                        # keep form for future use (if needed)
                    else:
                        print('calling subset on', k)
                        res[k]['value'] = combine_template_data(
                            v['form'],
                            list_to_dict(data[k], simple= simple)
                            )
                        # we folded the form into the
                        # values out, so drop it
                        res[k].pop('form')
                else:
                    print('form not in template subset!')
                    print(v)
            else:
                res[k]['value'] = data[k]

        elif k in data:
            # if v is not a dict, then it is
            # a template with fix value, written in data
            res[k] = data[k]
        else:
            # a template element that was not transferred,
            # there must be a reason...
            # probably documentation of the template
            # drop it
            res.pop(k)

    return res
# end of combine template data

def find_in_dict(data:dict, search:str:'file')->list:
    """ make a deep search into the dict and find every field with a key file_id,
        return all values as a simple list.
        This code is practically identical to that in dictDigUtils.

        parameters:
        data:       dict, typically a record
        search:    a key under which e.g. files are listed

        return:
        a list of hits merged together
    """
    if not isinstance(data, dict):
        raise ValueError('inproper input type')

    res = []
    for k,v in data.items():
        if ((isinstance(k, str) and search in k)
            or k == search):
            res.append(v)

        elif isinstance(v, dict):
            newres = find_in_dict(search, v)

            if newres:
                res += newres

        elif isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    newres = dict_search_in_key(search, i)
                    if newres:
                        res += newres
    # end of for in data
    return res
# end of find_in_dict
