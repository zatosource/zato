# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# SQLAlchemy
from sqlalchemy import select

# Django
from django.http import HttpResponse, HttpResponseNotFound

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.audit_log.columns import _preview_length
from zato.admin.web.views.audit_log.file_transfer_record import render_file_transfer_record
from zato.admin.web.views.audit_log.sources import _source_parse, render_scheduler_record, render_view_record
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.audit_log.body import resolve_body
from zato.common.audit_log.config_audit import record_view_event
from zato.x12.render import render_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# What the log access source calls this application - the server name of every event it writes
_dashboard_server_name = 'dashboard'

# The screen the message bodies and attachments are read from, as the log access source names it
_screen_browser = 'audit-log-browser'

# All the access events this module writes go through this one writer
_access_log = AuditLog(_dashboard_server_name)

# The sources whose parsed view is rendered from the database by event id.
_source_render_by_event_id = {
    AuditSource.Scheduler: render_scheduler_record,
    AuditSource.File_Outgoing: render_file_transfer_record,
}

# ################################################################################################################################

def _record_content_view(req:'any_', event_id:'int', source:'str', object_name:'str') -> 'None':
    """ Records who read the content of one event - a message body or an attachment.
    Access to patient data is itself an audited operation.
    """

    # A view record holds no patient data, so reading one is not itself a recordable
    # view - without this, browsing the log access records writes views of views without end
    if source == AuditSource.Config:
        return

    _ = record_view_event(
        _access_log,
        actor=req.user.username,
        viewed_event_id=event_id,
        screen=_screen_browser,
        viewed_source=source,
        viewed_object_name=object_name,
    )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def details(req:'any_') -> 'HttpResponse':
    """ Returns the payload of one audit event, along with the human-readable rendering of the
    document it carries, if it carries one at all. A caller that only shows the top of a message -
    a line of a flow opened for a look at it - asks for a preview instead, and gets the first few
    thousand characters with no parsed view, because a fragment of a message parses into nothing.
    Either way the full length is reported, so the reader is told how much of it is on the screen.
    """
    body = json.loads(req.body)
    event_id = body['id']

    # Which of the event's message bodies is wanted - what was sent, what came back
    # or what the other side said when it failed. With none named, the newest one answers,
    # which is what the message overlay asks for.
    kind = body['kind']

    # Whether the whole message is wanted or only the top of it
    is_preview = body['preview']

    data = ''
    source = ''
    object_name = ''
    event_time_iso = ''

    # Read the full payload of this one event from the shared audit log database.
    details_query = select(
        event_table.c.source, event_table.c.object_name, event_table.c.data,
        event_table.c.event_time_iso).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:

        result = connection.execute(details_query)
        row = result.fetchone()

        if row:
            source = row[0]
            object_name = row[1]
            data = row[2]
            event_time_iso = row[3]

    # Whoever is reading this message is recorded - the event exists, so there is content to see
    if row:
        _record_content_view(req, event_id, source, object_name)

    # A named body is one the data column never holds, so it always comes out of the body store ..
    if kind:
        data = ''

    # .. and a payload stored outside the data column resolves through the body registry -
    # sources with their own body stores answer for themselves, everything else
    # reads the shared body table.
    if not data:
        resolved = resolve_body(engine, source, event_id, kind)
        if resolved is not None:
            data = resolved

    # However much of the message is being shown, how long it is in full is what says so
    total_len = len(data)

    # A preview is the top of the message and nothing else ..
    if is_preview:
        data = data[:_preview_length]
        parsed = ''

    # .. and the whole message additionally gets its parsed view, from the source's own renderer
    # with the EDI renderer as the shared default - an empty result means no parsed tab at all.
    # A log access view record resolves against the database - who viewed what and when -
    # so it renders here, where the engine is at hand, rather than through _source_parse.
    # The sources in _source_render_by_event_id resolve against the database the same way.
    else:
        if source == AuditSource.Config:
            parsed = render_view_record(engine, data, event_time_iso)
        elif event_renderer := _source_render_by_event_id.get(source):
            parsed = event_renderer(engine, event_id)
        elif renderer := _source_parse.get(source):
            parsed = renderer(data)
        else:
            parsed = render_document(data)

    response_json = json.dumps({'data': data, 'parsed': parsed, 'total_len': total_len})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def attachments(req:'any_') -> 'HttpResponse':
    """ Returns the attachments of one audit event as JSON - the metadata of each of them,
    never the bytes, which is what the detail pane's attachment strip is drawn out of.
    """
    body = json.loads(req.body)
    event_id = body['id']

    engine = get_audit_engine()
    items = list_attachments(engine, event_id)

    response_json = json.dumps({'attachments': items})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

# In a downloaded filename, control characters become spaces
# and quotes and backslashes become underscores.
_filename_char_map = {}

for _code_point in range(0, 32):
    _filename_char_map[_code_point] = 32

_filename_char_map[127] = 32

for _code_point in range(128, 160):
    _filename_char_map[_code_point] = 32

_filename_char_map[ord('"')] = ord('_')
_filename_char_map[ord('\\')] = ord('_')

# ################################################################################################################################

@method_allowed('GET')
def attachment_download(req:'any_') -> 'HttpResponse':
    """ Streams one attachment's decoded bytes back under the filename and content type
    it was stored with, or a 404 when there is no such attachment.
    """
    # Query parameters are always strings while the body-row id column is numeric
    attachment_id = int(req.GET['id'])

    engine = get_audit_engine()
    attachment = get_attachment(engine, attachment_id)

    if attachment is None:
        out = HttpResponseNotFound(b'No such attachment')
        return out

    # Whoever is downloading this file is recorded, against the event the file arrived with
    owner_query = select(
        event_table.c.source, event_table.c.object_name).where(event_table.c.id == attachment['event_id'])

    with engine.connect() as connection:
        owner_row = connection.execute(owner_query).fetchone()

    source, object_name = owner_row
    _record_content_view(req, attachment['event_id'], source, object_name)

    # The stored filename goes through the character map first
    filename = attachment['filename'].translate(_filename_char_map)

    out = HttpResponse(attachment['content'], content_type=attachment['content_type'])
    out['Content-Disposition'] = f'attachment; filename="{filename}"'

    return out

# ################################################################################################################################
# ################################################################################################################################
