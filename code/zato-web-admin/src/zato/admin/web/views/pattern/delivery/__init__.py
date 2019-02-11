# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import loads
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.admin.web import from_utc_to_user, from_user_to_utc
from zato.admin.web.forms.pattern.delivery.definition import InstanceListForm
from zato.admin.web.views import CreateEdit, Index as _Index, get_js_dt_format, method_allowed
from zato.common import DELIVERY_STATE
from zato.common.model import DeliveryItem
from zato.common.util.json_ import dumps

logger = logging.getLogger(__name__)

# ##############################################################################

def _drop_utc(item, req):
    item.creation_time = from_utc_to_user(item.creation_time_utc + '+00:00', req.zato.user_profile)
    item.last_used = from_utc_to_user(item.last_used_utc + '+00:00', req.zato.user_profile)

    return item

# ##############################################################################

class Details(_Index):
    url_name = 'pattern-delivery-details'
    template = 'zato/pattern/delivery/details.html'
    service_name = 'zato.pattern.delivery.get-details'
    output_class = DeliveryItem

    class SimpleIO(_Index.SimpleIO):
        input_required = ('task_id',)
        output_required = ('def_name', 'target_type', 'task_id', 'creation_time_utc', 'last_used_utc',
                    'source_count', 'target_count', 'resubmit_count', 'state', 'retry_repeats', 'check_after', 'retry_seconds')
        output_optional = ('payload', 'args', 'kwargs', 'payload_sha1', 'payload_sha256')
        output_repeated = False

    def _handle_item(self, item):
        self.item = _drop_utc(item, self.req)
        self.item.args = '\n'.join('{}'.format(elem) for elem in loads(self.item.args))
        self.item.kwargs = '\n'.join('{}={}'.format(k, v) for k, v in iteritems(loads(self.item.kwargs)))
        if self.item.payload:
            self.item.payload_len = len(self.item.payload)

    def handle(self):

        out = {}
        service = 'zato.pattern.delivery.get-history-list'
        req = {'task_id': self.input['task_id']}
        response = self.req.zato.client.invoke(service, req)

        if self.item:
            out['has_item'] = True
            out['show_resubmit_button'] = self.item.state in([DELIVERY_STATE.IN_DOUBT, DELIVERY_STATE.CONFIRMED, DELIVERY_STATE.FAILED])
            out['show_update_button'] = not out['show_resubmit_button']
        else:
            out['has_item'] = False

        if response.ok:
            for item in response.data:
                item.entry_time = from_utc_to_user(item.entry_time + '+00:00', self.req.zato.user_profile)
            out['history'] = response.data
        else:
            logger.warn(response.details)

        return out

# ##############################################################################

class _Update(CreateEdit):
    url_name = 'pattern-delivery-resubmit'
    service_name = 'zato.pattern.delivery.resubmit'
    async_invoke = True
    action_verb = None

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('task_id',)
        input_optional = ('payload', 'args', 'kwargs')

    def __call__(self, req, initial_input_dict={}, initial_return_data={}, *args, **kwargs):

        initial_input_dict['payload'] = req.POST.get('payload', None)
        initial_input_dict['args'] = dumps([elem for elem in req.POST.get('args', '').split('\n')])

        initial_input_dict['kwargs'] = {}
        for elem in req.POST.get('kwargs', '').split('\n'):
            k, v = elem.split('=')
            initial_input_dict['kwargs'][k] = v
        initial_input_dict['kwargs'] = dumps(initial_input_dict['kwargs'])

        return super(_Update, self).__call__(req, initial_input_dict, initial_return_data, *args, **kwargs)

    def success_message(self, item):
        return 'Request to {} task [{}] sent successfully, check server logs for details'.format(self.action_verb, self.input['task_id'])

class Resubmit(_Update):
    url_name = 'pattern-delivery-resubmit'
    service_name = 'zato.pattern.delivery.resubmit'
    action_verb = 'resubmit'

class Edit(_Update):
    url_name = 'pattern-delivery-edit'
    service_name = 'zato.pattern.delivery.edit'
    action_verb = 'update'

# ##############################################################################

class Delete(CreateEdit):
    url_name = 'pattern-delivery-delete'
    service_name = 'zato.pattern.delivery.delete'
    async_invoke = True

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('task_id',)

    def success_message(self, item):
        return 'Request to delete task [{}] sent successfully, check server logs for details'.format(self.input['task_id'])

# ##############################################################################

def _update_many(req, cluster_id, service, success_msg, failure_msg):
    """ A common function for either resubmitting or deleting one or more tasks.
    """
    try:
        for task_id in req.POST.values():
            input_dict = {'task_id':task_id}
            response = req.zato.client.invoke_async(service, input_dict)

            if not response.ok:
                raise Exception(response.details)

        return HttpResponse(dumps({'message':success_msg}))

    except Exception:
        msg = '{}, e:`{}`'.format(failure_msg, format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

@method_allowed('POST')
def resubmit_many(req, cluster_id):
    """ Resubmits one or more delivery tasks.
    """
    return _update_many(req, cluster_id, 'zato.pattern.delivery.resubmit',
        'Request sent successfully, check server logs for details', 'Could not resubmit tasks')

@method_allowed('POST')
def delete_many(req, cluster_id):
    """ Resubmits one or more delivery tasks.
    """
    return _update_many(req, cluster_id, 'zato.pattern.delivery.delete',
        'Tasks deleted successfully', 'Could not delete tasks')

# ##############################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pattern-delivery-index'
    template = 'zato/pattern/delivery/index.html'
    service_name = 'zato.pattern.delivery.get-list'
    output_class = DeliveryItem

    class SimpleIO(_Index.SimpleIO):
        input_required = ('def_name',)
        input_optional = ('batch_size', 'current_batch', 'start', 'stop', 'state')
        output_required = ('def_name', 'target_type', 'task_id', 'creation_time_utc', 'last_used_utc',
            'source_count', 'target_count', 'resubmit_count', 'retry_repeats', 'check_after', 'retry_seconds')
        output_repeated = True

    def on_before_append_item(self, item):
        return _drop_utc(item, self.req)

    def on_after_set_input(self):
        for name in('start', 'stop'):
            if self.input.get(name):
                self.input[name] = from_user_to_utc(self.input[name], self.req.zato.user_profile)

    def handle(self):
        out = {'form': InstanceListForm(initial=self.req.GET)}
        out.update(get_js_dt_format(self.req.zato.user_profile))

        service = 'zato.pattern.delivery.get-batch-info'
        req = {key:self.input[key] for key in ('def_name', 'batch_size', 'current_batch', 'start', 'stop', 'state') if self.input.get(key)}
        response = self.req.zato.client.invoke(service, req)

        if response.ok:
            out.update(response.data)
        else:
            logger.warn(response.details)

        return out

# ##############################################################################
