#!/usr/bin/env python
""" upload a dict record to ElabFTW
    Author:     tomio
    License;    MIT
    Date:       2023-03-30
    Warranty:   None
"""
import json
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
                    'tags':['RDM Desktop', 'uploaded']
                     }

    # Create parts to be uploaded:
    # here we have to take apart the record...
    body, meta = body_meta_from_record(record)
    upload_dict = {'title': title,
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
        The body is in markdown, containing all multiline entries.

        parameters:
        record      a dict with the complete record (merged with its template)

        return:
        a tuple of body content and meta data content as strings
    """

    if not record:
        return ('','')

    # ElabFTW can have anything in its JSON part, but extra_fields build
    # a form system
    body = ''
    meta = {}
    extra = {}

    j = 1
    for k,v in record.items():
        if isinstance(v, dict):
            # Elab has description fields where we have 'doc':
            if 'doc' in v:
                v['description'] = v.pop('doc')

            if 'type' in v:
                if v['type'] == 'subset':
                    meta[k] = v

                elif v['type'] == 'multiline' and 'value' in v:

                    body = f'{body}\n\n# {k}\n{v["value"]}'

                elif v['type'] == 'text' and 'value' in v\
                        and '\n' in v['value']:

                    body = f'{body}\n\n# {k}\n{v["value"]}'

                else:
                    if v['type'] in ['list', 'numericlist', 'file']:
                        v['type'] = 'text'
                        if 'value' in v:
                            if v['value'] is None:
                                v['value'] = ''
                            else:
                                v['value'] = ', '.join(str(v['value']))
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
            # it is not a dict, some key/value pair, like a subset
            # Elab cannot handle such a thing right now
            if isinstance(v, str) and '\n' in v:
                body= f'{body}\n\n#{k}\n{v}'
            else:
                meta[k] = v

    if extra:
        # meta['extra_fields'] = json.dumps(extra)
        meta['extra_fields'] = extra

    if meta:
        meta = json.dumps(meta)
    else:
        meta = None

    return (body, meta)
# end body_meta_from_record
