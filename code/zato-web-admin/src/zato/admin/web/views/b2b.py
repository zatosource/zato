# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id
from zato.x12.control import ControlNumberStore, Kind_Group, Kind_Interchange, Kind_Transaction_Set, Max_Control_Number, \
     get_control_db_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What each control number kind is called on the page
_kind_label = {
    Kind_Interchange: 'Interchange',
    Kind_Group: 'Group',
    Kind_Transaction_Set: 'Transaction set',
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def control_numbers(req:'any_') -> 'TemplateResponse':
    """ The X12 control numbers page - one row per sender-receiver pair
    and control number level.
    """

    # The rows the page shows
    rows:'anylist' = []

    # The store lives in a file shared with the servers - the listing is read directly from it.
    store = ControlNumberStore(get_control_db_path())

    try:
        for item in store.get_sequences():
            rows.append({
                'sender': item.sender,
                'receiver': item.receiver,
                'kind': item.kind,
                'kind_label': _kind_label[item.kind],
                'next_number': item.next_number,
                'last_used': item.last_used,
                'last_used_time': item.last_used_time,
            })
    finally:
        store.close()

    return_data = {
        'cluster_id': default_cluster_id,
        'rows': rows,
        'zato_clusters': True,
        'zato_template_name': 'zato/b2b-control-numbers.html',
    }

    return TemplateResponse(req, 'zato/b2b-control-numbers.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def set_next(req:'any_') -> 'JsonResponse':
    """ Repositions one sequence so its next number is the one given on input.
    """
    body = json.loads(req.body)

    sender = body['sender']
    receiver = body['receiver']
    kind = body['kind']
    next_number = body['next_number']

    # The number arrives from a text input, so it is validated at this boundary.
    try:
        next_number = int(next_number)
    except ValueError:
        return JsonResponse({'is_ok': False, 'message': 'Next number must be an integer'}, status=400)

    if next_number < 1 or next_number > Max_Control_Number:
        message = 'Next number must be between 1 and {}'.format(Max_Control_Number)
        return JsonResponse({'is_ok': False, 'message': message}, status=400)

    store = ControlNumberStore(get_control_db_path())

    try:
        store.set_next(sender, receiver, kind, next_number)
    finally:
        store.close()

    return JsonResponse({'is_ok': True, 'message': 'Next number saved', 'next_number': next_number})

# ################################################################################################################################
# ################################################################################################################################
