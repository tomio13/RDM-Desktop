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

    # allow skipping default
    nk = 'no_default'
    if nk in template \
            and template[nk] == True:
        template.pop(nk)
        return template

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
                # a subset is a list of dicts
                # however, this does not dig into the lower levels
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
                    If false, handle every subset as an own
                    record iteratively

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
                        #res[k]['value'] = list_to_dict(data[k],
                        #                               simple= simple)
                        res[k]['value'] = data[k]
                        # keep form for future use (if needed)
                    else:
                        print('calling subset on', k)
                        # res[k]['value'] = combine_template_data(
                        new_input = combine_template_data(
                            v['form'],
                            list_to_dict(data[k], simple= False),
                            simple= False
                            )
                        res[k].update(new_input)
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


def find_in_record(data:dict, search:str='file')->list:
    """ make a deep search into the dict and find every field with a type
        in variable search, and return all values as a simple list.

        parameters:
        data:       dict, typically a record
        search:    a key under which e.g. files are listed

        return:
        a list of hits merged together
    """
    if not data:
        return []

    if not isinstance(data, dict):
        raise ValueError('inproper input type')

    search = search.lower()

    res = []
    for k,v in data.items():
        if isinstance(v, dict):
            if 'type' in v:
                if v['type'].lower() == search:
                    if 'value' in v:
                        if isinstance(v, list):
                            res += v['value']
                        else:
                            res.append(v['value'])
                    else:
                        print(f'key found without value in {k}')

                elif (v['type'] == 'subset'
                      and 'form' in v
                      and 'value' in v):
                    # now, it gets tricky, because here
                    # form contains types under keys,
                    # value contains a list of dicts
                    klist = find_key_in_record(v['form'], search)

                    if klist:
                        vv = v['value']
                        for kk in klist:
                            # vv = v['value'] is a list of dicts
                            for this_vv in v['value']:
                                if not this_vv[kk] or this_vv[kk] is None:
                                    continue

                                if isinstance(this_vv[kk], list):
                                    res += this_vv[kk]
                                else:
                                    res.append(this_vv[kk])
                        # end collecting results
                    # now, check other subsets
                    klist = find_key_in_record(v['form'], 'subset')
                    if klist:
                        vf = v['form']
                        for kk in klist:
                            for this_vv in v['value']:
                                if not this_vv[kk] or this_vv[kk] is None:
                                    continue

                                this_record = vf[kk]
                                this_record['value']= this_vv[kk]
                                res += find_in_record(this_record, search)
                    # end digging deeper
            # no else
    # end of for in data
    # for debugging, indicate the result:
    print('found', search,':', res)
    return res
# end of find_in_record


def find_key_in_record(data:dict|list, search:str)->list:
    """ Find a key in a dict or a list of dicts, which has type in search.
        Typical run in subsets, form part, thus value may not be present.

        parameter
        data    a dict dicts to search in
        search  a string to search for in types

        return
        a list of keys under which the type was found
    """
    if not data:
        return []

    if isinstance(data, dict):
        data = [data]

    res = []

    for dat in data:
        for k,v in dat.items():
            # now, we have a dict most probably
            if isinstance(v, dict):
                if ('type' in v and
                    v['type'] == search):
                    res.append(k)
    return res
# end of find_key_in_record


def read_record(record:str|None = None,
                default_template:str|None= None,
                template:str|None = None)->dict:
    """ Read a full record based on the file names pointing to
        the record with values (or a full record), and the corresponding
        templates.
        The key point here is to utilize the functions above, and go
        by checking first if record is a full record, if not, then combine
        with its templates, also checking for template version matching
        the version in the record.

        If the record is given, template should be the template dir,
        the template is picked from the record.

        If the record is not found, then the template is returned, to be
        used in a fill-out form (via formBuilder).
        If template is not found either, then an empty dict is returned.

        Full record is defined with a 'full record': true entry and having
        at least one field with a type subfield in it.

        Parameters:
        record:             path to the record or None
        default_template:   path to default template
        template:           path to template or to the template dir

        Return:
        a dict with the full record or an epty dict on failure
    """

    record_dict = {}
    if (record is not None
        and os.path.isfile(record)):
        with open(record, 'rt', encoding='UTF-8') as fp:
            record_dict = yaml.safe_load(fp)
            # if we got somehow a messy file:
            if not record_dict:
                return {}

            type_in_record = any(['type' in v\
                                for k,v in record_dict.items()\
                                if isinstance(v, dict)])

            # the user has a full record that includes
            # its own template:
            if ('full record' in record_dict
                and record_dict['full record']
                and type_in_record):
                return record_dict
    # end loading record

    if (record_dict and 'template' in record_dict
        and os.path.isdir(template)):
        template = os.path.join(template,
                                record_dict['template'])
    # end constructing template path

    # we allow the user to disable the default template
    temp_dict = merge_templates(template,
                                default_template)

    # if no record, then an empty form:
    if not record_dict:
        return temp_dict

    if not record_dict and not temp_dict:
        return {}

    # we have both, then version check first:
    k = 'template version'
    if (k in  temp_dict and k in record_dict
        and  temp_dict[k] != record_dict[k]):
        print('Version mismatch!')
        print('Template has:', temp_dict[k])
        print('Data has:', record_dict[k])
        return {}
    # end if version mismatch

    return combine_template_data(temp_dict,
                                 record_dict,
                                 simple= True)
# end read_record


def save_record(record:dict,
                file_path:str,
                overwrite:bool= True,
                full_record:bool= True)->bool:
    """ dump a dict as a yaml file, with some tiny tuning
        to get a better formatted output.
        Existing files would be overwritten.

        parameters
        record:     the dict to be saved
        file_path:  file to be saved
        overwrite:  Bool, if true, overwrite the file
        full_record: save everything or strip out subdicts

        return:
        True if done, False upon error
    """
    file_path = os.path.abspath(
            os.path.expanduser(file_path)
            )
    if not file_path.endswith('.yaml'):
        file_path = f'{file_path}.yaml'

    fpath = os.path.dirname(file_path)

    if not os.path.isdir(fpath):
        os.makedirs(fpath)

    if (not overwrite
        and os.path.isfile(file_path)):
        print('File exist, will not overwwite!')
        return False

    if not full_record:
        k_list = list(record.keys())
        for k in k_list:
            v = record[k]
            if (isinstance(v, dict)
                and 'type' in v
                and 'value' in v):
                record[k] = v['value']
        # we are saving a reduced record,
        # so if there is a full record in it,
        # that is wrong:
        if 'full record' in record:
            record.pop('full record')

    else:
        # it is full_record, so we add the label:
        # make sure we know there is a full record
        if 'full record' not in record:
            record['full record'] = True
    # end if full_record to be stripped

    with open(file_path,
              'wt',
              encoding='UTF-8') as fp:
        out_txt = yaml.safe_dump(record,
                                 sort_keys= False,
                                 allow_unicode= True,
                                 width= 70,
                                 default_style= None)
        # remove the multiple new lines produced by yaml
        # which breaks multiline entries badly apart
        # strip may not be needed actually
        # fp.write(out_txt.strip().replace('\n\n', '\n'))
        fp.write(out_txt.replace('\n\n', '\n'))
    return True
# end of save_record

