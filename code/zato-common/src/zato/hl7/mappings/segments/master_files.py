# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import cast_
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.segments.common import append_to_list_field, preserve_other_components, preserve_unmapped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_MFI_Handled = frozenset({1, 3})
_MFE_Handled = frozenset({1, 4})

# The extensions the master file frame becomes on the MessageHeader
_Master_File_Extension       = 'master-file'
_Master_File_Event_Extension = 'master-file-event'

# The table the MFE-1 record-level event codes - MAD, MUP, MDL and the like - come from
_Record_Event_System = 'http://terminology.hl7.org/CodeSystem/v2-0180'

# Which component of the MFE-4 primary key is the value itself, the rest depends on the key's type.
_Primary_Key_Component = 1
_Primary_Key_Consumed  = frozenset({_Primary_Key_Component})

# ################################################################################################################################
# ################################################################################################################################

def _add_coded_extension(
    accessor:'SegmentAccessor',
    position:'int',
    name:'str',
    message_header:'any_',
    context:'ConversionContext',
    ) -> 'None':
    """ Adds one coded MFI field to the MessageHeader as an extension.
    """
    config = context.config

    # A field that carries no concept adds no extension.
    repetition = accessor.first(position)

    if concept := cwe_to_codeable_concept(repetition, config):
        base_url = config.extension_base_url
        url = f'{base_url}/{name}'
        extension = {'url': url, 'valueCodeableConcept': concept}

        append_to_list_field(message_header, 'extension', extension)

# ################################################################################################################################

def apply_mfi(accessor:'SegmentAccessor', context:'ConversionContext', message_header:'any_') -> 'None':
    """ Applies MFI - the master file identification - to the MessageHeader. The master file
    and the file-level event become extensions, the rest of the frame is preserved as-is.
    """
    _add_coded_extension(accessor, 1, _Master_File_Extension, message_header, context)
    _add_coded_extension(accessor, 3, _Master_File_Event_Extension, message_header, context)

    preserve_unmapped(accessor, _MFI_Handled, message_header, context)

# ################################################################################################################################

def apply_mfe(accessor:'SegmentAccessor', context:'ConversionContext', resource:'any_') -> 'None':
    """ Applies MFE - the master file entry - to the resource its group built. The record-level event
    becomes a meta tag and the primary key an identifier, the rest of the entry is preserved as-is.
    """
    config = context.config

    # The record event tags the resource ..
    event_repetition = accessor.first(1)

    if event := cwe_to_codeable_concept(event_repetition, config):
        codings = event['coding']
        tag:'stranydict' = codings[0]

        # The table is known even when the field does not name it.
        if 'system' not in tag:
            tag['system'] = _Record_Event_System

        current = resource.to_dict()

        meta:'stranydict' = {}
        tags:'anylist' = []

        # .. a resource that already carries tags keeps them, the new one joining the rest ..
        if existing_meta := current.get('meta'):
            meta = cast_('stranydict', existing_meta)

            if existing_tags := meta.get('tag'):
                tags = cast_('anylist', existing_tags)

        tags.append(tag)
        meta['tag'] = tags

        resource.meta = meta

    # .. and the primary key identifies it, whatever else the key carries is preserved.
    primary_key = accessor.component(4, _Primary_Key_Component)

    if primary_key:
        identifier = {'value': primary_key}
        append_to_list_field(resource, 'identifier', identifier)
        preserve_other_components(accessor, 4, _Primary_Key_Consumed, resource, context)

    preserve_unmapped(accessor, _MFE_Handled, resource, context)

# ################################################################################################################################
# ################################################################################################################################
