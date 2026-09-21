# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue and DLQ page of one outgoing connection.

# stdlib
import json
import logging
from datetime import timedelta
from http import HTTPStatus
from traceback import format_exc
from urllib.parse import quote

# dateutil
from dateutil.parser import parse as dt_parse

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import method_allowed
from zato.common.api import HTTP_SOAP
from zato.common.content_type import format_content, get_content_type
from zato.common.defaults import default_cluster_id
from zato.common.pubsub.dlq import Header_Moved_Time, Header_Rounds, Key_DLQ
from zato.common.pubsub.outgoing import Key_Data, Key_Headers, Key_Request
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_dlq = HTTP_SOAP.DLQ

_template = 'zato/outgoing/delivery.html'

_default_error_message = 'Error'
_default_page = 1

Kind_Queue = 'queue'
Kind_DLQ   = 'dlq'

Service_Get_List      = 'zato.pubsub.outgoing.get-message-list'
Service_Get_Time_List = 'zato.pubsub.outgoing.get-message-time-list'
Service_Get           = 'zato.pubsub.outgoing.get-message'
Service_Action        = 'zato.pubsub.outgoing.message-action'
Service_Update        = 'zato.pubsub.outgoing.update-message'

# A refreshed cell's id is its tab and its message id, which lets one refresh cover both tabs
Refresh_ID_Separator = ':'
Refresh_Time_Field   = 'time_utc'

Download_Body     = 'body'
Download_Document = 'document'

_body_extensions = {
    'application/json': 'json',
    'application/xml': 'xml',
    'text/xml': 'xml',
    'text/csv': 'csv',
    'text/plain': 'txt',
}
_default_body_extension = 'txt'

# The DLQ rule, as the details window states it
_rule_keep        = 'Keep'
_rule_retry       = 'Retry {}'
_rule_forward     = 'Forward to {} {}'
_rule_discard     = 'Discard {}'
_rule_rounds_used = 'Stays, {} of {} retries used'
_rule_due_now     = 'on the next run'
_rule_due_in      = 'in {}'

_rule_actions = {
    _dlq.Action.Retry: _rule_retry,
    _dlq.Action.Discard: _rule_discard,
}

# Compact duration units
_duration_units = (
    (86400, 'd'),
    (3600, 'h'),
    (60, 'm'),
    (1, 's'),
)
_duration_just_now = '0s'

# ################################################################################################################################
# ################################################################################################################################

def _format_duration(seconds:'int') -> 'str':
    """ A duration as its two largest units.
    """
    if seconds <= 0:
        out = _duration_just_now
        return out

    parts:'anylist' = []
    remainder = seconds

    for unit_seconds, label in _duration_units:
        count, remainder = divmod(remainder, unit_seconds)
        if count:
            parts.append(f'{count}{label}')

    parts = parts[:2]

    out = ' '.join(parts)
    return out

# ################################################################################################################################

def _rule_text(moved_time_iso:'str', rounds:'int', settings:'anydict', now:'any_') -> 'str':
    """ What the DLQ rule will do with one message and when.
    """
    action = settings[_dlq.Field_Action]

    if action == _dlq.Action.Keep:
        out = _rule_keep
        return out

    interval = settings[_dlq.Field_Retry_Interval]
    moved = dt_parse(moved_time_iso)
    due = moved + timedelta(seconds=interval)
    seconds_left = int((due - now).total_seconds())

    if seconds_left > 0:
        due_text = _rule_due_in.format(_format_duration(seconds_left))
    else:
        due_text = _rule_due_now

    if action == _dlq.Action.Retry:
        max_rounds = settings[_dlq.Field_Retries]

        if rounds >= max_rounds:
            out = _rule_rounds_used.format(rounds, max_rounds)
            return out

    if action == _dlq.Action.Forward:
        out = _rule_forward.format(settings[_dlq.Field_Forward_To], due_text)
    else:
        template = _rule_actions[action]
        out = template.format(due_text)

    return out

# ################################################################################################################################

def _enrich_row(row:'stranydict', kind:'str', user_profile:'any_') -> 'stranydict':
    """ Adds to one row what the page shows and the service does not know.
    """
    out = dict(row)

    out['pub_time'] = from_utc_to_user(row['pub_time_iso'], user_profile)

    if kind == Kind_DLQ:
        out['moved_time'] = from_utc_to_user(row['moved_time_iso'], user_profile)

    return out

# ################################################################################################################################

def _page_url(kind:'str', query:'str', page:'int') -> 'str':
    """ The address of one page of one tab's list.
    """
    query_encoded = quote(query, safe='')
    out = f'?cluster={default_cluster_id}&tab={kind}&query={query_encoded}&cur_page={page}'
    return out

# ################################################################################################################################

def _build_meta(data:'anydict', kind:'str', query:'str') -> 'anydict':
    """ The paging of one tab's list.
    """
    cur_page = data['cur_page']
    num_pages = data['num_pages']

    has_prev_page = cur_page > 1
    has_next_page = cur_page < num_pages

    out = {
        'total': data['total'],
        'cur_page': cur_page,
        'num_pages': num_pages,
        'page_size': data['page_size'],
        'has_prev_page': has_prev_page,
        'has_next_page': has_next_page,
        'prev_page_url': _page_url(kind, query, cur_page - 1),
        'next_page_url': _page_url(kind, query, cur_page + 1),
    }

    return out

# ################################################################################################################################

def _load_tab(req:'any_', kind:'str', conn_type:'str', conn_id:'int', query:'str', cur_page:'int') -> 'anydict':
    """ One tab of the page.
    """
    response = req.zato.client.invoke(Service_Get_List, {
        'conn_type': conn_type,
        'conn_id': conn_id,
        'kind': kind,
        'query': query,
        'cur_page': cur_page,
    })

    if not response.ok:
        raise Exception(response.details)

    data = response.data

    items:'anylist' = []

    for row in data['items']:
        items.append(_enrich_row(row, kind, req.zato.user_profile))

    out = {
        'kind': kind,
        'is_dlq': kind == Kind_DLQ,
        'items': items,
        'query': query,
        'meta': _build_meta(data, kind, query),
        'data': data,
    }

    return out

# ################################################################################################################################

def _error_response(message:'str') -> 'HttpResponse':
    """ A JSON error the page's scripts read.
    """
    error_json = json.dumps({'error': message})

    out = HttpResponse(error_json.encode('utf-8'), content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_', conn_type:'str', conn_id:'int') -> 'TemplateResponse':
    """ The queue and the DLQ of an outgoing connection.
    """
    active_tab = req.GET['tab']
    query = req.GET.get('query', '')

    if cur_page := req.GET.get('cur_page'):
        cur_page = int(cur_page)
    else:
        cur_page = _default_page

    # The search and the page apply to the active tab only
    tabs:'anydict' = {}

    for kind in (Kind_Queue, Kind_DLQ):
        if kind == active_tab:
            tabs[kind] = _load_tab(req, kind, conn_type, conn_id, query, cur_page)
        else:
            tabs[kind] = _load_tab(req, kind, conn_type, conn_id, '', _default_page)

    data = tabs[active_tab]['data']
    settings = data['dlq_settings']

    out = TemplateResponse(req, _template, {
        'cluster_id': default_cluster_id,
        'active_tab': active_tab,
        'conn_type': conn_type,
        'conn_id': conn_id,
        'conn_name': data['conn_name'],
        'is_queue_browsable': data['is_queue_browsable'],
        'queue_tab': tabs[Kind_Queue],
        'dlq_tab': tabs[Kind_DLQ],
        'topic_list': data['topic_list'],
        'forward_to': settings[_dlq.Field_Forward_To],
        'keep_header': settings[_dlq.Field_Keep_Header],
        'req': req,
        'zato_clusters': True,
        'zato_template_name': _template,
    })

    return out

# ################################################################################################################################

def _get_message(req:'any_') -> 'stranydict':
    """ One message in full along with its connection's DLQ settings, as the GET parameters name it.
    """
    response = req.zato.client.invoke(Service_Get, {
        'conn_type': req.GET['conn_type'],
        'conn_id': int(req.GET['conn_id']),
        'kind': req.GET['kind'],
        'msg_id': req.GET['msg_id'],
    })

    if not response.ok:
        raise Exception(response.details)

    out = response.data
    return out

# ################################################################################################################################

@method_allowed('GET')
def message(req:'any_') -> 'JsonResponse':
    """ One message for the details window.
    """
    message_data = _get_message(req)
    document = message_data['document']
    request = document[Key_Request]

    data = request[Key_Data]
    content_type = get_content_type(data)

    has_dlq_header = Key_DLQ in document
    rule = ''

    # What the DLQ rule will do with this message is told here rather than in the listing
    if has_dlq_header:
        dlq_header = document[Key_DLQ]
        rule = _rule_text(dlq_header[Header_Moved_Time], dlq_header[Header_Rounds], message_data['dlq_settings'], utcnow())

    out = JsonResponse({
        'document': document,
        'data': format_content(data, content_type),
        'content_type': content_type,
        'has_dlq_header': has_dlq_header,
        'rule': rule,
    })

    return out

# ################################################################################################################################

@method_allowed('GET')
def download(req:'any_') -> 'HttpResponse':
    """ One message as a file, its data alone or the whole document.
    """
    document = _get_message(req)['document']
    msg_id = req.GET['msg_id']
    what = req.GET['what']

    if what == Download_Body:
        request = document[Key_Request]
        data = request[Key_Data]
        content_type = request[Key_Headers]['Content-Type']

        if not (extension := _body_extensions.get(content_type)):
            extension = _default_body_extension

        file_name = f'{msg_id}.{extension}'
        out = HttpResponse(data.encode('utf-8'), content_type=content_type)

    else:
        file_name = f'{msg_id}.json'
        text = json.dumps(document, indent=2)
        out = HttpResponse(text.encode('utf-8'), content_type='application/json')

    out['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return out

# ################################################################################################################################

@method_allowed('POST')
def refresh(req:'any_') -> 'HttpResponse':
    """ When each of the messages shown entered its queue - the time-ago cells of both tabs ask in one request.
    """
    conn_type = req.GET['conn_type']
    conn_id = int(req.GET['conn_id'])

    # The ids arrive as one comma-separated parameter, each one a tab and a message id ..
    if id_list := req.POST.get('id_list'):
        id_list = id_list.split(',')
    else:
        id_list = []

    msg_ids_by_kind:'anydict' = {}

    for item in id_list:
        kind, msg_id = item.split(Refresh_ID_Separator, 1)
        msg_ids_by_kind.setdefault(kind, []).append(msg_id)

    # .. and one call per tab covers all of its messages.
    out:'anydict' = {}

    for kind, msg_id_list in msg_ids_by_kind.items():
        response = req.zato.client.invoke(Service_Get_Time_List, {
            'conn_type': conn_type,
            'conn_id': conn_id,
            'kind': kind,
            'msg_id_list': json.dumps(msg_id_list),
        })

        if not response.ok:
            raise Exception(response.details)

        for msg_id, time_iso in response.data['items'].items():
            out[f'{kind}{Refresh_ID_Separator}{msg_id}'] = {Refresh_Time_Field: time_iso}

    response_json = json.dumps(out)
    return HttpResponse(response_json.encode('utf-8'), content_type='application/json')

# ################################################################################################################################

@method_allowed('POST')
def action(req:'any_') -> 'HttpResponse':
    """ Runs one action on the messages the form names, or on all the messages matching the query.
    """
    try:
        response = req.zato.client.invoke(Service_Action, {
            'conn_type': req.POST['conn_type'],
            'conn_id': int(req.POST['conn_id']),
            'kind': req.POST['kind'],
            'action': req.POST['action'],
            'msg_id_list': req.POST['msg_id_list'],
            'query': req.POST['query'],
            'forward_to': req.POST['forward_to'],
            'keep_header': req.POST['keep_header'] == 'true',
        })

        if response.ok:
            response_json = json.dumps(response.data)
            out = HttpResponse(response_json.encode('utf-8'), content_type='application/json')

        else:
            error_message = response.details
            if not error_message:
                error_message = _default_error_message

            out = _error_response(error_message)

    except Exception: # noqa: BLE001
        logger.error('Delivery action error: %s', format_exc())
        out = _error_response(_default_error_message)

    return out

# ################################################################################################################################

@method_allowed('POST')
def save(req:'any_') -> 'HttpResponse':
    """ Replaces one message's data with what the details window's editor holds.
    """
    body = json.loads(req.body)

    try:
        response = req.zato.client.invoke(Service_Update, {
            'conn_type': body['conn_type'],
            'conn_id': int(body['conn_id']),
            'kind': body['kind'],
            'msg_id': body['msg_id'],
            'data': body['data'],
        })

        if response.ok:
            response_json = json.dumps(response.data)
            out = HttpResponse(response_json.encode('utf-8'), content_type='application/json')

        else:
            error_message = response.details
            if not error_message:
                error_message = _default_error_message

            out = _error_response(error_message)

    except Exception: # noqa: BLE001
        logger.error('Delivery save error: %s', format_exc())
        out = _error_response(_default_error_message)

    return out

# ################################################################################################################################
# ################################################################################################################################
