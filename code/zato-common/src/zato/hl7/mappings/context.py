# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from uuid import NAMESPACE_URL, uuid5

# Zato
from zato.fhir.bundle import BatchBuilder, TransactionBuilder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intstrdict, stranydict, strintdict, strlist, strstrdict
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# All the deterministic resource UUIDs derive from this namespace.
_uuid_namespace = uuid5(NAMESPACE_URL, 'urn:zato:hl7v2:to-fhir')

# Only resources that are never mutated after being added may deduplicate by content.
_immutable_resource_types = frozenset({'Practitioner', 'Location', 'Organization', 'Device'})

# ################################################################################################################################
# ################################################################################################################################

class ConversionContext:
    """ Carries everything one message conversion accumulates - the resources produced so far,
    their bundle-internal references, deduplication state and conversion warnings.
    """

    def __init__(self, config:'FHIRMappingConfig') -> 'None':
        self.config = config

        # Every resource that will enter the bundle, in the order it was added
        self.resources:'anylist' = []

        # Maps each added resource's id() to its urn:uuid full URL.
        self._full_urls:'intstrdict' = {}

        # Maps content keys to full URLs so identical resources collapse into one.
        self._dedup:'strstrdict' = {}

        # Counts how many times each content key was added, so non-deduplicated
        # resources with identical initial content still get distinct full URLs.
        self._content_counts:'strintdict' = {}

        # Everything the conversion could not map, one entry per field or segment
        self.warnings:'strlist' = []

        # References to the resources segment mappers need to point at
        self.patient_reference:'stranydict | None' = None
        self.encounter_reference:'stranydict | None' = None

# ################################################################################################################################

    def add(self, resource:'any_') -> 'stranydict':
        """ Adds a resource to the bundle and returns a reference to it.
        Immutable resources whose content is identical to one already added are deduplicated -
        the reference points at the resource added first. Everything else may still be mutated
        after this call, so each occurrence stays a resource of its own, with a distinct URL.
        """

        # The content key is the resource serialized in a stable order ..
        content = resource.to_dict()
        resource_type = content['resourceType']
        content_json = json.dumps(content, sort_keys=True)
        content_key = resource_type + '|' + content_json

        # .. identical content of an immutable resource means this entity is already in the bundle ..
        if resource_type in _immutable_resource_types:
            if existing_url := self._dedup.get(content_key):

                out = {'reference': existing_url}
                return out

        # .. otherwise the key and its occurrence counter derive the resource's stable bundle-internal URL,
        # .. the counter keeping initially identical mutable resources apart.
        occurrence = self._content_counts.get(content_key, 0)
        self._content_counts[content_key] = occurrence + 1

        occurrence_key = f'{content_key}|{occurrence}'
        content_uuid = uuid5(_uuid_namespace, occurrence_key)
        full_url = f'urn:uuid:{content_uuid}'

        resource_id = id(resource)

        self.resources.append(resource)
        self._full_urls[resource_id] = full_url

        if resource_type in _immutable_resource_types:
            self._dedup[content_key] = full_url

        out = {'reference': full_url}
        return out

# ################################################################################################################################

    def build_bundle(self) -> 'any_':
        """ Wraps all the accumulated resources in a bundle of the configured type.
        """
        bundle_type = self.config.bundle_type

        # Transaction and batch bundles get one POST entry per resource ..
        if bundle_type == 'batch':
            builder = BatchBuilder()
        else:
            builder = TransactionBuilder()

        for resource in self.resources:
            resource_id = id(resource)
            full_url = self._full_urls[resource_id]
            _ = builder.create(resource, full_url=full_url)

        out = builder.build()

        # .. while collection and message bundles carry the resources as-is, without any requests.
        if bundle_type in ('collection', 'message'):
            out.type_ = bundle_type

            for entry in out.entry:
                entry.request = None

        return out

# ################################################################################################################################
# ################################################################################################################################

def get_conversion_warnings(bundle:'any_') -> 'strlist':
    """ Returns the warnings a to_fhir conversion attached to its bundle.
    """
    out = bundle._conversion_warnings

    return out

# ################################################################################################################################
# ################################################################################################################################
