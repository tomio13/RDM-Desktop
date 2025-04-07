#!/usr/bin/env python
""" upload a dict record to ElabFTW
    Author:     tomio
    License;    MIT
    Date:       2023-03-30
    Warranty:   None
"""
import json
import os
from rdm_modules.rdm_templates import find_in_record
from rdm_modules.rdm_converters import is_record
from requests import (request, ConnectionError)
from tkinter.messagebox import showerror, askyesno
import time
import yaml


def upload_record(
        title:str,
        record:dict,
        record_path:str,
        server:str,
        token:str,
        verify= True)->dict:
    """ Send a record to a server, and return
        a confirmation with information about the upload

        parameters:
        title:          a title of the experiment
        record:         a dict containing form information and values
        record_path:    the path to the folder,
                        so attachments can be found
        server:         the https link to the server
        token:          the security token to be used
        verify:         check certificate validity
                        (False for self signed certificates)

        return:
        a dict containing:
        {'server': link to the server
        'id'     : record ID to reach the result on the server
        'link    : link to the actual record
        'date'   : date and time string (ISO...) of the upload
        }
        None on error
    """
    res = dict()

    if not server:
        showerror('Server error', 'URL not provided!')
        return None

    if not token:
        showerror('Authentication', 'Authentication token is not provided!')
        return None

    header = {'Accept': 'application/json',
              'charset': 'UTF-8',
              'Authorization': token}

    # category or category_id cannot be written in any way
    # other than the -1 below results in a bad request
    empty_content = {
                    'category_id': -1,
                    'tags':['RDM Desktop', 'uploaded'],
                     }

    # Create parts to be uploaded:
    # here we have to take apart the record...
    body, meta, filelist = body_meta_from_record(record)

    upload_dict = {
                   'content_type': 2,
                   'title': title,
                   'body': body,
                   'metadata': meta,
                   'action': 'lock',
                   }

    # create the experiment
    try:
        rep = request('POST',
                   f'{server}/api/v2/experiments',
                   headers= header,
                  json= empty_content,
                  verify= verify,
                  # set a default 10 seconds timout
                  # for connect, 30 for read
                  timeout= (10, 30))

    except ConnectionError:
        showerror('Server error', 'Server connection was refused!')
        return None

    if rep.ok and rep.status_code == 201:
        print('experiment is created')
    else:
        showerror('error', rep.text)
        return None

    link = rep.headers['Location']

    # add title, body and metadata
    for k,v in upload_dict.items():
        rep = request('PATCH',
                      link,
                      headers= header,
                      json= {k:v},
                      verify= verify,
                      timeout= (10, 30))

        if rep.ok and rep.status_code == 200:
            print(f'{k} is added')
        else:
            showerror('error', rep.text)
            return None

    # filelist provides all potential attachments
    # YAML files are supposed to be other records
    # these would not be uploaded
    if filelist:
        filelist = [i for i in  filelist\
                if os.path.isfile(
                    os.path.join(record_path, i)
                    # ) and not i.endswith('.yaml')
                    ) and not is_record(i)
                    ]
        if filelist:
            print('Uploading', len(filelist), 'attachments')
            go_on = True

            if len(filelist) > 10:
                go_on = askyesno("Upload",
                    "Too many attachments found!\n"
                         "Consider uploading a zip file manually\n"
                         "Continue with this upload?")
            if go_on:
                print('Start uploading attachments')
                # not setting Content-Type, let requests handle it
                header = {'Accept': 'application/json',
                          # 'charset': 'UTF-8',
                          'Authorization': token}

                i = 0
                for fn in filelist:
                    with open(os.path.join(record_path, fn), 'rb') as fp:
                        rep = request('POST',
                                      f'{link}/uploads',
                                      files= {'file': fp},
                                      headers= header,
                                      verify= verify)
                        if rep.ok and rep.status_code == 201:
                            print('Uploaded', fn)
                            i += 1
                        else:
                            showerror('error', rep.text)

                print('All together uploaded', i, 'files')

    exp_id = link.rsplit('/',1)[-1]
    res['server'] = server
    res['id'] = exp_id
    res['link'] = link
    res['date'] = time.strftime('%Y-%m-%d %H:%M %z', time.localtime())
    # res['date'] = time.strftime('%Y-%m-%d %H:%M %z',
    #                            time.strptime(rep.headers['Date'],
    #                                          '%a, %d %b %Y %H:%M:%S %Z')
    #                            )
    # header has the time in GMT, but DST is also dropped, so the conversion is problematic
    return(res)
# end of upload_record


def body_meta_from_record(record:dict)->tuple:
    """ Split up a record to meta data and body parts, ready
        to be uploaded to an ElabFTW server.
        The body is in markdown (the uploader has to set the
        content_type to 2) containing all multiline entries.

        parameters:
        record      a dict with the complete record (merged with its template)

        return:
        a tuple of body content and meta data content as strings, and
        a list of files mentioned in the record as potential attachments
    """

    if not record:
        return ('','')

    # ElabFTW can have anything in its JSON part, but extra_fields build
    # a form system
    body = ''
    meta = {}
    extra = {}
    # ElabFTW has now groups to put fields under a single label
    # this works in two steps:
    # one adds a label to the group id list, and an index
    # to every item under that label
    #
    # Here we have labels with a value of group or group_id,
    # every field under them becomes packed into that group like
    # HTML forms do with field sets.
    #
    # this is under key: 'elabftw':{'extra_fields_groups': [{'id': 1, 'name': 'group 1'},
    # {'id': 2, 'name': 'whatever'}, ...]}
    # Since about 5.0 ElabFTW assigns groups even if we did not, it shall be
    # called 'UNKNOWN GROUP' I do not like it
    #
    # Let us make a default: 'general description'

    # since about end of 2024 there are read-only fields possible,
    # which is an excellent way of storing the default, read-only key-value
    # pairs of RDM-desktop

    # key translation between RDM-desktop and ElabFTW
    # these are only the types, there are other factors to consider
    type_translation = {
            'text': 'text',
            'multiline': 'text',
            'numeric': 'number',
            'integer': 'number',
            'list': 'text',
            'numericlist': 'text',
            'select': 'select',
            'multiselect': 'select',
            'checkbox': 'checkbox',
            'url': 'url',
            'date': 'datetime-local',
            'file': 'text'
            }

    groups = []
    group_id = 0
    filelist = find_in_record(record, 'file')

    # handle the record content extracting files and body elements,
    # converting types to those usable in ElabFTW
    # the metadata part is the original record corrected
    j = 0
    keylist = list(record.keys())
    for k in keylist:
        v = record[k]
        # exception:
        #if k == 'doc':
        #    body = f'{body}\n\n # Description \n{v}\n\n'
        #    continue

        # elements to skip:
        if k.lower() in ['doc', 'full record', 'uploaded']:
            record.pop(k)
            continue

        # handle the rest
        if isinstance(v, dict):
            # Elab has description fields where we have 'doc':
            if 'doc' in v:
                v['description'] = v.pop('doc')

            if 'type' in v:
                if v['type'] == 'subset':
                    print('subset:')
                    # Subsets are lists of dicts,
                    #
                    # since we do not have anything similar in ElabFTW,
                    # we convert them to tables in the body
                    #
                    # if extraction was simple, value is a list of dicts too
                    #
                    # but now since numeric values are presented as lists,
                    # we either take their type from form or we have to check
                    # carefully cases of lists of two, one number the other text
                    if 'value' in v:
                        #val = v.pop('value')
                        # keep a copy of the full set in the metadata, so
                        # keep the values there too...
                        val = v['value']
                        # add the table to the body with the key as title
                        table = f'# {k}\n'

                        # with lists for values (simple= True)
                        # this value list contains dicts of key : value pairs,
                        # where the latter value still can be a list...
                        if isinstance(val, list):
                            table_keys = list(val[0].keys())
                            table_vals = []
                            for row in val:
                                # using list(row.values()) is not good for deeper dicts
                                table_row = [i for i in row.values()]
                                table_vals.append(table_row)

                            print('keys:', table_keys)
                            print('got values:', table_vals)
                        else:
                            # this means an invalid structure!
                            print('Unknown structure!')
                            print('we got:', val)
                            continue


                        # common table writing:
                        table = f'{table}\n|' + \
                                '|'.join(table_keys)+ '|\n'

                        head_line = '|' + '|'.join(['-'*len(i) for i in table_keys]) + '|'
                        table = f'{table}{head_line}\n'

                        # add values row-by-row
                        for i in table_vals:
                            # vals is a list of dicts, which may
                            # contain further lists of dicts
                            ii_new = []
                            for ii in i:
                                if isinstance(ii, list):
                                    # try catching numeric + unit parts:
                                    if ii and isinstance(ii[0], dict):
                                        ii_text = yaml.safe_dump(ii)
                                        ii_text = ii_text.replace('\n','<BR>')
                                    else:
                                        if len(ii) == 2 and isinstance(ii[1],str):
                                            ii_text = f'{ii[0]} {ii[1]}'
                                        else:
                                            ii_text = '-'+'<BR>-'.join(ii)
                                        ii_text.replace('file:', '')

                                elif isinstance(ii, dict):
                                    # this should not really come up, but be safe
                                    ii_text = yaml.safe_dump(ii)
                                    ii_text = ii_text.replace('\n','<BR>')

                                else:
                                    ii_text = str(ii)

                                # add the row to the text list:
                                ii_new.append(ii_text)
                            # end running in the rows

                            # write out the resulted table
                            table = f'{table}|' + '|'.join(ii_new) + '|\n'

                        body = f'{body}{table}\n\n'

                    #else:
                        # no value, then it is not so nice to use...
                        # ElabFTW cannot handle this one, so keep it in the
                        # general metadata
                    #   meta[k] = v

                    # stop dropping, because it may break Elab and
                    # the record looks overly complex
                    ## drop the rest into the metadata
                    # meta[k] = v

                # which types need special attention?
                # multiline, list, numericlist, file
                    continue

                # because of continue, we start with an if
                # instead of elif
                if v['type'] == 'multiline' and 'value' in v:
                    # add key as a new header, and value as its content
                    body = f'{body}# {k}\n{v["value"]}\n\n'
                    continue

                if v['type'] in ['list', 'numericlist']:
                    # lists are converted to comma separated text
                    # because ElabFTW cannot handle list variables properly
                    if 'value' in v and v['value'] is not None:
                        # str(v) produces something like '[1, 2, 2.2, ...]'
                        # then join() messes it up. So use the proper conversion
                        v['value'] = ', '.join([str(i) for i in v['value']])

                    # a file list is something we can use for adding
                    # attachments in the future
                elif v['type'] == 'file':
                    if 'value' in v and v['value'] is not None:
                        # for a single filename we have a text,
                        # for multiple ones a list
                        if isinstance(v['value'], list):
                            # file names may start as file:...
                            fl = [i.replace('file:', '') for i in v['value']]
                            v['value'] = ', '.join(fl)

                        else:
                            v['value'] = v['value'].replace('file:', '')
                # if type...
                # all critical types are sorted out
                elif v['type'] == 'multiselect':
                    v['allow_multi_values'] = True

                # clean up value
                if 'value' not in v or v['value'] is None:
                    v['value'] = ''

                # the rest is common to all
                # add field to the extra dict...
            else:
                # we have no type in v, but v is a dict...
                #
                # this is not a standard record! Something different!
                # best is to keep it as a non form meta element
                meta[k] = v
                continue

            # all had a type, this we translate for ElabFWT
            v['type'] = type_translation[v['type']]

        else:
            # it is not a dict, some key/value pair,
            # so we keep it around... if it is a multiline text,
            # add to the body
            if isinstance(v, str):
                # if one left a multiline text as read-only field,
                # we put it to body
                # if single line text or list, put it to a read-only
                # field
                if '\n' in v:
                    #body= f'{body}\n\n<h1>{k}</h1>\n<p>{v}'
                    body= f'{body}# {k}\n{v}\n\n'
                    continue

                elif v.lower() in ['group', 'group_id']:
                    # we have a new group
                    group_id += 1
                    groups.append({'id': group_id, 'name': k})
                    continue

                print('simple string special case', k, ':', v)
                v = {'type': 'text', 'value': v}

            elif isinstance(v, (int, float)):
                v = {'type': 'number', 'value': v}

            else :
                v = {'type': 'text', 'value': str(v)}

            # we can add non standard form elements are read-only information
            v['readonly'] = True

        # end if v type was detected or a readonly one
        # every extra form element needs position or group ID
        # (all others jumped out using continue above)

        v['position'] = j

        # do we have groups?
        if group_id < 1:
            # we have fields without group, so we make
            # a default group:
            group_id += 1
            groups = [{'id':group_id, 'name':'general description'}]

        ################### define the new record in metadata
        # now, in all case, add the group to the record:
        v['group_id'] = group_id

        extra[k] = v

        j += 1


    # end for in the record

    # we are done interpreting the YAML form,
    # do we have extra fields (extra not empty):
    if extra:
        # meta['extra_fields'] = json.dumps(extra)
        meta['extra_fields'] = extra

    if groups:
        meta['elabftw']= {'extra_fields_groups': groups}

    if meta:
        meta = json.dumps(meta)
    else:
        meta = None

    # clean up filelist
    filelist = [i.replace('file:','') for i in filelist if isinstance(i,str)]
    print('found files in record:', filelist)

    return (body, meta, filelist)
# end body_meta_from_record
