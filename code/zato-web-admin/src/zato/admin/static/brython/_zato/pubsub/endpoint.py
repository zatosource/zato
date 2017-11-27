# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Brython
from browser import document as doc, window

# ################################################################################################################################

row_prefix = 'endpoint_row_id_'

# ################################################################################################################################

rows = {
    'amqp': [],
    'files': [],
    'ftp': [],
    'imap': [],
    'rest': ['security_id', 'out_rest_id', 'out_rest_callback'],
    'service': ['service_id'],
    'sms-twilio': [],
    'smtp': [],
    'soap': ['security_id', 'out_soap_id'],
    'sql': [],
    'websockets': ['ws_channel_id'],
}

# Build a unique set of all row IDs that we manipulate in main class
all_rows = set()
for values in rows.values():
    for value in values:
        all_rows.add(value)

all_rows = list(all_rows)

# ################################################################################################################################

class EndpointFormHandler(object):
    """ Dynamically adds or remove entries from endpoint forms depending on chosen endpoint_type.
    """
    def __init__(self, default='websockets', elem_name='endpoint_type'):
        self.current = default
        self.create_source = doc['id_{}'.format(elem_name)]
        self.edit_source = doc['id_edit-{}'.format(elem_name)]

    def run(self):
        # Bind events
        self.create_source.bind('change', self.on_create_changed)
        self.edit_source.bind('change', self.on_edit_changed)

        # Remove any old data
        self.clear()

        # Populate initial forms
        self.switch_to(self.current, '')
        self.switch_to(self.current, 'edit-')

# ################################################################################################################################

    def clear(self):
        """ Clear out any older values possibly left in forms.
        """
        self.remove('', self.get_all_rows(''))
        self.remove('edit-', self.get_all_rows('edit-'))

# ################################################################################################################################

    def on_create_changed(self, e):
        """ Runs when a SELECT value changes in create form.
        """
        return self.on_changed(e)

# ################################################################################################################################

    def on_edit_changed(self, e):
        """ Runs when a SELECT value changes in edit form.
        """
        return self.on_changed(e, 'edit-')

# ################################################################################################################################

    def on_changed(self, e, form_prefix=''):
        """ A callback that switches values according to currently selected value.
        """
        self.switch_to(e.srcElement.value, form_prefix)

# ################################################################################################################################

    def _get_rows(self, form_prefix, source):
        return ['{}{}{}'.format(form_prefix, row_prefix, elem) for elem in source]

# ################################################################################################################################

    def get_all_rows(self, form_prefix):
        return self._get_rows(form_prefix, all_rows)

# ################################################################################################################################

    def get_rows(self, form_prefix, source_elem):
        return self._get_rows(form_prefix, rows[source_elem])

# ################################################################################################################################

    def switch_to(self, switch_to, form_prefix):
        """ Switches to new rows - removes current ones and adds new.
        """
        to_remove = self.get_rows(form_prefix, self.current)
        to_add = self.get_rows(form_prefix, switch_to)

        self.remove(form_prefix, to_remove)
        self.add(form_prefix, to_add)

        self.current = switch_to

# ################################################################################################################################

    def set_visibility(self, form_prefix, rows, style):
        """ Sets new visibility for table rows and elements they contain, either showing or hiding them.
        """
        for row_id in rows:
            row = doc[row_id]
            row.set_style({'display':style})

            # Above, we changed display style for the table row but we still need to reset each individual field.
            if not form_prefix:
                field_id = 'id_{}'.format(row_id.replace(row_prefix, '', 1))
                field = doc[field_id]
                field.set_value('')

# ################################################################################################################################

    def remove(self, form_prefix, rows):
        """ Removes from display all input elems and resets their value.
        """
        self.set_visibility(form_prefix, rows, 'none')

# ################################################################################################################################

    def add(self, form_prefix, rows):
        """ Makes input elements visibile.
        """
        self.set_visibility(form_prefix, rows, 'table-row')

# ################################################################################################################################

handler = EndpointFormHandler()
handler.run()

# Register our code with JavaScript
window.zato_endpoint_form_handler = handler

# ################################################################################################################################
