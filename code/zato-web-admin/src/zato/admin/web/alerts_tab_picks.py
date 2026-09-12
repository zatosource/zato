# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connection selects of the Alerts tab's pick lines - the email connection an alert is sent
# through and the LLM connection that explains it. Each select opens with the dashboard's own first
# option, the one meaning no connection, and lists every connection there is flat, under a label
# naming its kind where a line has more than one kind of connection. A select with nothing to list
# is swapped for a sentence with the links that open the pages where a connection is created, and
# the select comes back as soon as one exists - the live form updates poll keeps both in step.

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

# The connection selects of the pick lines open with the dashboard's own first option, the one meaning
# no connection, and list every connection there is flat, under a label naming its kind where a line has
# more than one kind of connection. A select with nothing to list is swapped for a sentence with the links
# that open the pages where a connection is created, and the select comes back as soon as one exists.
# The class the selects wear is what alerts-tab.css sizes them under.
Pick_Select_Class = 'alerts-tab-select'

# What the live form updates poll knows the connections of the pick lines as
Live_Type_Email_Connection = 'alert_email_connection'
Live_Type_LLM_Connection = 'alert_llm_connection'

# What a select with nothing to list says instead - each `{}` is the create link of one kind, in the order of the kinds
Email_Empty_Text = 'No email connections found. Click to create an {} or a {} one.'
LLM_Empty_Text = 'No LLM connections found. Click to {}.'

# Where a create link leads - the kind's own page with its create form open, in a new tab
Create_Link_Target = '_blank'

# What the label of a connection reads as where the select lists more than one kind - the kind, a slash, the name
Kind_Label_Separator = '/'

# ################################################################################################################################
# ################################################################################################################################

def _get_email_connection_names(req:'any_', kind:'anydict') -> 'strlist':
    """ The names of the email connections of one kind - every SMTP connection there is,
    and among the IMAP ones only those of the Microsoft 365 kind, the only ones that can send.
    """
    out:'strlist' = []

    response = req.zato.client.invoke(kind['service'], {'cluster_id': req.zato.cluster_id})

    for item in response:

        if kind['kind'] == Email_Conn_Type_IMAP:
            if item.server_type != EMAIL.IMAP.ServerType.Microsoft365:
                continue

        out.append(item.name)

    return out

# ################################################################################################################################

def _get_llm_connection_names(req:'any_', kind:'anydict') -> 'strlist':
    """ The names of every LLM connection there is.
    """
    out:'strlist' = []

    request = {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
        'paginate': False,
    }

    response = req.zato.client.invoke(kind['service'], request)

    for item in response:
        out.append(item.name)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The kinds of connection the email select lists, in the order they are shown, each with the service
# listing its connections and the function reading that listing, the label its options carry and the
# text of its create link in the empty sentence - an email value names both the kind and the connection,
# e.g. smtp:ops.smtp, so encode_kind is on for the whole list.
email_kinds = [
    {'kind': Email_Conn_Type_SMTP, 'label': 'SMTP', 'link_text': 'SMTP', 'url_name': 'email-smtp',
        'service': 'zato.email.smtp.get-list', 'list_func': _get_email_connection_names},
    {'kind': Email_Conn_Type_IMAP, 'label': 'Microsoft 365', 'link_text': 'Microsoft 365', 'url_name': 'email-imap',
        'service': 'zato.email.imap.get-list', 'list_func': _get_email_connection_names},
]

# The one kind of the LLM select - every LLM connection there is, listed by the generic connection service
llm_kinds = [
    {'kind': 'llm', 'label': 'LLM', 'link_text': 'create one', 'url_name': 'out-llm',
        'service': 'zato.generic.connection.get-list', 'list_func': _get_llm_connection_names},
]

# The kinds and the encoding of each type the live form updates poll knows
live_types = {
    Live_Type_Email_Connection: {'kinds': email_kinds, 'encode_kind': True},
    Live_Type_LLM_Connection: {'kinds': llm_kinds, 'encode_kind': False},
}

# ################################################################################################################################
# ################################################################################################################################

def encode_pick_value(encode_kind:'bool', kind:'str', name:'str') -> 'str':
    """ The value one entry of a select carries - the kind and the name where the kind is encoded, the name alone otherwise.
    """
    if encode_kind:
        out = encode_email_connection(kind, name)
    else:
        out = name

    return out

# ################################################################################################################################

def pick_label(encode_kind:'bool', kind:'anydict', name:'str') -> 'str':
    """ What one connection reads as in a select - the kind before the name where the kind is encoded, the name alone otherwise.
    """
    if encode_kind:
        out = kind['label'] + Kind_Label_Separator + name
    else:
        out = name

    return out

# ################################################################################################################################

def get_options(req:'any_', kinds:'anylist', encode_kind:'bool') -> 'anylist':
    """ The connections of the given kinds, flat and in the order of the kinds - each as its value and its label.
    """
    out:'anylist' = []

    for kind in kinds:
        names = kind['list_func'](req, kind)

        for name in names:
            out.append((encode_pick_value(encode_kind, kind['kind'], name), pick_label(encode_kind, kind, name)))

    return out

# ################################################################################################################################

def get_pick_choices(req:'any_', line:'anydict') -> 'anylist':
    """ The choices of a pick line's select - the dashboard's own first option, then every connection there is.
    """
    out:'anylist' = [INITIAL_CHOICES]
    out.extend(get_options(req, line['kinds'], line['encode_kind']))

    return out

# ################################################################################################################################

def get_live_items(req:'any_', live_type:'str') -> 'dictlist':
    """ The connections of one live type as the live form updates poll lists them - the id of an item is the value
    its option carries and the name is the label it reads as, so the poll adds options that read the way the page's do.
    """
    out:'dictlist' = []
    config = live_types[live_type]

    for value, label in get_options(req, config['kinds'], config['encode_kind']):
        out.append({'id': value, 'name': label})

    return out

# ################################################################################################################################

def get_create_url(kind:'anydict') -> 'str':
    """ Where the create link of one kind of connection leads - the kind's own page with its create form open.
    """
    url = reverse(kind['url_name'])
    out = f'{url}?cluster={default_cluster_id}&create=1'

    return out

# ################################################################################################################################

def get_empty_html(line:'anydict') -> 'str':
    """ What a pick line's select is swapped for when there is nothing to list - the sentence
    with one create link per kind of connection.
    """
    links:'anylist' = []

    for kind in line['kinds']:
        links.append(format_html('<a href="{}" target="{}">{}</a>', get_create_url(kind), Create_Link_Target, kind['link_text']))

    out = format_html(line['empty_text'], *links)
    return out

# ################################################################################################################################
# ################################################################################################################################
