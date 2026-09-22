# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7.dcm4che_tools.system import DCM4CHETools
from live_hl7.dcm4chee.system import DCM4CHEE
from live_hl7.extension import extension
from live_hl7.openelis.system import OpenELIS
from live_hl7.openemr.system import OpenEMR
from live_hl7.openhim.system import OpenHIM
from live_hl7.openmrs.system import OpenMRS
from live_hl7.oscar.system import OSCAR
from live_hl7.sftp.system import SFTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strset, strtuple
    from live_hl7.system import LiveSystem

# ################################################################################################################################
# ################################################################################################################################

system_dict = dict[str, 'LiveSystem']
group_dict  = dict[str, 'strtuple']

# ################################################################################################################################
# ################################################################################################################################

# The systems this repository carries
_systems:'system_dict' = {
    'dcm4che_tools': DCM4CHETools(),
    'dcm4chee':      DCM4CHEE(),
    'openelis':      OpenELIS(),
    'openemr':       OpenEMR(),
    'openhim':       OpenHIM(),
    'openmrs':       OpenMRS(),
    'oscar':         OSCAR(),
    'sftp':          SFTP(),
}

# The scenario groups, each in the order its systems start
_groups:'group_dict' = {
    'radiology':    ('dcm4chee', 'openmrs', 'dcm4che_tools'),
    'laboratory':   ('sftp', 'openelis', 'openemr', 'oscar'),
    'hie':          ('openhim', 'openmrs'),
    'registration': ('dcm4chee',),
    'lab':          ('openelis',),
}

# ################################################################################################################################
# ################################################################################################################################

# The names of the systems the extension package added
_extension_systems:'strset' = set()

# ################################################################################################################################

def _add_extension() -> 'None':
    """ Adds the systems and groups of the extension package when there is one.
    """
    if extension is None:
        return

    systems = extension.systems()

    _systems.update(systems)
    _groups.update(extension.groups())
    _extension_systems.update(systems)

# ################################################################################################################################

_add_extension()

# ################################################################################################################################
# ################################################################################################################################

def get_system(name:'str') -> 'LiveSystem':
    if system := _systems.get(name):
        return system
    else:
        names = ', '.join(system_names())
        raise Exception(f'Unknown system `{name}`, expected one of: {names}')

# ################################################################################################################################

def system_names() -> 'strlist':
    out = sorted(_systems)
    return out

# ################################################################################################################################

def is_extension_system(name:'str') -> 'bool':
    out = name in _extension_systems
    return out

# ################################################################################################################################

def get_group(name:'str') -> 'strtuple':
    if group := _groups.get(name):
        return group
    else:
        names = ', '.join(group_names())
        raise Exception(f'Unknown group `{name}`, expected one of: {names}')

# ################################################################################################################################

def group_names() -> 'strlist':
    out = sorted(_groups)
    return out

# ################################################################################################################################
# ################################################################################################################################
