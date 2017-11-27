# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Brython
from browser import document as doc

# ################################################################################################################################

row_prefix = 'endpoint_row_'

# ################################################################################################################################

rows = {
    'amqp': [],
    'files': [],
    'ftp': [],
    'imap': [],
    'rest': ['security_id'],
    'service': [],
    'sms-twilio': [],
    'smtp': [],
    'soap': [],
    'sql': [],
    'websockets': ['ws_channel_id'],
}
# ################################################################################################################################

class EndpointFormHandler(object):
    """ Dynamically adds or remove entries from endpoint forms depending on chosen endpoint_type.
    """
    def __init__(self, default='websockets', elem_name='endpoint_type'):
        self.current = default
        self.create_source = doc['id_{}'.format(elem_name)]
        self.edit_source = doc['id_edit-{}'.format(elem_name)]

    def run(self):
        self.create_source.bind('change', self.on_create_changed)
        self.edit_source.bind('change', self.on_edit_changed)

        self.switch_to(self.current, '')
        self.switch_to(self.current, 'edit-')

    def on_create_changed(self, e):
        return self.on_changed(e)

    def on_edit_changed(self, e):
        return self.on_changed(e, 'edit-')

    def on_changed(self, e, form_prefix=''):
        self.switch_to(e.srcElement.value)

    def switch_to(self, switch_to, form_prefix):

        to_remove = ['{}{}{}'.format(form_prefix, row_prefix, elem) for elem in rows[self.current]]
        to_add = ['{}{}{}'.format(form_prefix, row_prefix, elem) for elem in rows[switch_to]]

        self.remove(to_remove)
        self.add(to_add)

        self.current = switch_to

    def set_new_display_style(self, elems, style):
        for elem_id in elems:
            elem = doc[elem_id]
            elem.set_style({'display':style})

    def remove(self, elems):
        self.set_new_display_style(elems, 'none')

    def add(self, elems):
        self.set_new_display_style(elems, 'table-row')

# ################################################################################################################################

handler = EndpointFormHandler()
handler.run()

# ################################################################################################################################
