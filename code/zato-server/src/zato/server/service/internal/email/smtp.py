# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.broker_message import EMAIL
from zato.common.odb.model import SMTP
from zato.common.odb.query import email_smtp_list
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'email_smtp'
model = SMTP
label = 'an SMTP connection'
broker_message = EMAIL
broker_message_prefix = 'SMTP_'
list_func = email_smtp_list

def instance_hook(service, input, instance, attrs):
    instance.username = input.username or '' # So it's not stored as None/NULL

class GetList(AdminService):
    __metaclass__ = GetListMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta
