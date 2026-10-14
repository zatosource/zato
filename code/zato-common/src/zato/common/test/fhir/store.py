# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from datetime import datetime, timezone
from email.utils import formatdate
from typing import NamedTuple
from uuid import uuid4

# Zato
from zato.common.test.fhir.search import matches

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# A list of consecutive versions of one resource, oldest first
version_list = list['stranydict']

# Maps 'Type/id' keys to the version history of that resource
version_dict = dict[str, version_list]

# A list of resources matched by a search
resource_list = list['stranydict']

# Search parameters as a list of name/value pairs
search_parameter_list = list[tuple[str, str]]

# ################################################################################################################################
# ################################################################################################################################

# The version ID assigned to the first version of each resource
first_version_id = '1'

# ################################################################################################################################
# ################################################################################################################################

class ReadResult(NamedTuple):
    """ What the store returns for a read - the resource is None if it never existed.
    """
    resource: 'stranydict | None'
    is_deleted: bool

# ################################################################################################################################
# ################################################################################################################################

def utc_now_instant() -> 'str':
    """ Returns the current UTC time as a FHIR instant, e.g. 2026-07-04T13:33:12.123456+00:00.
    """
    now = datetime.now(timezone.utc)

    out = now.isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRStore:
    """ A thread-safe, in-memory, versioned store of FHIR resources.
    """
    def __init__(self) -> 'None':

        # Maps 'Type/id' to the list of all versions of that resource, oldest first
        self._versions:'version_dict' = {}

        # Keys of resources that have been deleted - reads return 410 Gone for them
        self._deleted:'strset' = set()

        # Maps 'Type/id' to the HTTP-date of its last modification, for the Last-Modified header
        self._last_modified:'strstrdict' = {}

        # Serializes all access to the dictionaries above
        self._lock = threading.Lock()

# ################################################################################################################################

    def _store_version(self, key:'str', resource:'stranydict', version_id:'str') -> 'None':
        """ Appends a new version of a resource under the given key. Must be called under self._lock.
        """

        # Each stored version carries its own metadata, as the spec requires ..
        meta = resource.setdefault('meta', {})
        meta['versionId'] = version_id
        meta['lastUpdated'] = utc_now_instant()

        # .. append it to the history ..
        versions = self._versions.setdefault(key, [])
        versions.append(resource)

        # .. remember when it was modified, for the Last-Modified header ..
        self._last_modified[key] = formatdate(usegmt=True)

        # .. and make sure the resource is not considered deleted anymore.
        self._deleted.discard(key)

# ################################################################################################################################

    def create(self, resource_type:'str', resource:'stranydict') -> 'stranydict':
        """ Creates a new resource, assigning it a server-side ID, per the spec's create interaction.
        """

        # The server ignores any client-supplied ID on create, as the spec recommends
        resource_id = uuid4().hex
        resource['id'] = resource_id

        key = f'{resource_type}/{resource_id}'

        with self._lock:
            self._store_version(key, resource, first_version_id)

        return resource

# ################################################################################################################################

    def put(self, resource_type:'str', resource_id:'str', resource:'stranydict') -> 'bool':
        """ Updates a resource, or creates it if it does not exist yet (update-as-create).
        Returns True if the resource was created rather than updated.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            # A deleted resource is brought back by an update, continuing its version history ..
            versions = self._versions.get(key)

            # .. if there is no history at all, this is update-as-create ..
            if not versions:
                self._store_version(key, resource, first_version_id)
                out = True
                return out

            # .. otherwise, the new version continues the sequence.
            latest = versions[-1]
            latest_version_id = latest['meta']['versionId']
            new_version_id = str(int(latest_version_id) + 1)

            was_deleted = key in self._deleted
            self._store_version(key, resource, new_version_id)

            out = was_deleted
            return out

# ################################################################################################################################

    def read(self, resource_type:'str', resource_id:'str') -> 'ReadResult':
        """ Returns the current version of a resource, along with its deletion status.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            # No history means the resource never existed ..
            versions = self._versions.get(key)
            if not versions:
                out = ReadResult(None, False)
                return out

            # .. a deleted resource still has history but reads must say 410 Gone ..
            if key in self._deleted:
                out = ReadResult(None, True)
                return out

            # .. otherwise, the current version is the last one stored.
            out = ReadResult(versions[-1], False)
            return out

# ################################################################################################################################

    def vread(self, resource_type:'str', resource_id:'str', version_id:'str') -> 'stranydict | None':
        """ Returns a specific version of a resource, or None if there is no such version.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            versions = self._versions.get(key)
            if not versions:
                return None

            # Historical versions remain readable even after deletion, per the spec's vread interaction
            for version in versions:
                if version['meta']['versionId'] == version_id:
                    out = version
                    break
            else:
                out = None

            return out

# ################################################################################################################################

    def delete(self, resource_type:'str', resource_id:'str') -> 'bool':
        """ Marks a resource as deleted. Returns False if the resource never existed.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:

            versions = self._versions.get(key)
            if not versions:
                out = False
                return out

            # Deletes are idempotent - deleting an already-deleted resource succeeds too
            self._deleted.add(key)

            out = True
            return out

# ################################################################################################################################

    def get_last_modified(self, resource_type:'str', resource_id:'str') -> 'str':
        """ Returns the HTTP-date of the resource's last modification.
        """
        key = f'{resource_type}/{resource_id}'

        with self._lock:
            out = self._last_modified[key]

        return out

# ################################################################################################################################

    def search(self, resource_type:'str', parameters:'search_parameter_list') -> 'resource_list':
        """ Returns all current, non-deleted resources of the given type that match all the search parameters.
        """
        out:'resource_list' = []

        type_prefix = f'{resource_type}/'

        with self._lock:

            for key, versions in self._versions.items():

                # Only current, non-deleted resources of the requested type take part in searches ..
                if not key.startswith(type_prefix):
                    continue

                if key in self._deleted:
                    continue

                resource = versions[-1]

                # .. and each one must match every search parameter given.
                for name, value in parameters:

                    # Result parameters like _count or _sort do not take part in matching
                    if name.startswith('_'):
                        if name != '_id':
                            continue

                    # Modifiers like name:contains are matched by the base field name
                    field_name = name.split(':')[0]

                    if not matches(resource, field_name, value):
                        break
                else:
                    out.append(resource)

        return out

# ################################################################################################################################

    def import_resource(self, resource:'stranydict') -> 'str':
        """ Stores a resource under its own ID, assigning one if it has none. Returns the ID used.
        """
        resource_type = resource['resourceType']

        # Imported resources keep their spec-assigned IDs so tests can look them up by them
        if resource_id := resource.get('id'):
            pass
        else:
            resource_id = uuid4().hex
            resource['id'] = resource_id

        key = f'{resource_type}/{resource_id}'

        with self._lock:
            self._store_version(key, resource, first_version_id)

        return resource_id

# ################################################################################################################################

    def get_stored_types(self) -> 'strlist':
        """ Returns the sorted list of resource types that have at least one non-deleted resource.
        """
        types:'strset' = set()

        with self._lock:

            for key in self._versions:
                if key in self._deleted:
                    continue

                resource_type = key.split('/')[0]
                types.add(resource_type)

        out = sorted(types)
        return out

# ################################################################################################################################
# ################################################################################################################################
