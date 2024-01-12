# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.audit import audit_pii
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import SSOAttr as AttrModel, SSOSession
from zato.sso import status_code, ValidationError

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_utcnow = datetime.utcnow
_default_expiration = datetime(year=9999, month=12, day=31)

AttrModelTable = AttrModel.__table__
AttrModelTableDelete = AttrModelTable.delete
AttrModelTableUpdate = AttrModelTable.update

SSOSessionTable = SSOSession.__table__

# ################################################################################################################################

class AttrEntity:
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

class AttrAPI:
    """ A base class for both user and session SSO attributes.
    """
    def __init__(self, cid, current_user_id, is_super_user, current_app, remote_addr, odb_session_func, is_sqlite, encrypt_func,
        decrypt_func, user_id, ust=None):
        self.cid = cid
        self.current_user_id = current_user_id
        self.is_super_user = is_super_user
        self.current_app = current_app
        self.remote_addr = remote_addr
        self.odb_session_func = odb_session_func
        self.is_sqlite = is_sqlite
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.user_id = user_id
        self.ust = ust
        self.is_session_attr = bool(ust)

# ################################################################################################################################

    def _require_correct_user(self, op, target_user_id):
        """ Makes sure that during current operation self.current_user_id is the same as target_user_id (which means that
        a person accesses his or her own attribute) or that current operation is performed by a super-user.
        """
        if self.is_super_user or self.current_user_id == target_user_id:
            result = status_code.ok
            log_func = audit_pii.info
        else:
            result = status_code.error
            log_func = audit_pii.warn

        log_func(self.cid, '_require_correct_user', self.current_user_id,
            target_user_id, result, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'op':op, 'is_super_user':self.is_super_user})

        if result != status_code.ok:
            raise ValidationError(status_code.auth.not_allowed)

# ################################################################################################################################

    def _ensure_ust_is_not_expired(self, session, ust, now):

        return session.query(SSOSessionTable.c.ust).\
            filter(SSOSessionTable.c.ust==ust).\
            filter(SSOSessionTable.c.expiration_time > now).\
            first()

# ################################################################################################################################

    def _create(self, session, name, value, expiration=None, encrypt=False, user_id=None, needs_commit=True,
        _utcnow=_utcnow):
        """ A low-level implementation of self.create which expects an SQL session on input.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._create', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'name':name, 'expiration':expiration, 'encrypt':encrypt, 'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        self._require_correct_user('_create', user_id)

        now = _utcnow()

        attr_model = AttrModel()
        attr_model.user_id = user_id
        attr_model.ust = self.ust
        attr_model._ust_string = self.ust or '' # Cannot, and will not be, NULL, check the comment in the model for details
        attr_model.is_session_attr = self.is_session_attr
        attr_model.name = name
        attr_model.value = dumps(self.encrypt_func(value.encode('utf8')) if encrypt else value)
        attr_model.is_encrypted = encrypt
        attr_model.creation_time = now
        attr_model.last_modified = now

        # Expiration is optional
        attr_model.expiration_time = now + timedelta(seconds=expiration) if expiration else _default_expiration

        session.add(attr_model)

        if needs_commit:
            session.commit()

# ################################################################################################################################

    def create(self, name, value, expiration=None, encrypt=False, user_id=None):
        """ Creates a new named attribute, raising an exception if it already exists.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.create', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('create', user_id)

        with closing(self.odb_session_func()) as session:
            try:
                return self._create(session, name, value, expiration, encrypt, user_id)
            except IntegrityError:
                logger.warning(format_exc())
                raise ValidationError(status_code.attr.already_exists)

# ################################################################################################################################

    def _set(self, session, name, value, expiration=None, encrypt=False, user_id=None, needs_commit=True):
        """ A low-level implementation of self.set which expects an SQL session on input.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._set', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'name':name, 'expiration':expiration, 'encrypt':encrypt,
                'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('_set', user_id)

        # Check if the attribute exists ..
        if self._exists(session, name, user_id):

            # .. it does, so we need to set its new value.
            self._update(session, name, value, expiration, encrypt, user_id, needs_commit)

        # .. does not exist, so we need to create it
        else:
            self._create(session, name, value, expiration, encrypt, user_id, needs_commit)

# ################################################################################################################################

    def set(self, name, value, expiration=None, encrypt=False, user_id=None):
        """ Set value of a named attribute, creating it if it does not already exist.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.set', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('set', user_id)

        with closing(self.odb_session_func()) as session:
            self._set(session, name, value, expiration, encrypt)

# ################################################################################################################################

    def _update(self, session, name, value=None, expiration=None, encrypt=False, user_id=None, needs_commit=True,
        _utcnow=_utcnow):
        """ A low-level implementation of self.update which expects an SQL session on input.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._update', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'name':name, 'expiration':expiration, 'encrypt':encrypt,
                'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('_update', user_id)

        now = _utcnow()
        values = {
            'last_modified': now
        }

        if value:
            values['value'] = dumps(self.encrypt_func(value.encode('utf8')) if encrypt else value)

        if expiration:
            values['expiration_time'] = now + timedelta(seconds=expiration)

        and_condition = [
            AttrModelTable.c.user_id==(user_id),
            AttrModelTable.c.ust==self.ust,
            AttrModelTable.c.name==name,
            AttrModelTable.c.expiration_time > now,
        ]

        if self.ust:

            # SQLite needs to be treated in a special way, otherwise we get an exception from SQLAlchemy
            # NotImplementedError: This backend does not support multiple-table criteria within UPDATE
            # which means that on SQLite we need an additional query.
            if self.is_sqlite:
                result = self._ensure_ust_is_not_expired(session, self.ust, now)
                if not result:
                    raise ValidationError(status_code.session.no_such_session)
            else:
                and_condition.extend([
                    AttrModelTable.c.ust==SSOSessionTable.c.ust,
                    SSOSessionTable.c.expiration_time > now
                ])

        session.execute(
            AttrModelTableUpdate().\
            values(values).\
            where(and_(*and_condition)))

        if needs_commit:
            session.commit()

# ################################################################################################################################

    def update(self, name, value, expiration=None, encrypt=False, user_id=None):
        """ Updates an existing attribute, raising an exception if it does not already exist.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.update', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('update', user_id)

        with closing(self.odb_session_func()) as session:
            return self._update(session, name, value, expiration, encrypt, user_id)

# ################################################################################################################################

    def _get(self, session, data, decrypt, serialize_dt, user_id=None, columns=AttrModel, exists_only=False, _utcnow=_utcnow):
        """ A low-level implementation of self.get which knows how to return one or more named attributes.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._get', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'data':data, 'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('_get', user_id)

        data = [data] if isinstance(data, basestring) else data
        out = dict.fromkeys(data, None)

        now = _utcnow()

        q = session.query(columns).\
            filter(AttrModel.user_id==(user_id)).\
            filter(AttrModel.ust==self.ust).\
            filter(AttrModel.name.in_(data)).\
            filter(AttrModel.expiration_time > now)

        if self.ust:
            q = q.\
                filter(AttrModel.ust==SSOSession.ust).\
                filter(SSOSession.expiration_time > now)

        result = q.all()

        for item in result:
            out[item.name] = True if exists_only else AttrEntity.from_sql(item, decrypt, self.decrypt_func, serialize_dt)

        # Explicitly convert None to False to satisfy the requirement of returning a boolean value
        # if we are being called from self.exist (otherwise, None is fine).
        if exists_only:
            for key, value in out.items():
                if value is None:
                    out[key] = False

        if len(data) == 1:
            return out[data[0]]
        else:
            return out

# ################################################################################################################################

    def get(self, data, decrypt=True, serialize_dt=False, user_id=None):
        """ Returns a named attribute.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.get/get_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('get', user_id)

        with closing(self.odb_session_func()) as session:
            return self._get(session, data, decrypt, serialize_dt, user_id)

    # Same as .get but a list/tuple/set is given on input instead of a single name
    get_many = get

# ################################################################################################################################

    def _exists(self, session, data, user_id=None):
        """ A low-level implementation of self.exists which expects an SQL session on input.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._exists', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('_exists', user_id)

        return self._get(session, data, False, False, user_id, AttrModel.name, True)

# ################################################################################################################################

    def names(self, user_id=None, _utcnow=_utcnow):
        """ Returns names of all attributes as a list (unsorted).
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.names', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
            'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('names', user_id)

        now = _utcnow()

        with closing(self.odb_session_func()) as session:
            q = session.query(AttrModel.name).\
                filter(AttrModel.user_id==(user_id)).\
                filter(AttrModel.ust==self.ust).\
                filter(AttrModel.expiration_time > now)

            if self.ust:
                q = q.\
                    filter(AttrModel.ust==SSOSession.ust).\
                    filter(SSOSession.expiration_time > now)

            result = q.all()

        return [item.name for item in result]

# ################################################################################################################################

    def exists(self, data, user_id=None):
        """ Returns a boolean flag to indicate if input attribute(s) exist(s) or not.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.exists/exists_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('exists', user_id)

        with closing(self.odb_session_func()) as session:
            return self._exists(session, data, user_id)

    # Same API for both calls ('exist' could be another name but its exists_many for consistence with other methods)
    exists_many = exists

# ################################################################################################################################

    def delete(self, data, user_id=None, _utcnow=_utcnow):
        """ Deletes one or more names attributes.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.delete/delete_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'data':data, 'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('delete', user_id)

        now = _utcnow()
        data = [data] if isinstance(data, basestring) else data

        and_condition = [
            AttrModelTable.c.user_id==(user_id),
            AttrModelTable.c.ust==self.ust,
            AttrModelTable.c.name.in_(data),
            AttrModelTable.c.expiration_time > now,
        ]

        with closing(self.odb_session_func()) as session:

            if self.ust:

                # Check comment in self._update for a comment why the below is needed
                if self.is_sqlite:
                    result = self._ensure_ust_is_not_expired(session, self.ust, now)
                    if not result:
                        raise ValidationError(status_code.session.no_such_session)
                else:
                    and_condition.extend([
                        AttrModelTable.c.ust==SSOSessionTable.c.ust,
                        SSOSessionTable.c.expiration_time > now
                    ])

            session.execute(
                AttrModelTableDelete().\
                where(and_(*and_condition)))
            session.commit()

    # One method can handle both calls
    delete_many = delete

# ################################################################################################################################

    def _set_expiry(self, session, name, expiration, user_id=None, needs_commit=True):
        """ A low-level implementation of self.set_expiry which expects an SQL session on input.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._set_expiry', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'is_super_user':self.is_super_user})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('_set_expiry', user_id)

        return self._update(session, name, expiration=expiration, user_id=user_id, needs_commit=needs_commit)

# ################################################################################################################################

    def set_expiry(self, name, expiration, user_id=None):
        """ Sets expiration for a named attribute.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.set_expiry', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('set_expiry', user_id)

        with closing(self.odb_session_func()) as session:
            return self._set_expiry(session, name, expiration, user_id)

# ################################################################################################################################

    def _call_many(self, func, data, expiration=None, encrypt=False, user_id=None):
        """ A reusable method for manipulation of multiple attributes at a time.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr._call_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr,
                'is_super_user':self.is_super_user,
                'func':func.__func__.__name__})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        with closing(self.odb_session_func()) as session:
            for item in data:

                # Check access permissions to that user's attributes
                _user_id = item.get('user_id', user_id)
                self._require_correct_user('_call_many', _user_id)

                func(session, item['name'], item['value'], item.get('expiration', expiration),
                    item.get('encrypt', encrypt), _user_id, needs_commit=False)

            # Commit now everything added to session thus far
            try:
                session.commit()
            except IntegrityError:
                logger.warning(format_exc())
                raise ValidationError(status_code.attr.already_exists)

# ################################################################################################################################

    def create_many(self, data, expiration=None, encrypt=False, user_id=None):
        """ Creates multiple attributes in one call.
        """
        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Audit comes first
        audit_pii.info(self.cid, 'attr.create_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Check access permissions to that user's attributes
        self._require_correct_user('create_many', user_id)

        self._call_many(self._create, data, expiration, encrypt, user_id)

# ################################################################################################################################

    def update_many(self, data, expiration=None, encrypt=False, user_id=None):
        """ Update multiple attributes in one call.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.update_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('update_many', user_id)

        self._call_many(self._update, data, expiration, encrypt, user_id)

# ################################################################################################################################

    def set_many(self, data, expiration=None, encrypt=False, user_id=None):
        """ Sets values of multiple attributes in one call.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.set_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        # Check access permissions to that user's attributes
        self._require_correct_user('set_many', user_id)

        self._call_many(self._set, data, expiration, encrypt, user_id)

# ################################################################################################################################

    def set_expiry_many(self, data, expiration=None, user_id=None):
        """ Sets expiry for multiple attributes in one call.
        """
        # Audit comes first
        audit_pii.info(self.cid, 'attr.set_expiry_many', self.current_user_id,
            user_id, extra={'current_app':self.current_app, 'remote_addr':self.remote_addr})

        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        with closing(self.odb_session_func()) as session:
            for item in data:

                # Check access permissions to that user's attributes
                _user_id = item.get('user_id', user_id)
                self._require_correct_user('set_expiry_many', _user_id)

                # Check OK
                self._set_expiry(session, item['name'], item.get('expiration', expiration), _user_id, needs_commit=False)

            # Commit now everything added to session thus far
            session.commit()

# ################################################################################################################################

    def to_dict(self, decrypt=True, value_to_dict=False, serialize_dt=False, user_id=None, _utcnow=_utcnow):
        """ Returns a list of all attributes.
        """
        # Default to current user unless overridden on input
        user_id = user_id or self.user_id

        out = {}
        now = _utcnow()

        with closing(self.odb_session_func()) as session:
            q = session.query(AttrModel).\
                filter(AttrModel.user_id==(user_id)).\
                filter(AttrModel.ust==self.ust).\
                filter(AttrModel.expiration_time > now)

            if self.ust:
                q = q.\
                    filter(AttrModel.ust==SSOSession.ust).\
                    filter(SSOSession.expiration_time > now)

            result = q.all()

        for item in result:
            value = AttrEntity.from_sql(item, decrypt, self.decrypt_func, serialize_dt)
            out[item.name] = value.to_dict() if value_to_dict else value

        return out

# ################################################################################################################################
