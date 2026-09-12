# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connection selects of the Alerts tab's pick lines - the email connection an alert is sent through and the LLM
# connection that explains it.

# Django
from django.urls import reverse
from django.utils.html import format_html

# Zato
from zato.admin.web.forms import INITIAL_CHOICES
from zato.common.alerting.object_config import Email_Conn_Type_IMAP, Email_Conn_Type_SMTP, encode_email_connection
from zato.common.api import EMAIL, GENERIC
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist
    any_ = any_
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The class alerts-tab.css sizes the selects under
Pick_Select_Class = 'alerts-tab-select'

# What the live form updates poll knows the connections of the pick lines as
Live_Type_Email_Connection = 'alert_email_connection'
Live_Type_LLM_Connection = 'alert_llm_connection'

# What a select with nothing to list says instead, each `{}` being the create link of one kind
Email_Empty_Text = 'No email connections found. Click to create an {} or a {} one.'
LLM_Empty_Text = 'No LLM connections found. Click to {}.'

Create_Link_Target = '_blank'

# Between the kind and the name of a connection where a select lists more than one kind
Kind_Label_Separator = '/'

# ################################################################################################################################
# ################################################################################################################################

def _get_email_connection_names(request:'any_', kind:'anydict') -> 'strlist':
    """ The names of the email connections of one kind, an IMAP one only when it is Microsoft 365.
    """
    out:'strlist' = []

    payload = {'cluster_id': request.zato.cluster_id}
    response = request.zato.client.invoke(kind['service'], payload)

    for item in response:

        if kind['kind'] == Email_Conn_Type_IMAP:
            if item.server_type != EMAIL.IMAP.ServerType.Microsoft365:
                continue

        out.append(item.name)

    return out

# ################################################################################################################################

def _get_llm_connection_names(request:'any_', kind:'anydict') -> 'strlist':
    """ The names of every LLM connection there is.
    """
    out:'strlist' = []

    payload = {
        'cluster_id': request.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
        'paginate': False,
    }

    response = request.zato.client.invoke(kind['service'], payload)

    for item in response:
        out.append(item.name)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The kinds of connection the email select lists, in the order they are shown
email_kinds:'anylist' = [
    {'kind': Email_Conn_Type_SMTP, 'label': 'SMTP', 'link_text': 'SMTP', 'url_name': 'email-smtp',
        'service': 'zato.email.smtp.get-list', 'list_names': _get_email_connection_names},
    {'kind': Email_Conn_Type_IMAP, 'label': 'Microsoft 365', 'link_text': 'Microsoft 365', 'url_name': 'email-imap',
        'service': 'zato.email.imap.get-list', 'list_names': _get_email_connection_names},
]

llm_kinds:'anylist' = [
    {'kind': 'llm', 'label': 'LLM', 'link_text': 'create one', 'url_name': 'out-llm',
        'service': 'zato.generic.connection.get-list', 'list_names': _get_llm_connection_names},
]

# The kinds and the encoding of each type the live form updates poll knows
live_types:'anydict' = {
    Live_Type_Email_Connection: {'kinds': email_kinds, 'encode_kind': True},
    Live_Type_LLM_Connection: {'kinds': llm_kinds, 'encode_kind': False},
}

# ################################################################################################################################
# ################################################################################################################################

def encode_pick_value(encode_kind:'bool', kind:'str', name:'str') -> 'str':
    """ The value one entry of a select carries.
    """
    if encode_kind:
        out = encode_email_connection(kind, name)
    else:
        out = name

    return out

# ################################################################################################################################

def pick_label(encode_kind:'bool', kind:'anydict', name:'str') -> 'str':
    """ What one connection reads as in a select.
    """
    if encode_kind:
        out = kind['label'] + Kind_Label_Separator + name
    else:
        out = name

    return out

# ################################################################################################################################

def get_options(request:'any_', kinds:'anylist', encode_kind:'bool') -> 'anylist':
    """ The connections of the given kinds, each as its value and its label.
    """
    out:'anylist' = []

    for kind in kinds:
        names = kind['list_names'](request, kind)

        for name in names:
            value = encode_pick_value(encode_kind, kind['kind'], name)
            label = pick_label(encode_kind, kind, name)
            out.append((value, label))

    return out

# ################################################################################################################################

def get_pick_choices(request:'any_', line:'anydict') -> 'anylist':
    """ The choices of a pick line's select.
    """
    out:'anylist' = [INITIAL_CHOICES]

    options = get_options(request, line['kinds'], line['encode_kind'])
    out.extend(options)

    return out

# ################################################################################################################################

def get_live_items(request:'any_', live_type:'str') -> 'dictlist':
    """ The connections of one live type as the live form updates poll lists them.
    """
    out:'dictlist' = []
    config = live_types[live_type]

    for value, label in get_options(request, config['kinds'], config['encode_kind']):
        out.append({'id': value, 'name': label})

    return out

# ################################################################################################################################

def get_create_url(kind:'anydict') -> 'str':
    """ The kind's own page with its create form open.
    """
    url = reverse(kind['url_name'])
    out = f'{url}?cluster={default_cluster_id}&create=1'

    return out

# ################################################################################################################################

def get_empty_html(line:'anydict') -> 'any_':
    """ The sentence a pick line's select is swapped for when there is nothing to list.
    """
    links:'anylist' = []

    for kind in line['kinds']:
        url = get_create_url(kind)
        link = format_html('<a href="{}" target="{}">{}</a>', url, Create_Link_Target, kind['link_text'])
        links.append(link)

    out = format_html(line['empty_text'], *links)
    return out

# ################################################################################################################################
# ################################################################################################################################
