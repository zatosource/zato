# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_template_name = 'zato/service/config-tables.html'

# A table whose file is bigger than this is worked on outside the dashboard - downloaded,
# changed and uploaded again - rather than in the browser.
_max_editable_size = 256 * 1024

# Where the files live
_user_conf_directory = './config/repo/user-conf/'

# ################################################################################################################################
# ################################################################################################################################

_loinc_content = """[codes]
2951-2 = Sodium [Moles/volume] in Serum or Plasma
2823-3 = Potassium [Moles/volume] in Serum or Plasma
1988-5 = C reactive protein [Mass/volume] in Serum or Plasma
718-7 = Hemoglobin [Mass/volume] in Blood
789-8 = Erythrocytes [#/volume] in Blood by Automated count
"""

_error_codes_content = """[codes]
100 = Segment sequence error
101 = Required field missing
102 = Data type error
103 = Table value not found
200 = Unsupported message type
207 = Application internal error
"""

_acme_lab_content = """[ACME_LAB]
CRP = 1988-5
NA = 2951-2
K = 2823-3
HGB = 718-7

[CITY_HOSPITAL]
SODIUM = 2951-2
POTASSIUM = 2823-3
"""

# ################################################################################################################################
# ################################################################################################################################

def _build_table(
    name:'str',
    file_name:'str',
    directory:'str',
    kind:'str',
    content:'str',
    section_count:'int',
    entry_count:'int',
    ) -> 'anydict':
    """ One config table as the page reads it - what it is called, where its file is
    and what it holds, plus the file itself when it is small enough to be edited in place.
    """
    size = len(content)
    is_editable = size <= _max_editable_size

    out = {
        'name': name,
        'file_name': file_name,
        'directory': directory,
        'path': directory + file_name,
        'kind': kind,
        'section_count': section_count,
        'entry_count': entry_count,
        'size': size,
        'is_editable': is_editable,
        'content': content,
    }

    return out

# ################################################################################################################################

def _get_table_list() -> 'anylist':
    """ The tables the page shows. The shape is what the service behind the page will answer with,
    so only where the list comes from changes once that service is in place.
    """
    out:'anylist' = []

    out.append(_build_table('loinc', 'loinc.ini', _user_conf_directory, 'codes', _loinc_content, 1, 5))
    out.append(_build_table('error-codes', 'error-codes.ini', _user_conf_directory, 'codes', _error_codes_content, 1, 6))
    out.append(_build_table('acme-lab', 'acme-lab.ini', _user_conf_directory, 'mappings', _acme_lab_content, 2, 6))

    return out

# ################################################################################################################################

def _get_directory_list() -> 'anylist':
    """ The directories a file may be put into, as the server reports them - a file is
    uploaded into one of these and into nothing else.
    """
    out:'anylist' = [_user_conf_directory]
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The config tables of the current cluster - one is picked at a time and everything
    about it reads off its own line.
    """
    table_list = _get_table_list()
    directory_list = _get_directory_list()

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'table_list_json': dumps(table_list),
        'directory_list_json': dumps(directory_list),
        'user_conf_directory': _user_conf_directory,
        'max_editable_size': _max_editable_size,
        'zato_clusters': True,
        'zato_template_name': _template_name,
    }

    out = TemplateResponse(req, _template_name, return_data)
    return out

# ################################################################################################################################
# ################################################################################################################################
