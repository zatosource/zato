# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.const import ServiceConst
from zato.server.service import Boolean, Integer, List
from zato.server.service.internal import AdminService, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

output_required = 'id', 'name', 'is_active', 'sec_type'
output_optional:'any_' = 'username', 'realm', 'password_type', Boolean('reject_empty_nonce_creat'), \
    Boolean('reject_stale_tokens'), Integer('reject_expiry_limit'),  Integer('nonce_freshness_time'), 'proto_version', \
        'sig_method', Integer('max_nonce_log')

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a single security definition by its ID.
    """
    class SimpleIO(GetListAdminSIO):
        response_elem = None
        input_required = 'cluster_id', 'id'
        output_required = output_required
        output_optional = output_optional

    def handle(self):
        for item in self.server.config_store.get_list('security'):
            if str(item.get('id')) == str(self.request.input.id):
                out = dict(item)
                if 'sec_type' not in out and out.get('type'):
                    out['sec_type'] = out['type']
                self.response.payload = out
                return

        raise Exception('Security definition with id `{}` not found'.format(self.request.input.id))

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of all security definitions available.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_security_get_list_request'
        response_elem = 'zato_security_get_list_response'
        input_optional = 'cluster_id'
        input_optional:'any_' = GetListAdminSIO.input_optional + (List('sec_type'), Boolean('needs_internal', default=True))
        output_required = output_required
        output_optional = output_optional
        output_repeated = True

    @staticmethod
    def _name_matches_query(name, query_criteria):
        """ Mirrors SQL name.contains per criterion (see zato.common.odb.query._SearchWrapper). """
        name_lower = name.lower()
        for criterion in query_criteria:
            crit = str(criterion)
            if crit.startswith('-'):
                if crit[1:].lower() in name_lower:
                    return False
            else:
                if crit.lower() not in name_lower:
                    return False
        return True

    def handle(self):

        _needs_internal = self.request.input.get('needs_internal') != ''
        _internal = {ServiceConst.API_Admin_Invoke_Username}

        if _needs_internal:
            needs_internal = True if self.request.input.get('needs_internal') is True else False
        else:
            needs_internal = True

        filter_by = self.request.input.get('sec_type', [])
        if filter_by and not isinstance(filter_by, (list, tuple)):
            filter_by = [filter_by]

        query_criteria = self.request.input.get('query')
        if query_criteria:
            query_criteria = query_criteria if isinstance(query_criteria, (list, tuple)) else [query_criteria]
        else:
            query_criteria = []

        items = self.server.config_store.get_list('security')

        for raw in items:
            row = dict(raw)
            st = row.get('sec_type') or row.get('type')
            if st:
                row['sec_type'] = st

            if filter_by and st not in filter_by:
                continue

            name = row.get('name', '') or ''
            if query_criteria and not self._name_matches_query(name, query_criteria):
                continue

            if name.startswith('zato') or name in _internal:
                if not needs_internal:
                    continue

            self.response.payload.append(row)

# ################################################################################################################################
# ################################################################################################################################
