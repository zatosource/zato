# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import NOT_FOUND, OK

# local
import _constants
import _enmasse
import _helpers
from _helpers import wait_until as _wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _client import MCPClient
    from zato.common.typing_ import anydict, strlist

    MCPClient = MCPClient

# ################################################################################################################################
# ################################################################################################################################

# Where the lifecycle gateway moves to for the duration of the url_path test
_moved_path = '/mcp/llm/lifecycle-moved'

# What the docstring probe advertises before and after its docstring-only redeploy
_docstring_first = 'Reports the CRM fingerprint of the first build.'
_docstring_redeployed = 'Reports the CRM fingerprint after the docstring redeploy.'

# The line the on-disk skill edit appends and the line the fixture always carries
_skill_edit_marker = 'Edited-on-disk marker line.'

# ################################################################################################################################
# ################################################################################################################################

def _list_prompt_names(client:'MCPClient', session_id:'str') -> 'strlist':
    """ The names one prompts/list request returns.
    """

    response = client.jsonrpc('prompts/list', session_id=session_id)
    prompts = response.json()['result']['prompts']

    out:'strlist' = []

    for prompt in prompts:
        out.append(prompt['name'])

    return out

# ################################################################################################################################

def _get_prompt_body(client:'MCPClient', session_id:'str', name:'str') -> 'anydict':
    """ The whole JSON-RPC response body of one prompts/get request.
    """

    params = {'name': name}
    response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

    out = response.json()
    return out

# ################################################################################################################################

def _get_tool_descriptions(zato_server:'anydict', url_path:'str') -> 'anydict':
    """ The advertised descriptions of one gateway's tools, keyed by tool name,
    read on a fresh session.
    """

    client = _helpers.make_client(zato_server, url_path)
    session_id = _helpers.open_session(client)

    tools = _helpers.list_tools(client, session_id)

    out:'anydict' = {}

    for tool in tools:
        out[tool['name']] = tool['description']

    return out

# ################################################################################################################################

def _skill_file_path(zato_server:'anydict', skill_name:'str') -> 'str':
    """ Where one skill's file lives in the server's own repository.
    """

    out = os.path.join(zato_server['server_directory'], 'config', 'repo', 'skills', skill_name, 'SKILL.md')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayComposition:
    """ What a gateway serves and admits, changing live - the URL path, the services list,
    the skills list, the security groups, the advertised docstrings and the skills
    as they are on disk.
    """

# ################################################################################################################################

    def test_a_url_path_change_moves_the_endpoint(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        old_client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)
        new_client = _helpers.make_client(zato_server, _moved_path)

        # The gateway serves at its own path before the change ..
        response = _helpers.initialize_response(old_client)
        assert response.status_code == OK, response.text

        try:
            # .. one re-import moves it ..
            overrides = {_constants.Gateway_Lifecycle: {'url_path': _moved_path}}
            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. the new path serves ..
            def new_path_serves() -> 'bool':
                response = _helpers.initialize_response(new_client)
                out = response.status_code == OK
                return out

            _wait_until(new_path_serves, 'the moved gateway serves at its new path')

            # .. and the old one is a plain 404 - the companion REST channel moved with it.
            response = _helpers.initialize_response(old_client)
            assert response.status_code == NOT_FOUND, response.text

        finally:
            # The gateway always comes back to its own path for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def old_path_serves() -> 'bool':
                response = _helpers.initialize_response(old_client)
                out = response.status_code == OK
                return out

            _wait_until(old_path_serves, 'the gateway serves at its original path again')

# ################################################################################################################################

    def test_the_services_list_changes_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        def tool_names_now() -> 'strlist':
            client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)
            session_id = _helpers.open_session(client)

            tools = _helpers.list_tools(client, session_id)

            out = _helpers.get_tool_names(tools)
            return out

        # The extra service is not served before the change ..
        assert _constants.Service_Text_Pad not in tool_names_now(), tool_names_now()

        try:
            # .. one re-import adds it ..
            services = [*_constants.Service_List_CRM, _constants.Service_Text_Pad]
            overrides = {_constants.Gateway_Lifecycle: {'services': services}}

            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. it appears in the next tools/list ..
            def tool_is_listed() -> 'bool':
                out = _constants.Service_Text_Pad in tool_names_now()
                return out

            _wait_until(tool_is_listed, 'the added service is listed')

            # .. and it is callable.
            client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)
            session_id = _helpers.open_session(client)

            body = _helpers.call_tool(client, session_id, _constants.Service_Text_Pad, {'count': '1'})

            data = _helpers.get_result_data(body)
            assert data['blocks'], body

        finally:
            # The baseline removes it again for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def tool_is_gone() -> 'bool':
                out = _constants.Service_Text_Pad not in tool_names_now()
                return out

            _wait_until(tool_is_gone, 'the removed service is gone from the listing')

        # A call to the removed service refuses as unknown - no restart anywhere.
        client = _helpers.make_client(zato_server, _constants.Path_Lifecycle)
        session_id = _helpers.open_session(client)

        body = _helpers.call_tool(client, session_id, _constants.Service_Text_Pad, {'count': '1'})
        assert body['error']['code'] == _constants.Error_Method_Not_Found, body

# ################################################################################################################################

    def test_the_skills_list_changes_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        def prompt_names_now() -> 'strlist':
            client = _helpers.make_client(zato_server, _constants.Path_Skills)
            session_id = _helpers.open_session(client)

            out = _list_prompt_names(client, session_id)
            return out

        # The extra skill is not served before the change ..
        assert _constants.Skill_Unassigned not in prompt_names_now(), prompt_names_now()

        try:
            # .. one re-import adds it ..
            skills = [_constants.Skill_House_Style, _constants.Skill_Unassigned]
            overrides = {_constants.Gateway_Skills: {'skills': skills}}

            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. its prompt appears in the next prompts/list ..
            def prompt_is_listed() -> 'bool':
                out = _constants.Skill_Unassigned in prompt_names_now()
                return out

            _wait_until(prompt_is_listed, 'the added skill is listed')

            # .. and it is readable.
            client = _helpers.make_client(zato_server, _constants.Path_Skills)
            session_id = _helpers.open_session(client)

            body = _get_prompt_body(client, session_id, _constants.Skill_Unassigned)
            assert body['result']['messages'], body

        finally:
            # The baseline removes it again for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def prompt_is_gone() -> 'bool':
                out = _constants.Skill_Unassigned not in prompt_names_now()
                return out

            _wait_until(prompt_is_gone, 'the removed skill is gone from the listing')

        # Reading the removed skill refuses.
        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        body = _get_prompt_body(client, session_id, _constants.Skill_Unassigned)
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

# ################################################################################################################################

    def test_a_security_definition_is_added_live(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        # The C gateway admits only its own bearer token, so the main basic
        # credentials are refused before the change ..
        client = _helpers.make_client(zato_server, _constants.Path_Iso_C)

        response = _helpers.initialize_response(client)
        assert response.status_code != OK, response.text

        try:
            # .. one re-import adds the group the basic credentials belong to ..
            groups = [_constants.Group_Iso_C, _constants.Group_Iso_A]
            overrides = {_constants.Gateway_Iso_C: {'security_groups': groups}}

            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            # .. and the credentials are admitted on the very next call.
            def credentials_admitted() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code == OK
                return out

            _wait_until(credentials_admitted, 'the added definition admits its credentials')

        finally:
            # The baseline narrows the gateway back down for the other tests.
            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def credentials_refused() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code != OK
                return out

            _wait_until(credentials_refused, 'the removed definition is refused again')

# ################################################################################################################################

    def test_the_docstring_is_the_description_over_the_wire(self, zato_server:'anydict') -> 'None':

        # The advertised description is the docstring stripped ..
        descriptions = _get_tool_descriptions(zato_server, _constants.Path_Docstring)
        assert descriptions[_constants.Service_Docstring_Probe] == _docstring_first, descriptions

        # .. a service without a docstring advertises an empty description ..
        assert descriptions[_constants.Service_Blank_Probe] == '', descriptions

        # .. and a hot redeploy with a changed docstring updates the advertised text.
        fixtures_directory = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
        probe_path = os.path.join(fixtures_directory, 'crm_docstring.py')

        with open(probe_path) as probe_file:
            probe_source = probe_file.read()

        probe_source = probe_source.replace(_docstring_first, _docstring_redeployed)

        pickup_path = os.path.join(zato_server['pickup_directory'], 'crm_docstring.py')

        with open(pickup_path, 'w') as pickup_file:
            _ = pickup_file.write(probe_source)

        def description_is_updated() -> 'bool':
            descriptions = _get_tool_descriptions(zato_server, _constants.Path_Docstring)

            out = descriptions[_constants.Service_Docstring_Probe] == _docstring_redeployed
            return out

        _wait_until(description_is_updated, 'the redeployed docstring is advertised')

# ################################################################################################################################

    def test_a_skill_edited_on_disk_serves_its_new_content(self, zato_server:'anydict') -> 'None':

        skill_path = _skill_file_path(zato_server, _constants.Skill_House_Style)

        with open(skill_path) as skill_file:
            original_content = skill_file.read()

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        # The marker is not served before the edit ..
        body = _get_prompt_body(client, session_id, _constants.Skill_House_Style)

        instructions = body['result']['messages'][0]['content']['text']
        assert _skill_edit_marker not in instructions, instructions

        try:
            # .. the file is edited on disk, nothing else happens anywhere ..
            with open(skill_path, 'w') as skill_file:
                _ = skill_file.write(original_content + '\n' + _skill_edit_marker + '\n')

            # .. and the very next read serves the new content - no restart, no re-import.
            body = _get_prompt_body(client, session_id, _constants.Skill_House_Style)

            instructions = body['result']['messages'][0]['content']['text']
            assert _skill_edit_marker in instructions, instructions

        finally:
            # The file always goes back to its fixture content for the other tests.
            with open(skill_path, 'w') as skill_file:
                _ = skill_file.write(original_content)

# ################################################################################################################################

    def test_a_skill_file_removed_from_disk_has_a_defined_outcome(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        skill_path = _skill_file_path(zato_server, _constants.Skill_Unassigned)
        aside_path = skill_path + '.aside'

        def prompt_names_now() -> 'strlist':
            client = _helpers.make_client(zato_server, _constants.Path_Skills)
            session_id = _helpers.open_session(client)

            out = _list_prompt_names(client, session_id)
            return out

        try:
            # Both skills are assigned and served first ..
            skills = [_constants.Skill_House_Style, _constants.Skill_Unassigned]
            overrides = {_constants.Gateway_Skills: {'skills': skills}}

            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def both_are_listed() -> 'bool':
                out = _constants.Skill_Unassigned in prompt_names_now()
                return out

            _wait_until(both_are_listed, 'both skills are listed')

            # .. the file disappears from disk while the skill stays assigned ..
            os.rename(skill_path, aside_path)

            client = _helpers.make_client(zato_server, _constants.Path_Skills)
            session_id = _helpers.open_session(client)

            # .. prompts/list drops the line for the missing file ..
            names = _list_prompt_names(client, session_id)
            assert _constants.Skill_Unassigned not in names, names

            # .. prompts/get refuses it cleanly ..
            body = _get_prompt_body(client, session_id, _constants.Skill_Unassigned)
            assert body['error']['code'] == _constants.Error_Invalid_Params, body

            # .. and the gateway's other skill keeps serving.
            body = _get_prompt_body(client, session_id, _constants.Skill_House_Style)

            instructions = body['result']['messages'][0]['content']['text']
            assert _constants.Skill_Marker in instructions, instructions

        finally:
            # The file and the baseline assignment always come back for the other tests.
            if os.path.isfile(aside_path):
                os.rename(aside_path, skill_path)

            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def extra_skill_is_gone() -> 'bool':
                out = _constants.Skill_Unassigned not in prompt_names_now()
                return out

            _wait_until(extra_skill_is_gone, 'the baseline skills list is back')

# ################################################################################################################################
# ################################################################################################################################
