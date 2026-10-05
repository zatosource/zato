# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps, loads
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import OAuth as COMMON_OAUTH, query_parameters, SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.const import SECRETS
from zato.common.odb.model import Cluster, OAuth
from zato.common.odb.query import oauth_list
from zato.common.private_key_jwt import get_public_jwk, get_public_key_pem, load_private_key, validate_definition
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, ChangePasswordBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The input fields shared by Create and Edit
_common_optional_input = '-username', '-client_id_field', \
    '-client_secret_field', '-grant_type', '-data_format', '-auth_server_url', '-scopes', '-extra_fields', \
    '-static_header', '-is_static_token', '-static_prefix', \
    '-issuer', '-jwks_url', '-audience', '-claims', '-identity_claim', \
    '-client_auth_method', '-private_key', '-jwt_algorithm', '-key_id', '-assertion_audience', '-certificate'

# ################################################################################################################################
# ################################################################################################################################

def _encrypt_private_key(service:'AdminService', input:'any_') -> 'None':
    """ Encrypts the private key on input unless it is already encrypted, which is the case when enmasse sends it.
    """
    for name in COMMON_OAUTH.Secret_Fields:
        if value := input.get(name):
            if not value.startswith(SECRETS.PREFIX):
                input[name] = service.server.encrypt(value)

# ################################################################################################################################

def _validate_private_key_jwt(service:'AdminService', input:'any_', private_key:'str') -> 'None':
    """ Checks a private key JWT definition before it is stored - the key must parse and match its algorithm,
    and a certificate, if given, must belong to the key. The key arrives either in plain text or encrypted.
    """
    if input.get('client_auth_method') != COMMON_OAUTH.Client_Auth_Method.Private_Key_JWT:
        return

    if not private_key:
        raise Exception('Bearer token definition `{}` needs a private key to use private key JWT'.format(input.name))

    jwt_algorithm = input.get('jwt_algorithm') or COMMON_OAUTH.Default.JWT_Algorithm
    certificate = input.get('certificate') or ''

    private_key = service.server.decrypt(private_key)
    _ = validate_definition(private_key, jwt_algorithm, certificate)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of Bearer token definitions available.
    """
    _filter_by = OAuth.name,

    input = 'cluster_id', *query_parameters
    output = 'id', 'name', 'is_active', 'username', 'client_id_field', 'client_secret_field', 'grant_type', \
        '-auth_server_url', '-scopes', '-extra_fields', '-data_format', \
        '-static_header', 'is_static_token', '-static_prefix', \
        '-issuer', '-jwks_url', '-audience', '-claims', '-identity_claim', \
        '-client_auth_method', 'has_private_key', '-jwt_algorithm', '-key_id', '-assertion_audience', '-certificate'

    def get_data(self, session:'any_') -> 'anylist':
        data = elems_with_opaque(self._search(oauth_list, session, self.request.input.cluster_id, False)) # type: ignore

        # The token itself is never returned - only a flag indicating whether the definition uses one ..
        for item in data:
            is_static_token = bool(item.pop('static_token', None)) or bool(item.get('is_static_token'))
            item['is_static_token'] = is_static_token

            # .. and the same goes for the private key.
            item['has_private_key'] = bool(item.pop('private_key', None))

        return data

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.strip_listing_secrets(self.get_data(session))
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new Bearer token definition.
    """
    input = 'cluster_id', 'name', 'is_active', *_common_optional_input
    output = 'id', 'name', 'has_private_key'

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex
        input.is_static_token = bool(input.is_static_token)

        # A private key JWT definition must have a usable key before anything is stored ..
        _validate_private_key_jwt(self, input, input.get('private_key') or '')

        # .. and the key is never stored in clear text.
        _encrypt_private_key(self, input)

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(OAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OAuth.name==input.name).first()

                if existing_one:
                    raise Exception('Bearer token definition `{}` already exists in this cluster'.format(input.name))

                definition = OAuth()
                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username
                definition.proto_version = 'not-used' # type: ignore
                definition.sig_method = 'not-used' # type: ignore
                definition.max_nonce_log = 0 # type: ignore
                definition.cluster = cluster # type: ignore

                set_instance_opaque_attrs(definition, input)

                session.add(definition)
                session.commit()

            except Exception:
                msg = 'Bearer token definition could not be created, e:`%s`'
                self.logger.error(msg, format_exc())
                session.rollback()

                raise
            else:
                input.id = definition.id
                input.action = SECURITY.OAUTH_CREATE.value
                input.sec_type = SEC_DEF_TYPE.OAUTH
                self.config_dispatcher.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name
            self.response.payload.has_private_key = bool(input.get('private_key'))

        # Make sure the object has been created
        _:'any_' = self.server.config_manager.wait_for_oauth(input.name)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an Bearer token definition.
    """
    input = 'id', 'cluster_id', 'name', 'is_active', *_common_optional_input
    output = 'id', 'name', 'has_private_key'

    def handle(self):
        input = self.request.input
        input.is_static_token = bool(input.is_static_token)
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(OAuth).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(OAuth.name==input.name).\
                    filter(OAuth.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('Bearer token definition `{}` already exists in this cluster'.format(input.name))

                definition = session.query(OAuth).filter_by(id=input.id).one()
                old_name = definition.name

                # The Dashboard never shows the stored key, so an empty one on input means it is to be kept ..
                opaque = loads(definition.opaque1) if definition.opaque1 else {}
                for name in COMMON_OAUTH.Secret_Fields:
                    if not input.get(name):
                        if stored_value := opaque.get(name):
                            input[name] = stored_value

                # .. the definition must still be usable with whatever key it ends up with ..
                _validate_private_key_jwt(self, input, input.get('private_key') or '')

                # .. and a new key is never stored in clear text.
                _encrypt_private_key(self, input)

                definition.name = input.name
                definition.is_active = input.is_active
                definition.username = input.username

                set_instance_opaque_attrs(definition, input)

                session.add(definition)
                session.commit()

            except Exception:
                msg = 'Bearer token definition could not be updated, e:`%s`'
                self.logger.error(msg, format_exc())
                session.rollback()

                raise
            else:
                input.action = SECURITY.OAUTH_EDIT.value
                input.old_name = old_name
                input.sec_type = SEC_DEF_TYPE.OAUTH
                self.config_dispatcher.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name
                self.response.payload.has_private_key = bool(input.get('private_key'))

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an Bearer token definition.
    """
    password_required = False

    def handle(self):
        def _auth(instance:'any_', password:'str'):
            instance.password = password

            # Static tokens used to be kept in the opaque attributes - the password column
            # is their only home now, so the old copy is removed here.
            if instance.opaque1:
                opaque = loads(instance.opaque1)
                if 'static_token' in opaque:
                    del opaque['static_token']
                    opaque['is_static_token'] = True
                    instance.opaque1 = dumps(opaque)

        return self._handle(OAuth, _auth, SECURITY.OAUTH_CHANGE_PASSWORD.value)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an Bearer token definition.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(OAuth).\
                    filter(OAuth.id==self.request.input.id).\
                    one()

                # .. clean up all pub/sub state before the CASCADE delete ..
                self.server.config_manager.cleanup_security_pubsub(session, auth.id, auth.username)

                session.delete(auth)
                session.commit()
            except Exception:
                msg = 'Bearer token definition could not be deleted, e:`%s`'
                self.logger.error(msg, format_exc())
                session.rollback()

                raise
            else:
                self.request.input.action = SECURITY.OAUTH_DELETE.value
                self.request.input.name = auth.name
                self.config_dispatcher.publish(self.request.input)

# ################################################################################################################################
# ################################################################################################################################

class GetPublicKey(AdminService):
    """ Returns the public half of a private key JWT definition's key - as PEM and as a JWK set,
    which is what authorization servers ask for when the client is registered with them.
    """
    input = 'id'
    output = 'name', 'jwt_algorithm', 'key_id', 'public_key_pem', AsIs('jwks')

    def handle(self):
        with closing(self.odb.session()) as session:
            definition = session.query(OAuth).filter_by(id=self.request.input.id).one()
            opaque = loads(definition.opaque1) if definition.opaque1 else {}

        private_key = opaque.get('private_key')
        if not private_key:
            raise Exception('Bearer token definition `{}` has no private key'.format(definition.name))

        jwt_algorithm = opaque.get('jwt_algorithm') or COMMON_OAUTH.Default.JWT_Algorithm
        key_id = opaque.get('key_id') or ''

        # .. the key is stored encrypted and parsed only for the time it takes to derive its public half.
        key = load_private_key(self.server.decrypt(private_key))

        self.response.payload.name = definition.name
        self.response.payload.jwt_algorithm = jwt_algorithm
        self.response.payload.key_id = key_id
        self.response.payload.public_key_pem = get_public_key_pem(key)
        self.response.payload.jwks = {'keys': [get_public_jwk(key, jwt_algorithm, key_id)]}

# ################################################################################################################################
# ################################################################################################################################
