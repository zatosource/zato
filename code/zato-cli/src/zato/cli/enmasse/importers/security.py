# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from uuid import uuid4

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.cli.enmasse.util.secrets import Auto_Password_Prefix, decrypt_secret, encrypt_secret, ensure_encrypted, \
    is_encrypted, is_usable_secret
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import loads
from zato.common.odb.model import HTTPBasicAuth, APIKeySecurity, MTLSSecurity, NTLM, OAuth, SPNEGOSecurity, to_json, \
    WSSecurity
from zato.common.odb.query import basic_auth_list, apikey_security_list, mtls_list, ntlm_list, oauth_list, spnego_list, \
    wss_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The security types whose password column holds a secret - the other types keep their material in opaque attributes.
_types_with_password = ('basic_auth', 'apikey', 'ntlm', 'wss', 'bearer_token')

# The keys that never take part in the comparison of a YAML definition with a stored one.
_comparison_skip_keys = ('type', 'name', 'rate_limiting')

# How many bits of randomness an auto-generated password carries.
_auto_password_bits = 128

# ################################################################################################################################
# ################################################################################################################################

def password_needs_update(session:'SASession', yaml_password:'any_', db_password:'strnone') -> 'bool':
    """ Returns True if the password the YAML gives differs from the one stored, once the stored one is decrypted.
    A YAML password that is not usable is never compared, so it never triggers an update.
    """
    if not is_usable_secret(yaml_password):
        return False

    # The column is nullable, so a row may hold no password at all
    if db_password is None:
        return True

    stored = decrypt_secret(session, db_password)

    out = stored != yaml_password
    return out

# ################################################################################################################################
# ################################################################################################################################

class SecurityImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def _process_security_defs(self, query_result:'any_', sec_type:'str', out:'dict') -> 'None':
        definitions = to_json(query_result, return_as_dict=True)
        logger.info('Processing %d %s definitions', len(definitions), sec_type)

        for item in definitions:
            item['type'] = sec_type
            name = item['name']

            # Fields stored as opaque attributes, e.g. issuer, jwks_url, audience or claims,
            # are part of the definition too, so they can be compared against YAML input.
            if opaque1 := item.get('opaque1'):
                opaque = loads(opaque1)
                for key, value in opaque.items():
                    if key not in item:
                        item[key] = value

            logger.info('Processing security definition: %s (type=%s, id=%s)', name, sec_type, item.get('id'))
            out[name] = item

# ################################################################################################################################

    def get_security_defs_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving security definitions from database for cluster_id=%s', cluster_id)

        basic_auth = basic_auth_list(session, cluster_id)
        logger.info('Getting basic_auth definitions')
        self._process_security_defs(basic_auth, 'basic_auth', out)

        apikey = apikey_security_list(session, cluster_id)
        logger.info('Getting apikey definitions')
        self._process_security_defs(apikey, 'apikey', out)

        mtls = mtls_list(session, cluster_id)
        logger.info('Getting mtls definitions')
        self._process_security_defs(mtls, 'mtls', out)

        ntlm = ntlm_list(session, cluster_id)
        logger.info('Getting ntlm definitions')
        self._process_security_defs(ntlm, 'ntlm', out)

        spnego = spnego_list(session, cluster_id)
        logger.info('Getting spnego definitions')
        self._process_security_defs(spnego, 'spnego', out)

        oauth = oauth_list(session, cluster_id)
        logger.info('Getting oauth/bearer_token definitions')
        self._process_security_defs(oauth, 'bearer_token', out)

        wss = wss_list(session, cluster_id)
        logger.info('Getting wss definitions')
        self._process_security_defs(wss, 'wss', out)

        # Filter out specified keys from each security definition
        to_remove = ['cluster_name']

        for item in out.values():
            for key in to_remove:
                if key in item:
                    del item[key]

        logger.info('Total security definitions from DB: %d', len(out))
        for name, details in out.items():
            logger.info('DB security def: name=%s type=%s', name, details.get('type'))

        return out

# ################################################################################################################################

    def compare_security_defs(self, yaml_defs:'anylist', db_defs:'anydict', session:'SASession') -> 'listtuple':

        to_create = []
        to_update = []

        logger.info('Comparing %d YAML defs with %d DB defs', len(yaml_defs), len(db_defs))
        logger.info('DB definition keys: %s', list(db_defs.keys()))

        for item in yaml_defs:
            item = preprocess_item(item)

            if 'auth_endpoint' in item:
                logger.debug('Renaming auth_endpoint to auth_server_url')
                item['auth_server_url'] = item.pop('auth_endpoint')

            name = item['name']
            sec_type = item['type']

            if sec_type == 'apikey' and 'username' not in item:
                item['username'] = f'Zato-Not-Used-{uuid4().hex}'

            if sec_type == 'apikey' and 'header' not in item:
                item['header'] = 'X-API-Key'

            if sec_type == 'bearer_token':

                # Detect static vs dynamic bearer tokens by the presence of static fields
                is_static = 'static_header' in item or 'static_token' in item or 'static_prefix' in item \
                    or item.get('is_static_token')

                if is_static:
                    item['is_static_token'] = True

                    # The token lives in the password column - it is import-only and never exported
                    if static_token := item.pop('static_token', None):
                        item['password'] = static_token

                    if 'static_header' not in item:
                        item['static_header'] = 'Authorization'
                    if 'static_prefix' not in item:
                        item['static_prefix'] = 'bearer'
                    if 'username' not in item:
                        item['username'] = f'Zato-Not-Used-{uuid4().hex}'
                else:
                    if 'client_id_field' not in item:
                        item['client_id_field'] = 'client_id'
                    if 'client_secret_field' not in item:
                        item['client_secret_field'] = 'client_secret'
                    if 'grant_type' not in item:
                        item['grant_type'] = 'client_credentials'
                    if 'data_format' not in item:
                        item['data_format'] = 'form'

            logger.info('Checking YAML def: name=%s type=%s', name, sec_type)

            if not name:
                logger.warning('Skipping unnamed security definition')
                continue

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Definition %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Definition %s exists in DB with id=%s type=%s', name, db_def.get('id'), db_def.get('type'))

                needs_update = False
                for key, value in item.items():
                    if key in _comparison_skip_keys:
                        continue
                    if key == 'username' and sec_type == 'apikey':
                        continue
                    if key not in db_def:
                        continue

                    # The stored password is encrypted, so it is compared through decryption,
                    # and a YAML password that is not usable is not compared at all.
                    if key == 'password':
                        if password_needs_update(session, value, db_def[key]):
                            logger.info('Password mismatch for %s', name)
                            needs_update = True
                            break
                        continue

                    db_value = db_def[key]
                    if db_value != value:
                        logger.info('Value mismatch for %s.%s', name, key)
                        needs_update = True
                        break

                if needs_update:
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
        return to_create, to_update

# ################################################################################################################################

    def _create_basic_auth(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = HTTPBasicAuth(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('realm', 'zato'),
            security_def['password'],
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_apikey(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = APIKeySecurity(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def['password'],
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_ntlm(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = NTLM(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def['password'],
            cluster
        )

        # The model's constructor does not store the password it is given
        auth.password = security_def['password']

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_mtls(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = MTLSSecurity(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['name'],
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_spnego(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = SPNEGOSecurity(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['name'],
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_wss(self, security_def:'anydict', cluster:'any_') -> 'any_':
        auth = WSSecurity(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('password'),
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_bearer_token(self, security_def:'anydict', cluster:'any_') -> 'any_':
        name = security_def['name']

        auth = OAuth(
            None,
            security_def['name'],
            security_def.get('is_active', True),
            security_def['username'],
            security_def.get('password'),
            'not-used',
            'not-used',
            0,
            cluster
        )
        set_instance_opaque_attrs(auth, security_def)

        logger.debug('Created bearer_token `%s`', name)
        return auth

# ################################################################################################################################

    def create_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        sec_type = security_def['type']
        def_name = security_def.get('name', 'unnamed')

        logger.info('Creating security definition: name=%s type=%s', def_name, sec_type)
        cluster = self.importer.get_cluster(session)

        # The definition is written from a copy so that the YAML item keeps the password as the YAML gave it
        security_def = dict(security_def)

        # A definition whose type has a password gets a generated one if the YAML gives none,
        # and whichever it is, it is stored encrypted.
        if sec_type in _types_with_password:
            password = security_def.get('password')

            if not password:
                password = Auto_Password_Prefix + CryptoManager.generate_hex_string(_auto_password_bits)

            security_def['password'] = encrypt_secret(session, password)

        if sec_type == 'basic_auth':
            auth = self._create_basic_auth(security_def, cluster)
        elif sec_type == 'apikey':
            auth = self._create_apikey(security_def, cluster)
        elif sec_type == 'mtls':
            auth = self._create_mtls(security_def, cluster)
        elif sec_type == 'spnego':
            auth = self._create_spnego(security_def, cluster)
        elif sec_type == 'ntlm':
            auth = self._create_ntlm(security_def, cluster)
        elif sec_type == 'wss':
            auth = self._create_wss(security_def, cluster)
        elif sec_type == 'bearer_token':
            auth = self._create_bearer_token(security_def, cluster)
        else:
            logger.warning('Unsupported security type: %s', sec_type)
            return None

        logger.info('Created new security definition: %s (type=%s)', def_name, sec_type)
        session.add(auth)
        return auth

# ################################################################################################################################

    def _update_definition(self, definition:'any_', security_def:'anydict', session:'SASession') -> 'any_':

        sec_type = security_def.get('type')

        for key, value in security_def.items():
            if key in ('type', 'name', 'id'):
                continue
            if key == 'username' and sec_type == 'apikey':
                continue

            # The password column always holds an encrypted value - a password the YAML gave is encrypted here
            # and a stored one that was kept is encrypted in place if it was in clear text. The column is nullable.
            if key == 'password':
                if value is not None:
                    value = ensure_encrypted(session, value)

            if hasattr(definition, key):
                setattr(definition, key, value)

        set_instance_opaque_attrs(definition, security_def)
        return definition

# ################################################################################################################################

    def get_class_by_type(self, sec_type):
        class_map = {
            'basic_auth': HTTPBasicAuth,
            'apikey': APIKeySecurity,
            'mtls': MTLSSecurity,
            'ntlm': NTLM,
            'spnego': SPNEGOSecurity,
            'bearer_token': OAuth,
            'wss': WSSecurity
        }
        return class_map[sec_type]

# ################################################################################################################################

    def update_security_definition(self, sec_def:'anydict', session:'SASession', db_defs:'anydict') -> 'any_':
        sec_type = sec_def['type']
        def_id = sec_def['id']
        def_name = sec_def['name']
        logger.debug('Updating security definition: name=%s type=%s id=%s', def_name, sec_type, def_id)

        model = self.get_class_by_type(sec_type)

        # The definition is updated from a copy so that the YAML item keeps the password as the YAML gave it
        sec_def = dict(sec_def)

        # Remember which of the two mutually exclusive keys came from YAML
        # before database values are merged in below.
        has_yaml_quota_tier = 'quota_tier' in sec_def
        has_yaml_rate_limiting = 'rate_limiting' in sec_def

        # A password the YAML does not give in a usable form never replaces the stored one,
        # which is merged in from the database below instead.
        if not is_usable_secret(sec_def.get('password')):
            _ = sec_def.pop('password', None)

        db_def = db_defs[def_name]

        if 'opaque1' in db_def and db_def['opaque1']:
            opaque_data = loads(db_def['opaque1'])
            for key, value in opaque_data.items():
                if key not in sec_def:
                    sec_def[key] = value

        for item in db_def:
            if item not in sec_def and item not in ('id', 'type', 'definition', 'opaque1'):
                sec_def[item] = db_def[item]

        # A definition either references a quota tier or carries its own rules, never both,
        # so the stale counterpart merged in from the previous opaque data is dropped.
        if has_yaml_quota_tier and 'rate_limiting' in sec_def:
            del sec_def['rate_limiting']

        if has_yaml_rate_limiting and 'quota_tier' in sec_def:
            del sec_def['quota_tier']

        definition = session.query(model).filter_by(id=def_id).one()
        self._update_definition(definition, sec_def, session)

        session.add(definition)
        logger.debug('Finished updating security definition: %s', def_name)
        return definition

# ################################################################################################################################

    def _encrypt_kept_passwords(
        self,
        security_list:'anylist',
        to_update:'anylist',
        db_defs:'anydict',
        session:'SASession',
    ) -> 'None':
        """ Encrypts in place the password of every definition the YAML names that needed no update
        and whose stored password is still in clear text. Its value does not change, only its form,
        so this is not an update.
        """
        updated_names = {item['name'] for item in to_update}

        for item in security_list:
            name = item['name']

            if name in updated_names:
                continue

            db_def = db_defs.get(name)

            # A definition that was just created is not in the snapshot the comparison used
            if not db_def:
                continue

            # The column is nullable and not every type has one
            stored = db_def.get('password')
            if stored is None:
                continue

            if is_encrypted(stored):
                continue

            model = self.get_class_by_type(db_def['type'])
            definition = session.query(model).filter_by(id=db_def['id']).one()
            definition.password = encrypt_secret(session, stored)
            session.add(definition)

            logger.info('Encrypted the stored password of %s in place', name)

# ################################################################################################################################

    def sync_security_definitions(self, security_list:'anylist', session:'SASession') -> 'listtuple':

        count = len(security_list)
        noun = 'definition' if count == 1 else 'definitions'
        logger.info(f'Processing {count} security {noun} from YAML')

        valid_types = {'basic_auth', 'mtls', 'ntlm', 'spnego', 'bearer_token', 'apikey', 'wss'}

        for item in security_list:
            if item['type'] not in valid_types:
                raise ValueError(f'Invalid security definition type: {item["type"]}. Must be one of {valid_types} -> {item}')

        # Resolve quota tier references - YAML carries tier names but opaque data stores tier ids.
        for item in security_list:

            if 'quota_tier' not in item:
                continue

            # A definition either references a tier or carries its own rules, never both
            if 'rate_limiting' in item:
                raise ValueError(f'Security definition `{item["name"]}` cannot have both quota_tier and rate_limiting')

            tier_name = item['quota_tier']
            tier_def = self.importer.quota_tier_defs.get(tier_name)

            if not tier_def:
                raise ValueError(f'Quota tier `{tier_name}` not found for security definition `{item["name"]}`')

            item['quota_tier'] = tier_def['id']

        db_defs = self.get_security_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_security_defs(security_list, db_defs, session)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new security definitions', len(to_create))
            for item in to_create:
                logger.info('Creating security definition: name=%s type=%s', item.get('name'), item.get('type'))
                instance = self.create_security_definition(item, session)
                if instance:
                    logger.info('Created security definition: name=%s id=%s', instance.name, getattr(instance, 'id', None))
                out_created.append(instance)

            logger.info('Updating %d existing security definitions', len(to_update))
            for item in to_update:
                logger.info('Updating security definition: name=%s id=%s', item.get('name'), item.get('id'))
                instance = self.update_security_definition(item, session, db_defs)
                if instance:
                    logger.info('Updated security definition: name=%s id=%s', instance.name, getattr(instance, 'id', None))
                    out_updated.append(instance)

            self._encrypt_kept_passwords(security_list, to_update, db_defs, session)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

            self.populate_sec_defs_from_db(session)

        except Exception as e:
            logger.error('Error syncing security definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################

    def populate_sec_defs_from_db(self, session:'SASession') -> 'None':
        """ Populates the importer's sec_defs dictionary from existing DB entries.
        """
        db_defs = self.get_security_defs_from_db(session, self.importer.cluster_id)

        for name, def_info in db_defs.items():
            self.importer.sec_defs[name] = {
                'id': def_info['id'],
                'name': name,
                'type': def_info['type']
            }

        logger.info('Populated %d security definitions from database', len(self.importer.sec_defs))

# ################################################################################################################################
# ################################################################################################################################
