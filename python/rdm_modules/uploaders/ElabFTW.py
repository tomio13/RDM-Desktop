#!/usr/bin/env python
""" upload a dict record to ElabFTW
    Author:     tomio
    License;    MIT
    Date:       2023-03-30
    Warranty:   None
"""
import json
import os
from requests import request
from tkinter.messagebox import showerror
import time


def upload_record(
        title:str,
        record:dict,
        server:str,
        token:str,
        verify= True)->dict:
    """ Send a record to a server, and return
        a confirmation with information about the upload

        parameters:
        title:  a title of the experiment
        record: a dict containing form information and values
        server: the https link to the server
        token:  the security token to be used
        verify: check certificate validity (False for self signed certificates)

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
                   # 'action': 'lock'
                   }

    # create the experiment
    rep = request('POST',
                   f'{server}/api/v2/experiments',
                   headers= header,
                  json= empty_content,
                  verify= verify)

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
                      verify= verify)

        if rep.ok and rep.status_code == 200:
            print(f'{k} is added')
        else:
            showerror('error', rep.text)
            return None

    # MISSING STILL: handle file links as attachments...
    # for fn in filelist...

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
        The body is in HTML (markdown needs an editing step
        in Elab to be compiled), containing all multiline entries.

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
    filelist = []

    j = 1
    for k,v in record.items():
        # exception:
        if k == 'doc':
            k = 'description'

        if isinstance(v, dict):
            # Elab has description fields where we have 'doc':
            if 'doc' in v:
                v['description'] = v.pop('doc')

            if 'type' in v:
                if v['type'] == 'subset':
                    # Subsets are translated to a plain dict
                    if 'value' in v:
                        val = v.pop('value')
                        # table = f'<h1>{k}</h1>\n<table>\n'
                        # MD:
                        table = f'# {k}\n'

                        # with lists for values (simple= True)
                        if isinstance(val, dict):
                            table_keys = list(val.keys())
                            table_vals = list(zip(* val.values()))

                        #
                        # ElabFTW cannot handle this one
                        # we can try to make it to some kind of table
                        elif isinstance(val, list)\
                            and val\
                            and isinstance(val[0], dict):

                            table_keys = list(val[0].keys())
                            table_vals = [list(i.values()) for i in val]


                        # common table writing:
                        table = f'{table}\n|' + \
                                '|'.join(table_keys)+ '|\n'

                        head_line = '|' + '|'.join(['-'*len(i) for i in table_keys]) + '|'
                        table = f'{table}{head_line}\n'

                        # add values row-by-row
                        for i in table_vals:
                            #table = f'{table}\n<tr><td>'
                            #table = f'{table}' + '</td><td>'.join([str(ii) for ii in i])
                            #table = f'{table}</td></tr>\n'
                            table = f'{table}|' + '|'.join([str(ii) for ii in i]) + '|\n'

                        # body = f'{body}{table}</table>\n\n'
                        body = f'{body}{table}\n\n'

                    #else:
                        # no value, then it is not so nice to use...
                        # ElabFTW cannot handle this one, so keep it in the
                        # general metadata
                    #   meta[k] = v

                    # drop the rest into the metadata
                    meta[k] = v

                elif v['type'] == 'multiline' and 'value' in v:
                    # body = f'{body}<h1>{k}</h1>\n<p>{v["value"]}\n\n'
                    body = f'{body}# {k}\n{v["value"]}\n\n'

                elif v['type'] == 'text' and 'value' in v\
                        and '\n' in v['value']:
                    # body = f'{body}<h1>{k}</h1>\n<p>{v["value"]}\n\n'
                    body = f'{body}# {k}\n{v["value"]}\n\n'

                else:
                    # all other cases go to the extra_fiels -> form
                    if v['type'] in ['list', 'numericlist']:
                        v['type'] = 'text'
                        if 'value' in v:
                            if v['value'] is None:
                                v['value'] = ''
                            else:
                                v['value'] = ', '.join(str(v['value']))
                        else:
                            v['value'] = ''

                    # a file list is something we can use for adding
                    # attachments in the future
                    elif v['type'] == 'file':
                        if 'value' in v:
                            fl = [i.replace('file:', '') for i in v]
                            filelist += fl
                            v['value'] = ', '.join(fl)
                        else:
                            v['value'] = ''


                    elif v['type'] == 'date':
                        if 'value' in v and v['value']:
                            # cut the date time to date only (yyyy-mm-dd HH:MM -> yyyy-mm-dd)
                            v['value'] = v['value'].split(' ',1)[0]

                    else:
                        if 'value' not in v or v['value'] is None:
                            v['value'] = ''

                    v['position'] = j
                    extra[k] = v
                    j += 1
            else:
                # we have no type in v, but v is a dict...
                # best is to keep it as a non form meta element
                meta[k] = v

        else:
            # it is not a dict, some key/value pair,
            # so we keep it around... if it is a multiline text,
            # add to the body
            if isinstance(v, str) and '\n' in v:
                body= f'{body}\n\n<h1>{k}</h1>\n<p>{v}'
            else:
                meta[k] = v

    if extra:
        # meta['extra_fields'] = json.dumps(extra)
        meta['extra_fields'] = extra

    if meta:
        meta = json.dumps(meta)
    else:
        meta = None

    # clean up filelist
    filelist = [i for i in  filelist if os.path.isfile(i)]

    return (body, meta, filelist)
# end body_meta_from_record
