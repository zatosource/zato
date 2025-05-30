# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import HTTPBasicAuth, APIKeySecurity, NTLM, OAuth, to_json
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list, oauth_list
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

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

        ntlm = ntlm_list(session, cluster_id)
        logger.info('Getting ntlm definitions')
        self._process_security_defs(ntlm, 'ntlm', out)

        oauth = oauth_list(session, cluster_id)
        oauth_json = to_json(oauth)
        logger.info('Getting oauth/bearer_token definitions: %s', oauth_json)
        self._process_security_defs(oauth, 'bearer_token', out)

        logger.info('Total security definitions from DB: %d', len(out))
        for name, details in out.items():
            logger.info('DB security def: name=%s type=%s', name, details.get('type'))

        return out

# ################################################################################################################################

    def compare_security_defs(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML defs with %d DB defs', len(yaml_defs), len(db_defs))
        logger.info('DB definition keys: %s', list(db_defs.keys()))

        for item in yaml_defs:
            name = item['name']
            sec_type = item['type']

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
                    if key in ('type', 'name', 'password'):
                        continue

                    if key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
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
            security_def.get('password'),
            cluster
        )

        set_instance_opaque_attrs(auth, security_def)
        return auth

# ################################################################################################################################

    def _create_bearer_token(self, security_def:'anydict', cluster:'any_') -> 'any_':
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
        return auth

# ################################################################################################################################

    def create_security_definition(self, security_def:'anydict', session:'SASession') -> 'any_':
        sec_type = security_def['type']
        def_name = security_def.get('name', 'unnamed')

        logger.info('Creating security definition: name=%s type=%s', def_name, sec_type)
        cluster = self.importer.get_cluster(session)

        if sec_type == 'basic_auth':
            auth = self._create_basic_auth(security_def, cluster)
        elif sec_type == 'apikey':
            auth = self._create_apikey(security_def, cluster)
        elif sec_type == 'ntlm':
            auth = self._create_ntlm(security_def, cluster)
        elif sec_type == 'bearer_token':
            auth = self._create_bearer_token(security_def, cluster)
        else:
            logger.warning('Unsupported security type: %s', sec_type)
            return None

        logger.info('Created new security definition: %s (type=%s)', def_name, sec_type)
        session.add(auth)
        return auth

# ################################################################################################################################

    def _update_definition(self, definition:'any_', security_def:'anydict') -> 'any_':
        for key, value in security_def.items():
            if key in ('type', 'name', 'id'):
                continue

            if hasattr(definition, key):
                setattr(definition, key, value)
            else:
                def_type = security_def['type']
                def_name = security_def['name']
                logger.warning(f'Invalid attribute {key!r} for {def_type} security definition {def_name!r}')

        set_instance_opaque_attrs(definition, security_def)
        return definition

# ################################################################################################################################

    def get_class_by_type(self, sec_type):
        class_map = {
            'basic_auth': HTTPBasicAuth,
            'apikey': APIKeySecurity,
            'ntlm': NTLM,
            'bearer_token': OAuth
        }
        return class_map[sec_type]

# ################################################################################################################################

    def update_security_definition(self, sec_def:'anydict', session:'SASession', db_defs:'anydict') -> 'any_':
        sec_type = sec_def['type']
        def_id = sec_def['id']
        def_name = sec_def['name']

        model = self.get_class_by_type(sec_type)

        db_def = db_defs[def_name]
        for item in db_def:
            if item not in sec_def and item not in ('id', 'type', 'definition'):
                sec_def[item] = db_def[item]

        definition = session.query(model).filter_by(id=def_id).one()
        self._update_definition(definition, sec_def)

        session.add(definition)
        return definition

# ################################################################################################################################

    def sync_security_definitions(self, security_list:'anylist', session:'SASession') -> 'listtuple':
        security_yaml_defs = [item for item in security_list if 'type' in item]
        logger.info('Processing %d security definitions from YAML', len(security_yaml_defs))

        db_defs = self.get_security_defs_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_security_defs(security_yaml_defs, db_defs)

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

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

            # Populate sec_defs after commit, so instance IDs are available
            for item_in_yaml in to_create: 
                created_instance = next((inst for inst in out_created if inst.name == item_in_yaml['name']), None)
                if created_instance:
                    instance_dict = {
                        'id': created_instance.id, 
                        'name': created_instance.name,
                        'type': item_in_yaml['type'] 
                    }
                    self.importer.sec_defs[created_instance.name] = instance_dict

            for item_in_yaml in to_update:
                updated_instance = next((inst for inst in out_updated if inst.name == item_in_yaml['name']), None)
                if updated_instance:
                    instance_dict = {
                        'id': updated_instance.id, 
                        'name': updated_instance.name,
                        'type': item_in_yaml['type']
                    }
                    self.importer.sec_defs[updated_instance.name] = instance_dict

        except Exception as e:
            logger.error('Error syncing security definitions: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
