
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from random import randint
from traceback import format_exc
from uuid import uuid4

# SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.odb.model import SSOAttr as AttrModel, SSOUser as UserModel
from zato.server.service import Service
from zato.sso import const, SearchCtx, SignupCtx, status_code, ValidationError

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_utcnow = datetime.utcnow
_default_expiration = datetime(year=9999, month=12, day=31)

AttrModelTable = AttrModel.__table__
AttrModelTableDelete = AttrModelTable.delete
AttrModelTableUpdate = AttrModelTable.update

# ################################################################################################################################

class Attr(object):
    """ A base class for both user and session SSO attributes.
    """
    def __init__(self, odb_session_func, encrypt_func, user_id, ust=None):
        self.odb_session_func = odb_session_func
        self.encrypt_func = encrypt_func
        self.user_id = user_id
        self.ust = ust
        self.is_session_attr = bool(ust)

# ################################################################################################################################

    def _create(self, session, name, value, expiration=None, is_encrypted=False, _utcnow=_utcnow):
        """ A low-level implementation of self.create which expects an SQL session on input.
        """
        now = _utcnow()

        attr_model = AttrModel()
        attr_model.user_id = self.user_id
        attr_model.ust = self.ust
        attr_model.is_session_attr = self.is_session_attr
        attr_model.name = name
        attr_model.value = self.encrypt_func(value.encode('utf8')) if is_encrypted else value
        attr_model.is_encrypted = is_encrypted
        attr_model.creation_time = now
        attr_model.last_modified = now

        # Expiration is optional
        attr_model.expiration_time = now + timedelta(seconds=expiration) if expiration else _default_expiration

        session.add(attr_model)
        session.commit()

# ################################################################################################################################

    def create(self, name, value, expiration=None, is_encrypted=False):
        """ Creates a new named attribute, raising an exception if it already exists.
        """
        with closing(self.odb_session_func()) as session:
            try:
                return self._create(session, name, value, expiration, is_encrypted)
            except IntegrityError:
                logger.warn(format_exc())
                raise ValidationError(status_code.attr.already_exists)

# ################################################################################################################################

    def set(self, name, value, expiration=None, is_encrypted=False):
        """ Set value of a named attribute, creating it if it does not already exist.
        """
        with closing(self.odb_session_func()) as session:

            # Check if the attribute exists ..
            if self._exists(session, name):

                # .. it does, so we need to set its new value.
                self._update(session, name, value, expiration, is_encrypted)

            # .. does not exist, so we need to create it
            else:
                self._create(session, name, value, expiration, is_encrypted)

# ################################################################################################################################

    def _update(self, session, name, value, expiration=None, is_encrypted=False, needs_commit=True, _utcnow=_utcnow):
        """ A low-level implementation of self.set which expects an SQL session on input.
        """
        values = {
            'value': self.encrypt_func(value.encode('utf8')) if is_encrypted else value,
            'last_modified': _utcnow(),
        }
        if expiration:
            values['expiration_time'] = now + timedelta(seconds=expiration)

        out = session.execute(
            AttrModelTableUpdate().\
            values(values).\
            where(and_(
                AttrModelTable.c.user_id==self.user_id,
                AttrModelTable.c.ust==self.ust,
                AttrModelTable.c.name==name,
        )))

        if needs_commit:
            session.commit()

# ################################################################################################################################

    def update(self, name, value, expiration=None, is_encrypted=False):
        """ Updates an existing attribute, raising an exception if it does not already exist.
        """
        with closing(self.odb_session_func()) as session:
            return self._update(session, name, value, expiration, is_encrypted)

# ################################################################################################################################

    def get(self, name, details=False, decrypt=True):
        """ Returns a named attribute.
        """

# ################################################################################################################################

    def list(self, details=False, decrypt=True):
        """ Returns a list of attributes.
        """

# ################################################################################################################################

    def _exists(self, session, data):
        """ A low-level implementation of self.exists which expects an SQL session on input.
        """
        data = [data] if isinstance(data, basestring) else data
        out = dict.fromkeys(data, False)

        result = session.query(AttrModel.name).\
            filter(AttrModel.name.in_(data)).\
            all()

        for item in result:
            out[item.name] = True

        if len(data) == 1:
            return out[data[0]]
        else:
            return out

# ################################################################################################################################

    def exists(self, data):
        """ Returns a boolean flag to indicate if input attribute(s) exist(s) or not.
        """
        with closing(self.odb_session_func()) as session:
            return self._exists(session, data)

# ################################################################################################################################

class MyService(Service):
    def handle(self):

        # Current user's data
        username = 'admin1'
        password = '*****'
        current_app = 'CRM'
        remote_addr = '127.0.0.1'
        user_agent = 'Firefox 139.0'

        # Log in current user
        session = self.sso.user.login(self.cid, username, password, current_app, remote_addr, user_agent)

        user = self.sso.user.get_user_by_id(self.cid, session.user_id, session.ust, current_app, remote_addr)

        user.attr = Attr(self.sso.user.odb_session_func, self.sso.user.encrypt_func, user.user_id)

        #user.attr.create('name', 'value')
        #exists = user.attr.exists(['zxc', 'name'])

        user.attr.set('zzz3', 'vvv')

        '''
        user.attr.set('name', 'value')

        # Get an attribute
        value = user.attr.get('name')

        # Delete an attribute
        user.attr.delete('name')

        # Alternatively, if user object is needed only for one operations,
        # that object's ID can be provided explicitly - this is more efficient
        # because one SQL query less is needed

        # Create an attribute
        self.sso.user.attr.set('name', 'value', user_id=user_id)

        # Get an attribute
        value = self.sso.user.attr.get('name', user_id=user_id)

        # Delete an attribute
        self.sso.user.attr.delete('name', user_id=user_id)
        '''

# ################################################################################################################################
