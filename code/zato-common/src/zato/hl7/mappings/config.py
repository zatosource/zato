# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from threading import Lock

# Zato
from zato.common.ext.configobj_ import ConfigObj
from zato.hl7.common import add_config_location, get_config_locations

# Re-exported so that callers can register directories through this module as well
add_config_location = add_config_location

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone, strstrdict
    any_ = any_
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
code_map_dict = dict[str, 'strstrdict']

# ################################################################################################################################
# ################################################################################################################################

# The bundle type produced when the config file does not say otherwise
Default_Bundle_Type = 'transaction'

# The timezone offset applied to DTM values that carry none of their own
Default_Timezone = '+00:00'

# Where Z-segment data goes when the config file does not define its own base URL
Default_Extension_Base_URL = 'urn:zato:hl7v2:extension'

# The prefix identifier systems are derived from when an assigning authority has no configured URI
Authority_URN_Prefix = 'urn:zato:hl7v2:authority:'

# The bundle types a config file may request
Bundle_Types = ('transaction', 'batch', 'collection')

# The file name suffixes a config name is resolved against in the user-conf directories
_config_file_suffixes = ('.ini', '.conf')

# The sections a config file may contain, along with the keys each section allows.
# Sections whose keys are None accept subsections instead of keys.
_allowed_sections = {
    'bundle': ('type',),
    'datetime': ('default_timezone',),
    'identifiers': None,
    'codes': None,
    'extensions': ('base_url',),
}

# The keys an [identifiers] subsection allows
_identifier_keys = ('authority', 'system')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FHIRMappingConfig:
    """ Everything that customizes how an HL7 v2 message converts to a FHIR bundle.
    Built from an .ini file, never constructed by user code directly.
    """

    # What kind of bundle to produce - transaction, batch or collection
    bundle_type: 'str'

    # The offset applied to date/time values that have none of their own, e.g. +02:00
    default_timezone: 'str'

    # Maps assigning authority names to the identifier system URIs they stand for
    identifier_systems: 'strstrdict'

    # Maps vocabulary map names to per-code overrides, e.g. {'patient_class': {'P': 'AMB'}}
    code_mappings: 'code_map_dict'

    # The base URL Z-segment extensions are published under
    extension_base_url: 'str'

# ################################################################################################################################

def _new_config() -> 'FHIRMappingConfig':
    """ Builds a mapping config populated with the constant defaults.
    """
    out = FHIRMappingConfig()
    out.bundle_type = Default_Bundle_Type
    out.default_timezone = Default_Timezone
    out.identifier_systems = {}
    out.code_mappings = {}
    out.extension_base_url = Default_Extension_Base_URL

    return out

# ################################################################################################################################
# ################################################################################################################################

# Parsed configs, keyed by the name or path they were loaded from
_config_cache:'dict[str, FHIRMappingConfig]' = {}

# Serializes access to the cache
_config_lock = Lock()

# The config used when to_fhir is called without any
_default_config = _new_config()

# ################################################################################################################################

def _resolve_name_to_path(name:'str') -> 'str':
    """ Finds the .ini file a config name points to, searching all the registered directories.
    """
    directories = get_config_locations()

    for dir_name in directories:
        for suffix in _config_file_suffixes:
            full_path = os.path.join(dir_name, name + suffix)
            if os.path.isfile(full_path):
                out = full_path
                return out

    # If we are here, the name did not match any file in any directory
    raise Exception(f'HL7-FHIR mapping config `{name}` not found in any of {directories}')

# ################################################################################################################################

def _reject_keys_outside_sections(file_path:'str') -> 'None':
    """ Rejects files whose first real line is a key rather than a section
    - ConfigObj itself cannot parse such files and its error would be opaque.
    """
    with open(file_path) as file_object:
        for line in file_object:
            line = line.strip()

            # Blank lines and comments may come before the first section ..
            if not line:
                continue

            if line.startswith('#') or line.startswith(';'):
                continue

            # .. the first line with content must open a section.
            if not line.startswith('['):
                raise Exception(f'Key `{line}` in `{file_path}` is outside any section')

            return

# ################################################################################################################################

def _validate_sections(parsed:'any_', file_path:'str') -> 'None':
    """ Rejects unknown sections and keys so that typos never pass silently.
    """
    for section_name in parsed.sections:

        # The section itself must be one we know ..
        if section_name not in _allowed_sections:
            allowed = sorted(_allowed_sections)
            raise Exception(f'Unknown section `[{section_name}]` in `{file_path}`, allowed: {allowed}')

        section = parsed[section_name]
        allowed_keys = _allowed_sections[section_name]

        # .. sections with a fixed key list may not contain anything else ..
        if allowed_keys is not None:

            if section.sections:
                first_subsection = section.sections[0]
                raise Exception(f'Section `[{section_name}]` in `{file_path}` does not allow subsections' + \
                    f', found `[[{first_subsection}]]`')

            for key in section.scalars:
                if key not in allowed_keys:
                    raise Exception(f'Unknown key `{key}` in `[{section_name}]` in `{file_path}`, allowed: {list(allowed_keys)}')

        # .. sections built of subsections may not carry loose keys of their own.
        else:
            if section.scalars:
                first_key = section.scalars[0]
                raise Exception(f'Section `[{section_name}]` in `{file_path}` only allows subsections' + \
                    f', found key `{first_key}`')

    # Keys outside any section are never valid
    if parsed.scalars:
        first_key = parsed.scalars[0]
        raise Exception(f'Key `{first_key}` in `{file_path}` is outside any section')

# ################################################################################################################################

def _build_config(parsed:'any_', file_path:'str') -> 'FHIRMappingConfig':
    """ Turns a validated ConfigObj into a mapping config, merging the file over the defaults.
    """

    # Our response to produce
    out = _new_config()

    # The bundle type must be one of the recognized ones ..
    if 'bundle' in parsed:
        bundle_section = parsed['bundle']
        if 'type' in bundle_section:
            bundle_type = bundle_section['type']
            if bundle_type not in Bundle_Types:
                raise Exception(f'Unknown bundle type `{bundle_type}` in `{file_path}`, allowed: {list(Bundle_Types)}')
            out.bundle_type = bundle_type

    # .. the default timezone is taken as-is ..
    if 'datetime' in parsed:
        datetime_section = parsed['datetime']
        if 'default_timezone' in datetime_section:
            out.default_timezone = datetime_section['default_timezone']

    # .. each identifiers subsection maps an assigning authority to a system URI ..
    if 'identifiers' in parsed:
        identifiers_section = parsed['identifiers']

        for subsection_name in identifiers_section.sections:
            subsection = identifiers_section[subsection_name]

            for key in subsection.scalars:
                if key not in _identifier_keys:
                    raise Exception(f'Unknown key `{key}` in `[[{subsection_name}]]` in `{file_path}`' + \
                        f', allowed: {list(_identifier_keys)}')

            if 'authority' not in subsection:
                raise Exception(f'Missing key `authority` in `[[{subsection_name}]]` in `{file_path}`')

            if 'system' not in subsection:
                raise Exception(f'Missing key `system` in `[[{subsection_name}]]` in `{file_path}`')

            authority = subsection['authority']
            system = subsection['system']
            out.identifier_systems[authority] = system

    # .. each codes subsection carries per-code overrides for one vocabulary map ..
    if 'codes' in parsed:
        codes_section = parsed['codes']

        for subsection_name in codes_section.sections:
            subsection = codes_section[subsection_name]
            overrides:'strstrdict' = {}

            for key in subsection.scalars:
                overrides[key] = subsection[key]

            out.code_mappings[subsection_name] = overrides

    # .. and the extension base URL is taken as-is.
    if 'extensions' in parsed:
        extensions_section = parsed['extensions']
        if 'base_url' in extensions_section:
            out.extension_base_url = extensions_section['base_url']

    return out

# ################################################################################################################################

def load_mapping_config(name_or_path:'strnone') -> 'FHIRMappingConfig':
    """ Returns the mapping config for a name or path, loading and caching it on first use.
    A name resolves through the registered user-conf directories, a path loads directly.
    """

    # No config given means the constant defaults apply
    if not name_or_path:
        out = _default_config
        return out

    # Return the cached config if this name or path was already loaded ..
    with _config_lock:
        if name_or_path in _config_cache:

            out = _config_cache[name_or_path]
            return out

    # .. a value that points to an existing file is used directly ..
    if os.path.isfile(name_or_path):
        file_path = name_or_path

    # .. anything else is a name to resolve through the known directories.
    else:
        file_path = _resolve_name_to_path(name_or_path)

    _reject_keys_outside_sections(file_path)

    parsed = ConfigObj(file_path)
    _validate_sections(parsed, file_path)

    out = _build_config(parsed, file_path)

    with _config_lock:
        _config_cache[name_or_path] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
