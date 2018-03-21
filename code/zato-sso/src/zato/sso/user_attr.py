
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from json import dumps, loads
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

class AttrEntity(object):
    """ Holds information about a particular attribute.
    """
    __slots__ = ('name', 'value', 'creation_time', 'last_modified', 'expiration_time', 'is_encrypted', '_is_session_attr')

    def __init__(self, name, value, creation_time, last_modified, expiration_time, is_encrypted, _is_session_attr):
        self.name = name
        self.value = value
        self.creation_time = creation_time
        self.last_modified = last_modified
        self.expiration_time = expiration_time
        self.is_encrypted = is_encrypted
        self._is_session_attr = _is_session_attr

# ################################################################################################################################

    def to_dict(self):
        """ Serializes this attribute to a Python dictionary.
        """
        # Note that we do not serialize _is_session_attr - this is internal only
        return {
            'name': self.name,
            'value': self.value,
            'creation_time': self.creation_time,
            'last_modified': self.last_modified,
            'expiration_time': self.expiration_time,
            'is_encrypted': self.is_encrypted,
        }

# ################################################################################################################################

    @staticmethod
    def from_sql(item, needs_decrypt, decrypt_func, serialize_dt):
        """ Builds a new AttrEntity out of an SQL row.
        """
        return AttrEntity(item.name,
            decrypt_func(loads(item.value)) if (needs_decrypt and item.is_encrypted) else loads(item.value),
            item.creation_time.isoformat() if serialize_dt else item.creation_time,
            item.last_modified.isoformat() if serialize_dt else item.last_modified,
            item.expiration_time.isoformat() if serialize_dt else item.expiration_time,
            item.is_encrypted, item.is_session_attr)

# ################################################################################################################################

class Attr(object):
    """ A base class for both user and session SSO attributes.
    """
    def __init__(self, odb_session_func, encrypt_func, decrypt_func, user_id, ust=None):
        self.odb_session_func = odb_session_func
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.user_id = user_id
        self.ust = ust
        self.is_session_attr = bool(ust)

# ################################################################################################################################

    def _create(self, session, name, value, expiration=None, is_encrypted=False, user_id=None, needs_commit=True,
        _utcnow=_utcnow):
        """ A low-level implementation of self.create which expects an SQL session on input.
        """
        now = _utcnow()

        attr_model = AttrModel()
        attr_model.user_id = user_id or self.user_id
        attr_model.ust = self.ust
        attr_model.is_session_attr = self.is_session_attr
        attr_model.name = name
        attr_model.value = dumps(self.encrypt_func(value.encode('utf8')) if is_encrypted else value)
        attr_model.is_encrypted = is_encrypted
        attr_model.creation_time = now
        attr_model.last_modified = now

        # Expiration is optional
        attr_model.expiration_time = now + timedelta(seconds=expiration) if expiration else _default_expiration

        session.add(attr_model)

        if needs_commit:
            session.commit()

# ################################################################################################################################

    def create(self, name, value, expiration=None, is_encrypted=False, user_id=None):
        """ Creates a new named attribute, raising an exception if it already exists.
        """
        with closing(self.odb_session_func()) as session:
            try:
                return self._create(session, name, value, expiration, is_encrypted, user_id)
            except IntegrityError:
                logger.warn(format_exc())
                raise ValidationError(status_code.attr.already_exists)

# ################################################################################################################################

    def _set(self, session, name, value, expiration=None, is_encrypted=False, user_id=None, needs_commit=True):
        """ A low-level implementation of self.set which expects an SQL session on input.
        """
        # Check if the attribute exists ..
        if self._exists(session, name, user_id):

            # .. it does, so we need to set its new value.
            self._update(session, name, value, expiration, is_encrypted, user_id, needs_commit)

        # .. does not exist, so we need to create it
        else:
            self._create(session, name, value, expiration, is_encrypted, user_id, needs_commit)

# ################################################################################################################################

    def set(self, name, value, expiration=None, is_encrypted=False, user_id=None):
        """ Set value of a named attribute, creating it if it does not already exist.
        """
        with closing(self.odb_session_func()) as session:
            self._set(session, name, value, expiration, is_encrypted)

# ################################################################################################################################

    def _update(self, session, name, value=None, expiration=None, is_encrypted=False, user_id=None, needs_commit=True,
        _utcnow=_utcnow):
        """ A low-level implementation of self.update which expects an SQL session on input.
        """
        now = _utcnow()
        values = {
            'last_modified': now
        }

        if value:
            values['value'] = dumps(self.encrypt_func(value.encode('utf8')) if is_encrypted else value)

        if expiration:
            values['expiration_time'] = now + timedelta(seconds=expiration)

        out = session.execute(
            AttrModelTableUpdate().\
            values(values).\
            where(and_(
                AttrModelTable.c.user_id==(user_id or self.user_id),
                AttrModelTable.c.ust==self.ust,
                AttrModelTable.c.name==name,
        )))

        if needs_commit:
            session.commit()

# ################################################################################################################################

    def update(self, name, value, expiration=None, is_encrypted=False, user_id=None):
        """ Updates an existing attribute, raising an exception if it does not already exist.
        """
        with closing(self.odb_session_func()) as session:
            return self._update(session, name, value, expiration, is_encrypted, user_id)

# ################################################################################################################################

    def _get(self, session, data, decrypt, serialize_dt, user_id=None, columns=AttrModel, exists_only=False):
        """ A low-level implementation of self.get which knows how to return one or more named attributes.
        """
        data = [data] if isinstance(data, basestring) else data
        out = dict.fromkeys(data, False)

        result = session.query(columns).\
            filter(AttrModel.user_id==(user_id or self.user_id)).\
            filter(AttrModel.ust==self.ust).\
            filter(AttrModel.name.in_(data)).\
            all()

        for item in result:
            out[item.name] = True if exists_only else AttrEntity.from_sql(item, decrypt, self.decrypt_func, serialize_dt)

        if len(data) == 1:
            return out[data[0]]
        else:
            return out

# ################################################################################################################################

    def get(self, data, decrypt=True, serialize_dt=False, user_id=None):
        """ Returns a named attribute.
        """
        with closing(self.odb_session_func()) as session:
            return self._get(session, data, decrypt, serialize_dt, user_id)

    # Same as .get but a list/tuple/set is given on input instead of a single name
    get_many = get

# ################################################################################################################################

    def to_dict(self, decrypt=True, value_to_dict=False, serialize_dt=False, user_id=None):
        """ Returns a list of all attributes.
        """
        out = {}

        with closing(self.odb_session_func()) as session:
            result = session.query(AttrModel).\
                filter(AttrModel.user_id==(user_id or self.user_id)).\
                filter(AttrModel.ust==self.ust).\
                all()

        for item in result:
            value = AttrEntity.from_sql(item, decrypt, self.decrypt_func, serialize_dt)
            out[item.name] = value.to_dict() if value_to_dict else value

        return out

# ################################################################################################################################

    def _exists(self, session, data, user_id=None):
        """ A low-level implementation of self.exists which expects an SQL session on input.
        """
        return self._get(session, data, False, False, user_id, AttrModel.name, True)

# ################################################################################################################################

    def names(self, user_id=None):
        """ Returns names of all attributes as a list (unsorted).
        """
        with closing(self.odb_session_func()) as session:
            result = session.query(AttrModel.name).\
                filter(AttrModel.user_id==(user_id or self.user_id)).\
                filter(AttrModel.ust==self.ust).\
                all()

        return [item.name for item in result]

# ################################################################################################################################

    def exists(self, data, user_id=None):
        """ Returns a boolean flag to indicate if input attribute(s) exist(s) or not.
        """
        with closing(self.odb_session_func()) as session:
            return self._exists(session, data, user_id)

# ################################################################################################################################

    def delete(self, data, user_id=None):
        """ Deletes one or more names attributes.
        """
        data = [data] if isinstance(data, basestring) else data

        with closing(self.odb_session_func()) as session:
            session.execute(
                AttrModelTableDelete().\
                where(and_(
                    AttrModelTable.c.user_id==(user_id or self.user_id),
                    AttrModelTable.c.ust==self.ust,
                    AttrModelTable.c.name.in_(data),
            )))
            session.commit()

    # One method can handle both calls
    delete_many = delete

# ################################################################################################################################

    def _set_expiry(self, session, name, expiration, user_id=None, needs_commit=True):
        """ A low-level implementation of self.set_expiry which expects an SQL session on input.
        """
        return self._update(session, name, expiration=expiration, user_id=user_id, needs_commit=needs_commit)

# ################################################################################################################################

    def set_expiry(self, name, expiration, user_id=None):
        """ Sets expiration for a named attribute.
        """
        with closing(self.odb_session_func()) as session:
            return self._set_expiry(name, expiration, user_id)

# ################################################################################################################################

    def _call_many(self, func, data, expiration=None, is_encrypted=False, user_id=None):
        """ A reusable method for manipulation of multiple attributes at a time.
        """
        with closing(self.odb_session_func()) as session:
            for item in data:
                func(session, item['name'], item['value'], item.get('expiration', expiration),
                    item.get('is_encrypted', is_encrypted), item.get('user_id', user_id), needs_commit=False)

            # Commit now everything added to session thus far
            session.commit()

# ################################################################################################################################

    def create_many(self, data, expiration=None, is_encrypted=False, user_id=None):
        """ Creates multiple attributes in one call.
        """
        self._call_many(self._create, data, expiration, is_encrypted, user_id)

# ################################################################################################################################

    def set_many(self, data, expiration=None, is_encrypted=False, user_id=None):
        """ Sets values of multiple attributes in one call.
        """
        self._call_many(self._set, data, expiration, is_encrypted, user_id)

# ################################################################################################################################

    def set_expiry_many():
        pass

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
        user.attr = Attr(self.sso.user.odb_session_func, self.sso.user.encrypt_func, self.sso.user.decrypt_func, user.user_id)

        attrs = [
            {'name':'abc', 'value':'abc-value-11'},
            {'name':'def', 'value':'def-value-22'},
            {'name':'zxc', 'value':'zxc-value-33'},
        ]

        user.attr.set_many(attrs, is_encrypted=False)

        result = user.attr.get(['abc', 'def'])

        print(result)

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
