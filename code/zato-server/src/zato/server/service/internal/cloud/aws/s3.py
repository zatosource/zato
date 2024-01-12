# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import CLOUD
from zato.common.odb.model import AWSS3
from zato.common.odb.query import cloud_aws_s3_list
from zato.server.service import Bool, SIOElem, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    """ Returns a list of AWS S3 connections.
    """
    _filter_by = AWSS3.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_cloud_aws_s3_get_list_request'
        response_elem = 'zato_cloud_aws_s3_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'pool_size', 'address', Int('debug_level'), Bool('suppr_cons_slashes'),
            'content_type', 'security_id', Bool('encrypt_at_rest'), 'storage_class')
        output_optional = ('metadata_', 'bucket')

    def get_data(self, session):
        return self._search(cloud_aws_s3_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new AWS S3 connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_cloud_aws_s3_create_request'
        response_elem = 'zato_cloud_aws_s3_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'pool_size', 'address', Int('debug_level'),
            Bool('suppr_cons_slashes'), 'content_type', 'security_id', Bool('encrypt_at_rest'), 'storage_class')
        input_optional = ('metadata_', 'bucket')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(AWSS3.id).\
                filter(AWSS3.cluster_id==input.cluster_id).\
                filter(AWSS3.name==input.name).\
                first()

            if existing_one:
                raise Exception('An AWS S3 connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = AWSS3()
                for name in self.SimpleIO.input_required + self.SimpleIO.input_optional:
                    if isinstance(name, SIOElem):
                        name = name.name
                    setattr(item, name, self.request.input.get(name))

                session.add(item)
                session.commit()

                input.action = CLOUD.AWS_S3_CREATE_EDIT.value
                input.id = item.id
                input.username = item.security.username
                input.password = item.security.password

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                msg = 'Could not create an AWS S3 connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates an AWS S3 connection.
    """
    class SimpleIO(Create.SimpleIO):
        request_elem = 'zato_cloud_aws_s3_edit_request'
        response_elem = 'zato_cloud_aws_s3_edit_response'
        input_required = ('id',) + Create.SimpleIO.input_required

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            existing_one = session.query(AWSS3.id).\
                filter(AWSS3.cluster_id==input.cluster_id).\
                filter(AWSS3.name==input.name).\
                filter(AWSS3.id!=input.id).\
                first()

            if existing_one:
                raise Exception('An AWS S3 connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = session.query(AWSS3).filter_by(id=input.id).one()
                old_name = item.name

                for name in self.SimpleIO.input_required + self.SimpleIO.input_optional:
                    if isinstance(name, SIOElem):
                        name = name.name
                    setattr(item, name, self.request.input.get(name))

                session.add(item)
                session.commit()

                input.action = CLOUD.AWS_S3_CREATE_EDIT.value
                input.old_name = old_name
                input.id = item.id
                input.username = item.security.username
                input.password = item.security.password

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                msg = 'Could not update the AWS S3 connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an AWS S3 connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_cloud_aws_s3_delete_request'
        response_elem = 'zato_cloud_aws_s3_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(AWSS3).\
                    filter(AWSS3.id==self.request.input.id).\
                    one()

                session.delete(item)
                session.commit()

                msg = {'action': CLOUD.AWS_S3_DELETE.value, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                msg = 'Could not delete the AWS S3 connection, e:`{}`'.format(format_exc())
                self.logger.error(msg)

                raise
