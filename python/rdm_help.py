#!/usr/bin/env python
""" new window with a text widget to display help

    Author:     tomio
    License;    MIT
    Date:       2023-03-04
    Warranty:   None
"""
import tkinter as tk
from tkinter import ttk


class rdmHelp():
    """ a multiline text widget to show help
        Use <ESC> (<Escape>) to close
    """

    def __init__(self,
                 parent:tk.Misc = None,
                 form:dict = {'none':'no information is available'}
                 )-> None:
        """ A Tk text area widget to show the keys and doc strings
            of a template.

            parameters:
            parent:     the parent widget
            form:       the form dict, from which
                        doc-strings are extracted
        """

        # no form, no content, just stop pushing
        if not form:
            return
        self.form = form

        # we make a new window:
        if parent is None:
            window = tk.Tk()

        else:
            # this can be a frame or similar, we embed into
            self.parent = parent
            window = tk.Toplevel(self.parent)

        #window.geometry('650x600')
        window.minsize(600,300)
        window.geometry('')
        # leave the size automatic
        window.grid()
        # to make the frame at 0,0 stick and scale with the window:
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        # bring the window to top as a start
        window.lift()
        # but do not force it to the top
        # stacking order ==> always on top
        # window.attributes('-topmost', 1)

        window.title('Template information')
        window.bind('<Escape>',
                         lambda event: window.destroy())


        # the whole window is a text widget:
        # for width we include place for a TAB.
        self.text = tk.Text(window,
                            width= 85,
                            height= 15,
                            wrap='word')
        self.text.grid(column=0, row=0, sticky='news')

        # with scroll-bars:
        scroll_vertical= tk.Scrollbar(window,
                                      bg= 'grey',
                                      orient= 'vertical',
                                      command= self.text.yview,
                                      takefocus= True
                                      )
        scroll_vertical.grid(row= 0,
                                   column= 1,
                                   sticky= 'ns')
        self.text.config(yscrollcommand= scroll_vertical.set)

        scroll_horizontal= tk.Scrollbar(window,
                                        bg= 'grey',
                                        orient= 'horizontal',
                                        command= self.text.xview,
                                        takefocus= True
                                        )
        scroll_horizontal.grid(row= 1,
                                   column= 0,
                                   sticky= 'ew')
        self.text.config(xscrollcommand= scroll_horizontal.set)

        # interpret the dict and fill up the content
        self.add_content()
    # end __init__


    def add_content(self):
        """ extract the content from form and
            add it to the text widget
        """
        text = ''
        for k, v in self.form.items():
            lines = []
            if isinstance(v, dict) and 'doc' in v:
                lines = v['doc'].split('\n')
            elif k == 'doc':
                lines = v.split('\n')

            if lines:
                # instead of TAB, 4 spaces
                lines = ['    '+i for i in lines]
                content = '\n'.join(lines)

                if not text:
                    text = f'{k}:\n{content}'
                else:
                    text = f'{text}\n\n{k}:\n{content}'
        # end for
        if text:
            self.text.insert('0.0', text)
    # end add_content

# end of rdmHelp
