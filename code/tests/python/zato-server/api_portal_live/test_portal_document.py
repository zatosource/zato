# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The document the portal receives from a server whose services were deployed at startup - after the first start
# with the channels imported once the server was up, after a restart, and with one operation per channel method.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import PortalSuite

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Cases_Path = '/api/cases'
    Case_Path = '/api/cases/{case_id}'
    Expected_Paths = sorted([Cases_Path, Case_Path])

    Later_Channel_Path = '/api/cases/bulk'
    Later_Channel_File = 'channels_later.yaml'
    Later_Channel_Definitions = """
channel_rest:
  - name: api.cases.create.bulk
    service: api.cases.create
    url_path: /api/cases/bulk
    method: POST
    data_format: json
    should_include_in_openapi: true
"""

# ################################################################################################################################
# ################################################################################################################################

def _assert_all_paths(suite:'PortalSuite') -> 'None':
    """ Every channel of the suite is in the document.
    """
    document = suite.get_document()
    paths = sorted(document['paths'])

    assert paths == ModuleCtx.Expected_Paths

# ################################################################################################################################
# ################################################################################################################################

def test_document_after_first_start(portal_suite:'PortalSuite') -> 'None':
    _ = portal_suite.server_log_lines('Deployed user service')
    _ = portal_suite.server_log_lines('OpenAPI')

    _assert_all_paths(portal_suite)

# ################################################################################################################################

def test_document_after_restart(portal_suite:'PortalSuite') -> 'None':
    portal_suite.restart()

    _ = portal_suite.server_log_lines('Deployed user service')
    _ = portal_suite.server_log_lines('OpenAPI')

    _assert_all_paths(portal_suite)

# ################################################################################################################################

def test_one_operation_per_channel_method(portal_suite:'PortalSuite') -> 'None':
    document = portal_suite.get_document()
    paths = document['paths']

    # Two channels on one path, each with a method of its own, are two operations ..
    cases_methods = sorted(paths[ModuleCtx.Cases_Path])
    assert cases_methods == ['patch', 'post']

    # .. and a channel accepting any method documents the methods its service has handlers for.
    case_methods = sorted(paths[ModuleCtx.Case_Path])
    assert case_methods == ['get']

# ################################################################################################################################

def test_document_after_import_without_hot_deployment(portal_suite:'PortalSuite') -> 'None':
    portal_suite.import_channels(ModuleCtx.Later_Channel_File, ModuleCtx.Later_Channel_Definitions)

    _ = portal_suite.server_log_lines('Config loaded OK')
    _ = portal_suite.server_log_lines('OpenAPI')

    # A channel imported into a running server is in the document with no hot-deployment in between
    document = portal_suite.get_document()
    paths = document['paths']

    assert ModuleCtx.Later_Channel_Path in paths
    assert sorted(paths[ModuleCtx.Later_Channel_Path]) == ['post']

# ################################################################################################################################
# ################################################################################################################################
