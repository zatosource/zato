# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module holds the half of EnmasseYAMLImporter that deletes objects. An item marked should_delete is taken out of
# its section before anything is imported, the file is checked for items that conflict with or refer to what it
# deletes, and each marked item is then deleted through the same admin service the Dashboard invokes, with the id
# enmasse resolves from the item's name. The registry of sections, rows and services is in delete_targets.py.
# This class is only ever used as one of the bases of EnmasseYAMLImporter.

# stdlib
import logging

# Zato
from zato.cli.enmasse.client import get_server_client
from zato.cli.enmasse.importer.delete_targets import Key_Field_Security, Section_Alert_Notifications, Section_Alert_Rules, \
    Section_Generic_Connection, Should_Delete_Key, deferred_sections, generic_type_to_section, get_delete_order, \
    get_key_field, is_known_section, log_dependents, resolve_targets, section_aliases
from zato.cli.enmasse.importer.delete_references import check_references
from zato.cli.enmasse.util.common import preprocess_item, Security_Alias_Key
from zato.cli.enmasse.util.secrets import Session_Key_Server_Dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ################################################################################################################################
# ################################################################################################################################

# The key a zato_generic_connection item names its type under, and the key the importers move it to
_generic_type_key          = 'type'
_generic_type_key_internal = 'type_'

# ################################################################################################################################
# ################################################################################################################################

class DeleteSync:
    """ Takes the items marked should_delete out of a YAML config and deletes them through the admin services.
    """

    # Set by EnmasseYAMLImporter.__init__, declared here for the type checker
    cluster_id:'int'

# ################################################################################################################################

    def init_deletions(self) -> 'None':
        """ Initializes the deletion state of a new importer - the per-import tracking and the client that outlives it.
        """
        self.reset_deletion_tracking()

        # The client the delete services are invoked through, built when the first deletion needs it
        self.delete_client:'ZatoClient | None' = None

# ################################################################################################################################

    def reset_deletion_tracking(self) -> 'None':
        """ Resets everything one import's deletions are tracked with.
        """

        # The keys of the items marked for deletion, by the canonical section
        self.deletions:'dict[str, strlist]' = {}

        # The unmarked items of each canonical section, for the checks against what is deleted
        self.unmarked_items:'dict[str, anylist]' = {}

        # What was deleted, by section, each entry with the key and the id of the row
        self.deleted_objects:'dict[str, anylist]' = {}

# ################################################################################################################################

    def _get_canonical_section(self, key:'str', item:'stranydict') -> 'str':
        """ Returns the section an item belongs to - its own key, what an alias stands for, or the section
        a zato_generic_connection item names through its type.
        """
        if key == Section_Generic_Connection:
            if _generic_type_key in item:
                type_ = item[_generic_type_key]
            else:
                type_ = item[_generic_type_key_internal]
            out = generic_type_to_section[type_]

        elif key in section_aliases:
            out = section_aliases[key]

        else:
            out = key

        return out

# ################################################################################################################################

    def _add_deletion(self, section:'str', item:'stranydict', position:'int') -> 'None':
        """ Records one marked item under its canonical section after resolving its key against the environment.
        """
        if not is_known_section(section):
            raise Exception(f'Section `{section}` does not support `{Should_Delete_Key}`')

        key_field = get_key_field(section)
        item = preprocess_item(item)

        if key_field not in item:
            raise Exception(f'Item {position} of section `{section}` is marked `{Should_Delete_Key}` but has no `{key_field}`')

        keys = self.deletions.setdefault(section, [])
        keys.append(item[key_field])

# ################################################################################################################################

    def _split_section(self, key:'str', items:'anylist') -> 'anylist':
        """ Takes the marked items out of one list section and returns the items that stay in it.
        """
        out:'anylist' = []

        for position, item in enumerate(items):

            # The marker never reaches the importers, whatever its value
            is_marked = False
            if Should_Delete_Key in item:
                is_marked = bool(item.pop(Should_Delete_Key))

            section = self._get_canonical_section(key, item)

            if is_marked:
                if section == Section_Alert_Rules:
                    raise Exception(f'Section `{Section_Alert_Rules}` does not support `{Should_Delete_Key}`')
                self._add_deletion(section, item, position)
            else:
                out.append(item)
                unmarked = self.unmarked_items.setdefault(section, [])
                unmarked.append(item)

        return out

# ################################################################################################################################

    def split_deletions(self, yaml_config:'stranydict') -> 'None':
        """ Separates the items marked for deletion from every section of the config and checks that nothing left
        in the file conflicts with or refers to what is deleted. The config is modified in place.
        """
        self.reset_deletion_tracking()

        for key in list(yaml_config):
            items = yaml_config[key]

            # The notification targets are one mapping that cannot be deleted ..
            if key == Section_Alert_Notifications:
                if Should_Delete_Key in items:
                    raise Exception(f'Section `{Section_Alert_Notifications}` does not support `{Should_Delete_Key}`')
                continue

            # .. an include list or any other non-list value has no items to mark ..
            if not isinstance(items, list):
                continue

            # .. and every list section may have marked items.
            yaml_config[key] = self._split_section(key, items)

        if self.deletions:
            self._check_conflicts()
            check_references(self.deletions, self.unmarked_items, yaml_config)

            count = sum(len(keys) for keys in self.deletions.values())
            noun = 'item' if count == 1 else 'items'
            logger.info('Found %d %s marked for deletion: %s', count, noun, self.deletions)

# ################################################################################################################################

    def _check_conflicts(self) -> 'None':
        """ Refuses a file in which the same key of one section is both marked for deletion and not.
        """
        for section, keys in self.deletions.items():
            key_field = get_key_field(section)
            unmarked = self.unmarked_items.get(section, [])

            for item in unmarked:

                # The alternative spelling of the security key is accepted the way the importers accept it
                if key_field == Key_Field_Security and Key_Field_Security not in item:
                    unmarked_key = item.get(Security_Alias_Key)
                else:
                    unmarked_key = item.get(key_field)

                if unmarked_key in keys:
                    raise Exception(
                        f'Section `{section}` has `{unmarked_key}` both marked `{Should_Delete_Key}` and not - ' + \
                        'an object cannot be deleted and defined in one file')

# ################################################################################################################################

    def get_delete_client(self, session:'SASession', server_dir:'strnone') -> 'ZatoClient':
        """ Returns the client the delete services are invoked through, building it on first use.
        """
        if self.delete_client is None:

            if not server_dir:
                server_dir = session.info.get(Session_Key_Server_Dir)

            if not server_dir:
                raise Exception('Deleting objects requires the directory of a running server')

            self.delete_client = get_server_client(server_dir)

        return self.delete_client

# ################################################################################################################################

    def _delete_in_session(self, target:'any_', session:'SASession') -> 'None':
        """ Removes a row no admin service deletes.
        """
        row = session.query(target.model).filter_by(id=target.id).one()
        session.delete(row)
        session.commit()

# ################################################################################################################################

    def _delete_through_service(self, target:'any_', session:'SASession', server_dir:'strnone') -> 'None':
        """ Invokes the admin service that deletes the row - the one the Dashboard invokes.
        """
        cluster_id = self.cluster_id

        # The session holds no open transaction while the service writes to the same database ..
        session.commit()

        client = self.get_delete_client(session, server_dir)
        request = {'cluster_id': cluster_id, 'id': target.id}

        logger.info('Invoking %s for `%s` `%s` (id=%s)', target.service, target.section, target.key, target.id)
        response = client.invoke(target.service, request)

        if not response.ok:
            raise Exception(
                f'Could not delete `{target.section}` `{target.key}` through {target.service} -> {response.details}')

        # .. and what it read before the deletion is read again afterwards.
        session.expire_all()

# ################################################################################################################################

    def _run_sections(self, sections:'strlist', session:'SASession', server_dir:'strnone') -> 'None':
        """ Deletes every marked item of the sections given, in the order given.
        """
        cluster_id = self.cluster_id

        for section in sections:
            for key in self.deletions[section]:

                targets = resolve_targets(section, key, session, cluster_id)

                if not targets:
                    logger.info('No `%s` object named `%s` exists, nothing to delete', section, key)
                    continue

                for target in targets:
                    log_dependents(target, session, cluster_id)

                    if target.service:
                        self._delete_through_service(target, session, server_dir)
                    else:
                        self._delete_in_session(target, session)

                    deleted = self.deleted_objects.setdefault(section, [])
                    deleted.append({'name': key, 'id': target.id})

                    logger.info('Deleted `%s` `%s` (id=%s)', section, key, target.id)

# ################################################################################################################################

    def _log_processed(self, sections:'strlist') -> 'None':
        counts:'anydict' = {}

        for section in sections:
            counts[section] = len(self.deleted_objects.get(section, []))

        logger.info('Processed deletions: %s', counts)

# ################################################################################################################################

    def run_deletions(self, session:'SASession', server_dir:'strnone') -> 'None':
        """ Deletes every marked item except the deferred ones, dependents first, before anything is created or updated.
        """
        if not self.deletions:
            return

        sections = get_delete_order(set(self.deletions))
        self._run_sections(sections, session, server_dir)
        self._log_processed(sections)

# ################################################################################################################################

    def run_deferred_deletions(self, session:'SASession', server_dir:'strnone') -> 'None':
        """ Deletes the marked items of the sections whose rows are refused while anything references them,
        after the create and update pass has had its chance to drop the references.
        """
        sections:'strlist' = []

        for section in deferred_sections:
            if section in self.deletions:
                sections.append(section)

        if not sections:
            return

        self._run_sections(sections, session, server_dir)
        self._log_processed(sections)

# ################################################################################################################################
# ################################################################################################################################
