# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_services
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_default = HL7.Default

_dedup_ttl_unit_choices = [
    ('minutes', 'Minutes'),
    ('hours',   'Hours'),
    ('days',    'Days'),
]

_encoding_choices = [
    ('utf-8',        'UTF-8'),
    ('iso-8859-1',   'ISO-8859-1'),
    ('windows-1252', 'Windows-1252'),
    ('us-ascii',     'US-ASCII'),
]

_max_msg_size_unit_choices = [
    ('kb', 'kB'),
    ('mb', 'MB'),
]

# What a checkbox that starts out ticked renders with.
_checked_attrs = {'checked':'checked'}

# ################################################################################################################################

def _new_checkbox_field(is_checked:'bool'=False) -> 'any_':
    """ Returns a checkbox, ticked by default or not.
    """
    if is_checked:
        attrs = dict(_checked_attrs)
    else:
        attrs = {}

    widget = forms.CheckboxInput(attrs=attrs)

    out = forms.BooleanField(required=False, widget=widget)
    return out

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = _new_checkbox_field(is_checked=True)
    should_parse_on_input = _new_checkbox_field(is_checked=True)

    should_validate = _new_checkbox_field()
    should_return_errors = _new_checkbox_field()
    should_log_messages = _new_checkbox_field()
    is_audit_log_active = _new_checkbox_field(is_checked=True)

    # A channel hands each message to a service, to its destinations, or to both, so this
    # is not required on its own - the page checks that at least one of the two is there.
    service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))

    max_msg_size = forms.CharField(initial=_default.max_msg_size_value, widget=forms.TextInput(attrs={'style':'width:8%'}))
    max_msg_size_unit = forms.ChoiceField(
        choices=_max_msg_size_unit_choices,
        initial=_default.max_msg_size_unit,
        widget=forms.Select(attrs={'style':'width:60px'}),
    )
    recv_timeout = forms.CharField(initial=_default.recv_timeout, widget=forms.TextInput(attrs={'style':'width:8%'}))
    idle_timeout = forms.CharField(initial=_default.idle_timeout, widget=forms.TextInput(attrs={'style':'width:8%'}))
    start_seq = forms.CharField(initial=_default.start_seq, widget=forms.TextInput(attrs={'style':'width:15%'}))
    end_seq = forms.CharField(initial=_default.end_seq, widget=forms.TextInput(attrs={'style':'width:15%'}))

    keepalive_idle = forms.CharField(
        initial=_default.keepalive_idle, widget=forms.TextInput(attrs={'style':'width:8%'}))
    keepalive_interval = forms.CharField(
        initial=_default.keepalive_interval, widget=forms.TextInput(attrs={'style':'width:8%'}))
    keepalive_probe_count = forms.CharField(
        initial=_default.keepalive_probe_count, widget=forms.TextInput(attrs={'style':'width:8%'}))

    # Who the channel accepts a message from - the definition names the client certificate
    # the sender's connection has to have been made with, and the networks its address may be in
    security_id = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    allowed_networks = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Routing fields
    msh3_sending_app        = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh4_sending_facility   = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh5_receiving_app      = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh6_receiving_facility = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh9_message_type       = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:30%'}))
    msh9_trigger_event      = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:30%'}))
    msh11_processing_id     = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:15%'}))
    msh12_version_id        = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:15%'}))
    is_default              = _new_checkbox_field()

    # Dedup
    dedup_ttl_value = forms.CharField(
        initial=_default.dedup_ttl_value, required=False,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )
    dedup_ttl_unit = forms.ChoiceField(
        required=False,
        choices=_dedup_ttl_unit_choices,
        initial=_default.dedup_ttl_unit,
        widget=forms.Select(attrs={'style':'width:15%'}),
    )

    # Default character encoding (when MSH-18 is missing or toggle is off)
    default_character_encoding = forms.ChoiceField(
        required=False,
        choices=_encoding_choices,
        initial=_default.data_encoding,
        widget=forms.Select(attrs={'style':'width:20%'}),
    )

    # Message tolerance toggles (MLLP preprocessing layer)
    normalize_line_endings        = _new_checkbox_field(is_checked=True)
    force_standard_delimiters     = _new_checkbox_field(is_checked=True)
    restore_truncated_msh         = _new_checkbox_field(is_checked=True)
    split_concatenated_messages   = _new_checkbox_field(is_checked=True)
    use_msh18_encoding            = _new_checkbox_field(is_checked=True)

    # Parser tolerance toggles (Rust ER7 content-level fixups)
    normalize_obx2_value_type          = _new_checkbox_field(is_checked=True)
    replace_invalid_obx2_value_type    = _new_checkbox_field(is_checked=True)
    normalize_invalid_escape_sequences = _new_checkbox_field(is_checked=True)
    normalize_obx8_abnormal_flags      = _new_checkbox_field(is_checked=True)
    normalize_quadruple_quoted_empty   = _new_checkbox_field(is_checked=True)
    allow_short_encoding_characters    = _new_checkbox_field(is_checked=True)
    fix_off_by_one_field_index         = _new_checkbox_field()

    # Destinations - serialized by JS to hidden JSON fields
    destinations  = forms.CharField(required=False, widget=forms.HiddenInput())
    respond_from  = forms.CharField(required=False, widget=forms.HiddenInput())
    delivery_mode = forms.CharField(required=False, widget=forms.HiddenInput())

    # REST bridge
    use_rest         = _new_checkbox_field()
    rest_only        = _new_checkbox_field()
    rest_url_path    = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    rest_security_id = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(
        self,
        prefix:'any_'=None,
        post_data:'any_'=None,
        req:'any_'=None,
        security_list:'any_'=None,
        mtls_security_list:'any_'=None,
        ) -> 'None':

        super(CreateForm, self).__init__(post_data, prefix=prefix)

        if security_list is None:
            security_list = []

        if mtls_security_list is None:
            mtls_security_list = []

        add_services(self, req)
        add_security_select(self, security_list, field_name='rest_security_id')
        add_security_select(self, mtls_security_list, field_name='security_id')

# ################################################################################################################################
# ################################################################################################################################

class RowEditForm(forms.Form):
    """ What the channel list edits one row's target through, the wizard's panels reading form fields.
    """
    service = forms.ChoiceField(required=False, widget=forms.Select())

    destinations  = forms.CharField(required=False, widget=forms.HiddenInput())
    respond_from  = forms.CharField(required=False, widget=forms.HiddenInput())
    delivery_mode = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, req:'any_', prefix:'str') -> 'None':
        super(RowEditForm, self).__init__(prefix=prefix)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = _new_checkbox_field()

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        # An edit form opens with the values the object already has.
        for field in self.fields.values():
            if 'checked' in field.widget.attrs:
                del field.widget.attrs['checked']

# ################################################################################################################################
# ################################################################################################################################
