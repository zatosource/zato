# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# local
import _agent
import _constants
import _enmasse
import _helpers

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The JSON-RPC error message of a prompt the gateway does not serve,
# whether its file is absent or unreadable
_message_not_found = 'Prompt not found'

# The file mode that takes all permissions away from a skill file
_no_access_mode = 0

# ################################################################################################################################
# ################################################################################################################################

def _skill_file_path(zato_server:'anydict', skill_name:'str') -> 'str':
    """ Where one skill's file lives in the server's own repository.
    """

    out = os.path.join(zato_server['server_directory'], 'config', 'repo', 'skills', skill_name, 'SKILL.md')
    return out

# ################################################################################################################################

def _list_prompt_names(zato_server:'anydict') -> 'strlist':
    """ The prompt names the skills gateway lists right now, on a fresh session.
    """

    client = _helpers.make_client(zato_server, _constants.Path_Skills)
    session_id = _helpers.open_session(client)

    response = client.jsonrpc('prompts/list', session_id=session_id)
    prompts = response.json()['result']['prompts']

    out = []

    for prompt in prompts:
        out.append(prompt['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSkillsAsPrompts:
    """ The skills assigned to a gateway are its prompts - advertised in initialize,
    listed by prompts/list and served whole by prompts/get.
    """

# ################################################################################################################################

    def test_prompts_capability_is_advertised_only_with_skills(self, zato_server:'anydict') -> 'None':

        # The skills gateway advertises the prompts capability ..
        skills_client = _helpers.make_client(zato_server, _constants.Path_Skills)
        response = _helpers.initialize_response(skills_client)

        capabilities = response.json()['result']['capabilities']
        assert 'prompts' in capabilities, capabilities

        # .. and a gateway without skills does not.
        main_client = _helpers.make_client(zato_server, _constants.Path_Main)
        response = _helpers.initialize_response(main_client)

        capabilities = response.json()['result']['capabilities']
        assert 'prompts' not in capabilities, capabilities

# ################################################################################################################################

    def test_prompts_list_names_exactly_the_assigned_skills(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        response = client.jsonrpc('prompts/list', session_id=session_id)
        prompts = response.json()['result']['prompts']

        prompt_names = []

        for prompt in prompts:
            prompt_names.append(prompt['name'])

        assert prompt_names == [_constants.Skill_House_Style], prompt_names

# ################################################################################################################################

    def test_prompts_get_returns_the_skill_content(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        params = {'name': _constants.Skill_House_Style}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        result = response.json()['result']

        # The instructions travel as the one message of the prompt
        # and carry the marker phrase the skill mandates.
        message = result['messages'][0]
        instructions = message['content']['text']

        assert _constants.Skill_Marker in instructions, instructions

# ################################################################################################################################

    def test_unassigned_skills_stay_invisible(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        # The skill exists on disk but is assigned to no gateway, so it is not listed ..
        response = client.jsonrpc('prompts/list', session_id=session_id)
        prompts = response.json()['result']['prompts']

        prompt_names = []

        for prompt in prompts:
            prompt_names.append(prompt['name'])

        assert _constants.Skill_Unassigned not in prompt_names, prompt_names

        # .. and reading it directly is invalid params.
        params = {'name': _constants.Skill_Unassigned}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        body = response.json()
        assert body['error']['code'] == _constants.Error_Invalid_Params, body

# ################################################################################################################################

    def test_a_prompt_name_with_line_breaks_renders_on_one_log_line(self, zato_server:'anydict') -> 'None':

        server_log_path = zato_server['server_log_path']
        log_offset = os.path.getsize(server_log_path)

        client = _helpers.make_client(zato_server, _constants.Path_Skills)
        session_id = _helpers.open_session(client)

        # The prompt name carries line breaks and a distinctive trailer ..
        trailer = 'crm.note.' + rand_string()
        prompt_name = f'crm-house-style\r\n{trailer}'

        params = {'name': prompt_name}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        # .. the refusal is the same one an absent prompt gets ..
        body = response.json()
        assert body['error']['code'] == _constants.Error_Invalid_Params, body
        assert body['error']['message'] == _message_not_found, body

        # .. and in the server log the name sits inside the refusal's own line -
        # the trailer never opens a line of its own.
        new_log_text = _helpers.read_new_log_text(server_log_path, log_offset)
        assert trailer in new_log_text, new_log_text

        for line in new_log_text.splitlines():
            if trailer in line:
                assert 'Prompt not found' in line, line

# ################################################################################################################################
# ################################################################################################################################

class TestSkillUseByLLM:
    """ Behavioral proof the skill is used - the same task produces the mandated format
    only when the skill's instructions are in the conversation.
    """

# ################################################################################################################################

    def test_the_skill_shapes_the_answer_only_when_present(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Skills)

        # The skill's instructions come off the gateway itself, the way a real host reads them
        session_id = _helpers.open_session(client)

        params = {'name': _constants.Skill_House_Style}
        response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

        instructions = response.json()['result']['messages'][0]['content']['text']

        task = f'What is the name and city of customer {_constants.Customer_ID}? Use the tools.'

        # With the skill in the conversation, the answer carries the mandated marker ..
        with_skill = _agent.run_agent(client, task, system_text=instructions)
        assert _helpers.text_contains(with_skill.final_text, _constants.Skill_Marker), with_skill.final_text

        # .. and without it, the marker never appears - the model has no way to know it.
        without_skill = _agent.run_agent(client, task)
        assert not _helpers.text_contains(without_skill.final_text, _constants.Skill_Marker), without_skill.final_text

        # Both runs answered the actual question, so the difference is the format alone.
        assert _helpers.text_contains(with_skill.final_text, _constants.Customer_Name), with_skill.final_text
        assert _helpers.text_contains(without_skill.final_text, _constants.Customer_Name), without_skill.final_text

# ################################################################################################################################
# ################################################################################################################################

class TestSkillStorageFailure:
    """ A skill file the process cannot read drops out of the listing and answers
    prompts/get the same way an absent one does, while the other skills keep serving.
    """

# ################################################################################################################################

    def test_an_unreadable_skill_file_answers_as_an_absent_one(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        skill_path = _skill_file_path(zato_server, _constants.Skill_Unassigned)
        original_mode = os.stat(skill_path).st_mode

        try:
            # Both skills are assigned and served first ..
            skills = [_constants.Skill_House_Style, _constants.Skill_Unassigned]
            overrides = {_constants.Gateway_Skills: {'skills': skills}}

            config = _enmasse.build_suite_config(gateway_overrides=overrides)
            _enmasse.run_import(server_directory, config)

            def both_are_listed() -> 'bool':
                out = _constants.Skill_Unassigned in _list_prompt_names(zato_server)
                return out

            _helpers.wait_until(both_are_listed, 'both skills are listed')

            # .. the file stays on disk but its read permissions are gone ..
            os.chmod(skill_path, _no_access_mode)

            # .. prompts/list drops the unreadable line and keeps the readable one -
            # which is also how the other skill proves it keeps serving the listing ..
            names = _list_prompt_names(zato_server)
            assert names == [_constants.Skill_House_Style], names

            client = _helpers.make_client(zato_server, _constants.Path_Skills)
            session_id = _helpers.open_session(client)

            # .. prompts/get refuses the unreadable skill exactly the way it refuses
            # an absent one - the client cannot tell the two apart ..
            params = {'name': _constants.Skill_Unassigned}
            response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

            body = response.json()
            assert body['error']['code'] == _constants.Error_Invalid_Params, body
            assert body['error']['message'] == _message_not_found, body

            # .. the readable skill serves whole all along ..
            params = {'name': _constants.Skill_House_Style}
            response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

            instructions = response.json()['result']['messages'][0]['content']['text']
            assert _constants.Skill_Marker in instructions, instructions

            # .. and restored permissions serve the skill again - no restart, no re-import.
            os.chmod(skill_path, original_mode)

            params = {'name': _constants.Skill_Unassigned}
            response = client.jsonrpc('prompts/get', params=params, session_id=session_id)

            assert response.json()['result']['messages'], response.text

        finally:
            # The permissions and the baseline assignment always come back for the other tests.
            os.chmod(skill_path, original_mode)

            config = _enmasse.build_suite_config()
            _enmasse.run_import(server_directory, config)

            def extra_skill_is_gone() -> 'bool':
                out = _constants.Skill_Unassigned not in _list_prompt_names(zato_server)
                return out

            _helpers.wait_until(extra_skill_is_gone, 'the baseline skills list is back')

# ################################################################################################################################
# ################################################################################################################################
