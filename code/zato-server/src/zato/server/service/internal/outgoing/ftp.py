# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingFTP
from zato.common.odb.query import out_ftp, out_ftp_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

_get_output_required = 'id', 'name', 'is_active', 'host', 'port'
_get_output_optional = 'user', 'acct', 'timeout', Boolean('dircache'), 'default_directory'

# ################################################################################################################################
# ################################################################################################################################

class _FTPService(AdminService):
    """ A common class for various FTP-related services.
    """
    def notify_worker_threads(self, params, action=OUTGOING.FTP_CREATE_EDIT.value):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.publish(params)

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns an FTP connection by its ID.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ftp_get_by_id_request'
        response_elem = None
        input_required = 'cluster_id', 'id'
        output_required = _get_output_required
        output_optional = _get_output_optional
        output_repeated = False

    def get_data(self, session):
        return out_ftp(session, self.server.cluster_id, self.request.input.id)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing FTP connections.
    """
    _filter_by = OutgoingFTP.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_ftp_get_list_request'
        response_elem = 'zato_outgoing_ftp_get_list_response'
        input_required = 'cluster_id'
        output_required = _get_output_required
        output_optional = _get_output_optional
        output_repeated = True

    def get_data(self, session):
        return elems_with_opaque(self._search(out_ftp_list, session, self.request.input.cluster_id, False))

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class Create(_FTPService):
    """ Creates a new outgoing FTP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ftp_create_request'
        response_elem = 'zato_outgoing_ftp_create_response'
        input_required = 'cluster_id', 'name', 'is_active', 'host', 'port', Boolean('dircache')
        input_optional = 'user', 'acct', 'timeout', 'default_directory'
        output_required = 'id', 'name'

    def handle(self):

        input = self.request.input

        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingFTP.id).\
                filter(OutgoingFTP.cluster_id==input.cluster_id).\
                filter(OutgoingFTP.name==input.name).\
                first()

            if existing_one:
                raise Exception('Outgoing FTP connection `{}` already exists'.format(input.name))

            try:
                item = OutgoingFTP()
                item.name = input.name
                item.is_active = input.is_active
                item.cluster_id = input.cluster_id
                item.dircache = input.dircache
                item.host = input.host
                item.port = input.port
                item.user = input.user
                item.acct = input.acct
                item.timeout = input.timeout or None

                # Opaque attributes
                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Outgoing FTP connection could not be created, e:`{}`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
# ################################################################################################################################

class Edit(_FTPService):
    """ Updates an outgoing FTP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ftp_edit_request'
        response_elem = 'zato_outgoing_ftp_edit_response'
        input_required = 'id', 'cluster_id', 'name', 'is_active', 'host', 'port', Boolean('dircache')
        input_optional = 'user', 'acct', 'timeout', 'default_directory'
        output_required = 'id', 'name'

    def handle(self):

        input = self.request.input

        with closing(self.odb.session()) as session:
            existing_one = session.query(OutgoingFTP.id).\
                filter(OutgoingFTP.cluster_id==input.cluster_id).\
                filter(OutgoingFTP.name==input.name).\
                filter(OutgoingFTP.id!=input.id).\
                first()

            if existing_one:
                raise Exception('Outgoing FTP connection `{}` already exists'.format(input.name))

            try:
                item = session.query(OutgoingFTP).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.cluster_id = input.cluster_id
                item.dircache = input.dircache
                item.host = input.host
                item.port = input.port
                item.user = input.user
                item.acct = input.acct
                item.timeout = input.timeout or None

                input.password = item.password
                input.old_name = old_name

                # Opaque attributes
                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Could not update the outgoing FTP connection, e:`{}`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
# ################################################################################################################################

class Delete(_FTPService):
    """ Deletes an outgoing FTP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_ftp_delete_request'
        response_elem = 'zato_outgoing_ftp_delete_response'
        input_required = 'id'

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(OutgoingFTP).\
                    filter(OutgoingFTP.id==self.request.input.id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()

                self.notify_worker_threads({'name':old_name}, OUTGOING.FTP_DELETE.value)

            except Exception:
                session.rollback()
                self.logger.error('Could not delete the outgoing FTP connection, e:`{}`', format_exc())

                raise

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing FTP connection.
    """
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_outgoing_ftp_change_password_request'
        response_elem = 'zato_outgoing_ftp_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        self._handle(OutgoingFTP, _auth, OUTGOING.FTP_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################
