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
    from zato.common.typing_ import any_, anylist, stranydict, strlist, strstrdict
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# All the deterministic resource UUIDs derive from this namespace
_uuid_namespace = uuid5(NAMESPACE_URL, 'urn:zato:hl7v2:to-fhir')

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

        # Maps each added resource's id() to its urn:uuid full URL
        self._full_urls:'dict[int, str]' = {}

        # Maps content keys to full URLs so identical resources collapse into one
        self._dedup:'strstrdict' = {}

        # Everything the conversion could not map, one entry per field or segment
        self.warnings:'strlist' = []

        # References to the resources segment mappers need to point at
        self.patient_reference:'stranydict | None' = None
        self.encounter_reference:'stranydict | None' = None

# ################################################################################################################################

    def warn(self, text:'str') -> 'None':
        """ Records one thing the conversion could not map.
        """
        self.warnings.append(text)

# ################################################################################################################################

    def add(self, resource:'any_') -> 'stranydict':
        """ Adds a resource to the bundle and returns a reference to it.
        Resources whose content is identical to one already added are deduplicated -
        the reference points at the resource added first.
        """

        # The content key is the resource serialized in a stable order ..
        content = resource.to_dict()
        resource_type = content['resourceType']
        content_key = resource_type + '|' + json.dumps(content, sort_keys=True)

        # .. identical content means this entity is already in the bundle ..
        if content_key in self._dedup:

            out = {'reference': self._dedup[content_key]}
            return out

        # .. otherwise the key derives the resource's stable bundle-internal URL ..
        content_uuid = uuid5(_uuid_namespace, content_key)
        full_url = f'urn:uuid:{content_uuid}'

        self.resources.append(resource)
        self._full_urls[id(resource)] = full_url
        self._dedup[content_key] = full_url

        out = {'reference': full_url}
        return out

# ################################################################################################################################

    def reference(self, resource:'any_') -> 'stranydict':
        """ Returns a reference to a resource that was already added.
        """
        full_url = self._full_urls[id(resource)]

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
            full_url = self._full_urls[id(resource)]
            _ = builder.create(resource, full_url=full_url)

        out = builder.build()

        # .. while a collection bundle carries the resources as-is, without any requests.
        if bundle_type == 'collection':
            out.type_ = 'collection'

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
