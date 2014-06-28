# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import Cluster, ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service import Int
from zato.server.service.internal import AdminService
from zato.server.service.meta import AdminServiceMeta, GetListMeta

logger = getLogger(__name__)

class CreateEditMeta(AdminServiceMeta):
    is_create = False
    output_required = ('id', 'name')

    def __init__(cls, name, bases, attrs):
        attrs = bunchify(attrs)
        cls.SimpleIO = CreateEditMeta.get_sio(attrs)
        cls.handle = CreateEditMeta.handle(attrs)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            input = self.request.input
            verb = 'edit' if attrs.is_edit else 'create'

            with closing(self.odb.session()) as session:
                try:
                    cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                    # Let's see if we already have an instance of that name before committing
                    # any stuff to the database.

                    existing_one = session.query(attrs.model).\
                        filter(Cluster.id==input.cluster_id).\
                        filter(attrs.model.name==input.name)

                    if attrs.is_edit:
                        existing_one = existing_one.filter(attrs.model.id!=input.id)

                    existing_one = existing_one.first()

                    if existing_one and not attrs.is_edit:
                        raise Exception('{} [{}] already exists on this cluster'.format(
                            attrs.label[0].upper() + attrs.label[1:], input.name))

                    if attrs.is_edit:
                        instance = session.query(attrs.model).filter_by(id=input.id).one()
                    else:
                        instance = attrs.model()

                    instance.fromdict(input, allow_pk=True)

                    session.add(instance)
                    session.commit()

                except Exception, e:
                    msg = 'Could not {} a namespace, e:`%s`'.format(verb)
                    self.logger.error(msg, format_exc(e))
                    session.rollback()
                    raise
                else:
                    action = getattr(attrs.broker_message, attrs.broker_message_prefix + verb.upper())
                    input.action = action
                    self.broker_client.publish(input)

                    self.response.payload.id = instance.id
                    self.response.payload.name = instance.name

        return handle_impl

class BaseDelete(type):
    pass

class GetList(AdminService):
    __metaclass__ = GetListMeta
    elem = 'search_es'
    output_required = ElasticSearch
    get_data_func = search_es_list

class Create(AdminService):
    __metaclass__ = CreateEditMeta
    is_create_edit = True
    is_edit = False
    elem = 'search_es'
    model = ElasticSearch
    input_required = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Edit(AdminService):
    __metaclass__ = CreateEditMeta
    is_create_edit = True
    is_edit = True
    elem = 'search_es'
    model = ElasticSearch
    input_required = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Delete(object):
    model = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'
