# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Re-exports only - the implementation lives in the sibling modules.

# Zato
from zato.admin.web.views.gateway.mcp.common import _alert_field_names, _alert_type, _inline_field_names, \
    _inline_flag_names, _mcp_group_name_prefix, _row_edit_prefix, _shaping_fields, _wizard_template, get_size_cap_label, \
    logger, numeric_from_bool, save_security_group
from zato.admin.web.views.gateway.mcp.export import export
from zato.admin.web.views.gateway.mcp.index import _CreateEdit, Create, Delete, Edit, Index
from zato.admin.web.views.gateway.mcp.lists import get_security_list, get_service_list, get_skill_list
from zato.admin.web.views.gateway.mcp.wizard import _read_gateway, inline_edit, wizard_create, wizard_edit

# ################################################################################################################################
# ################################################################################################################################

# For flake8
_alert_field_names = _alert_field_names
_alert_type = _alert_type
_CreateEdit = _CreateEdit
_inline_field_names = _inline_field_names
_inline_flag_names = _inline_flag_names
_mcp_group_name_prefix = _mcp_group_name_prefix
_read_gateway = _read_gateway
_row_edit_prefix = _row_edit_prefix
_shaping_fields = _shaping_fields
_wizard_template = _wizard_template
Create = Create
Delete = Delete
Edit = Edit
export = export
get_security_list = get_security_list
get_service_list = get_service_list
get_size_cap_label = get_size_cap_label
get_skill_list = get_skill_list
Index = Index
inline_edit = inline_edit
logger = logger
numeric_from_bool = numeric_from_bool
save_security_group = save_security_group
wizard_create = wizard_create
wizard_edit = wizard_edit

# ################################################################################################################################
# ################################################################################################################################
