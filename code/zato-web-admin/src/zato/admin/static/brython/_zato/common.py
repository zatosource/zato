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

row_prefix = 'dyn_form_row_id_'

# ################################################################################################################################

class DynFormHandler(object):
    """ Dynamically adds or remove entries from forms depending on values changed in source SELECT.
    """
    def __init__(self, dyn_form_default=None):
        self.current = dyn_form_default or window['zato_dyn_form_default']
        self.elem_name = window['zato_dyn_form_elem_name']
        self.create_source_select = doc['id_{}'.format(self.elem_name)]
        self.switch_to_select_data_target = window['zato_select_data_target']
        self.switch_to_select_data_target_items = window['zato_select_data_target_items']
        self.jquery = window.jQuery
        self.rows = {}
        self.all_rows = set()

        self.needs_edit = not window['zato_dyn_form_skip_edit']

        if self.needs_edit:
            self.edit_source_select = doc['id_edit-{}'.format(self.elem_name)]

    def run(self):

        # Bind events
        self.create_source_select.bind('change', self.on_create_changed)

        if self.needs_edit:
            self.edit_source_select.bind('change', self.on_edit_changed)

        # Get input that should have been already prepared in HTML
        self.rows = window['zato_dyn_form_rows'].to_dict()

        # Build a unique set of all row IDs that we can possibly manipulate
        for values in self.rows.values():
            for value in values:
                self.all_rows.add(value)

        # Remove any old data
        self.clear()

        # Populate initial forms
        self.switch_to(self.current, '')

        if self.needs_edit:
            self.switch_to(self.current, 'edit-')

# ################################################################################################################################

    def clear(self):
        """ Clear out any older values possibly left in forms.
        """
        self.remove('', self.get_all_rows(''))

        if self.needs_edit:
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
        return self._get_rows(form_prefix, self.all_rows)

# ################################################################################################################################

    def get_rows(self, form_prefix, source_elem):
        return self._get_rows(form_prefix, self.rows[source_elem])

# ################################################################################################################################

    def switch_to(self, switch_to, form_prefix):
        """ Switches to new rows - removes current ones and adds new.
        """
        to_remove = self.get_rows(form_prefix, self.current)
        to_add = self.get_rows(form_prefix, switch_to)

        self.remove(form_prefix, to_remove)
        self.add(form_prefix, to_add)

        self.current = switch_to

        if self.switch_to_select_data_target:
            target_select = doc['id_{}{}'.format(form_prefix, self.switch_to_select_data_target)]
            target_select.clear()

            items = self.switch_to_select_data_target_items[self.switch_to_select_data_target]
            items = items[self.current]

            # Initially, nothing is selected
            option = doc.createElement('option');
            option.value = ''
            option.text = '------'
            target_select.appendChild(option)

            for item in items:
                option = doc.createElement('option');
                option.value = item.id
                option.text = item.name
                target_select.appendChild(option)

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
                try:
                    field = doc[field_id]
                except KeyError:
                    # This is not necessarily an error - it may happen if a single row contains multiple elements.
                    pass
                else:
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

def zato_run_dyn_form_handler(dyn_form_default=None):
    handler = DynFormHandler(dyn_form_default)
    handler.run()

window.zato_run_dyn_form_handler = zato_run_dyn_form_handler

# ################################################################################################################################
