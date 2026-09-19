# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from importlib import import_module

# Live HL7
from live_hl7.dcm4che_tools.system import DCM4CHETools
from live_hl7.dcm4chee.system import DCM4CHEE
from live_hl7.openelis.system import OpenELIS
from live_hl7.openemr.system import OpenEMR
from live_hl7.openhim.system import OpenHIM
from live_hl7.openmrs.system import OpenMRS
from live_hl7.oscar.system import OSCAR
from live_hl7.sftp.system import SFTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strtuple
    from live_hl7.system import LiveSystem

# ################################################################################################################################
# ################################################################################################################################

system_dict = dict[str, 'LiveSystem']
group_dict  = dict[str, 'strtuple']

# ################################################################################################################################
# ################################################################################################################################

# More systems and groups are taken from this package under Zato_Health_Root when it is set
Extension_Root_Env = 'Zato_Health_Root'
Extension_Dir      = 'live'
Extension_Package  = 'health_live_hl7'

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
    'radiology':  ('dcm4chee', 'openmrs', 'dcm4che_tools'),
    'laboratory': ('sftp', 'openelis', 'openemr', 'oscar'),
    'hie':        ('openhim', 'openmrs'),
    'hospital':   ('dcm4chee',),
}

# ################################################################################################################################
# ################################################################################################################################

def _load_extension() -> 'None':
    """ Adds the systems and groups of the package under Zato_Health_Root when it is set - the package exposes
    systems() returning a name to system dict and groups() returning a name to tuple dict.
    """
    root = os.environ.get(Extension_Root_Env)

    if not root:
        return

    directory = os.path.join(root, Extension_Dir)
    package_directory = os.path.join(directory, Extension_Package)

    if not os.path.isdir(package_directory):
        return

    if directory not in sys.path:
        sys.path.insert(0, directory)

    extension = import_module(Extension_Package)

    _systems.update(extension.systems())
    _groups.update(extension.groups())

# ################################################################################################################################

_load_extension()

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
