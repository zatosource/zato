# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from shutil import copytree

# pytest
import pytest

# Zato
from zato.common.alerting.rendering import get_default_template_dir, render_alert_template, template_names, \
    Template_Digest_Body, Template_Digest_Subject, Template_Email_Body, Template_Email_Subject, Template_Slack, \
    Template_Teams, Template_Webhook, Template_Dir_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import stranydict
    Path = Path
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The alert the templates render - the message and the audit log link every transport carries
_message = '[3x] REST outgoing connection billing.api is failing - 3 failures in a row in the last 5 minutes'
_link = 'https://dashboard.example.com/zato/audit-log/?object=billing.api'

# What a diagnosed alert adds to the context
_diagnosis = 'The remote endpoint answers with HTTP 503 - the service behind it is restarting'
_confidence = 'high'
_remediation = 'Wait for the restart to finish, then resubmit the failed calls'

# ################################################################################################################################

def _context() -> 'stranydict':
    """ The full template context of one undiagnosed alert.
    """
    out = {
        'alert_id': 1234,
        'rule': 'alerts_rest_Connection_Down',
        'kind': 'Connection_Down',
        'source': 'rest-outgoing',
        'object_name': 'billing.api',
        'message': _message,
        'link': _link,
        'severity': 'warning',
        'count': 3,
        'action_config': {},
        'diagnosis': '',
        'confidence': '',
        'remediation': None,
    }

    return out

# ################################################################################################################################

def _diagnosed_context() -> 'stranydict':
    """ The same alert once the LLM's diagnosis is attached.
    """
    out = _context()
    out['diagnosis'] = _diagnosis
    out['confidence'] = _confidence
    out['remediation'] = _remediation

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def template_dir(tmp_path:'Path') -> 'str':
    """ The templates as one server holds them - the shipped directory copied
    whole to the server's own location, exactly the way create_server.py copies it.
    """
    out = os.path.join(tmp_path, Template_Dir_Name)
    _ = copytree(get_default_template_dir(), out)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestShippedTemplates:

    def test_the_copy_carries_every_template(self, template_dir:'str') -> 'None':

        for name in template_names:
            path = os.path.join(template_dir, name + '.j2')
            assert os.path.exists(path), path

# ################################################################################################################################

    def test_slack_says_the_message_and_the_link(self, template_dir:'str') -> 'None':

        text = render_alert_template(Template_Slack, _context(), template_dir)

        assert text == f'{_message}\n{_link}'

# ################################################################################################################################

    def test_slack_without_a_link_is_just_the_message(self, template_dir:'str') -> 'None':

        context = _context()
        context['link'] = ''

        text = render_alert_template(Template_Slack, context, template_dir)

        assert text == _message

# ################################################################################################################################

    def test_teams_puts_a_blank_line_before_the_link(self, template_dir:'str') -> 'None':

        text = render_alert_template(Template_Teams, _context(), template_dir)

        assert text == f'{_message}\n\n{_link}'

# ################################################################################################################################

    def test_the_email_subject_is_the_message(self, template_dir:'str') -> 'None':

        subject = render_alert_template(Template_Email_Subject, _context(), template_dir)

        assert subject == _message

# ################################################################################################################################

    def test_the_email_body_is_the_message_and_the_link(self, template_dir:'str') -> 'None':

        body = render_alert_template(Template_Email_Body, _context(), template_dir)

        assert body == f'{_message}\n{_link}'

# ################################################################################################################################

    def test_the_digest_counts_its_findings(self, template_dir:'str') -> 'None':

        context = {
            'count': 4,
            'findings': [
                {'message': 'Finding one', 'link': 'https://dashboard.example.com/one'},
                {'message': 'Finding two', 'link': 'https://dashboard.example.com/two'},
                {'message': 'Finding three', 'link': 'https://dashboard.example.com/three'},
                {'message': 'Finding four', 'link': 'https://dashboard.example.com/four'},
            ],
        }

        subject = render_alert_template(Template_Digest_Subject, context, template_dir)
        body = render_alert_template(Template_Digest_Body, context, template_dir)

        assert subject == 'Zato alert digest - 4 findings'

        assert '* Finding one' in body
        assert '  https://dashboard.example.com/one' in body
        assert '* Finding four' in body
        assert '  https://dashboard.example.com/four' in body

# ################################################################################################################################

    def test_a_digest_with_one_finding_speaks_in_the_singular(self, template_dir:'str') -> 'None':

        context = {
            'count': 1,
            'findings': [
                {'message': 'The only finding', 'link': 'https://dashboard.example.com/only'},
            ],
        }

        subject = render_alert_template(Template_Digest_Subject, context, template_dir)

        assert subject == 'Zato alert digest - 1 finding'

# ################################################################################################################################

    def test_the_webhook_renders_the_whole_structured_payload(self, template_dir:'str') -> 'None':

        rendered = render_alert_template(Template_Webhook, _context(), template_dir)
        payload = json.loads(rendered)

        assert payload == {
            'alert_id': 1234,
            'rule': 'alerts_rest_Connection_Down',
            'kind': 'Connection_Down',
            'source': 'rest-outgoing',
            'object_name': 'billing.api',
            'message': _message,
            'link': _link,
            'severity': 'warning',
            'count': 3,
            'action_config': {},
        }

# ################################################################################################################################
# ################################################################################################################################

class TestDiagnosisContext:
    """ An alert with a diagnosis says more - the diagnosis, its confidence and
    the proposed remediation travel through the same templates.
    """

    def test_slack_carries_the_diagnosis_line(self, template_dir:'str') -> 'None':

        text = render_alert_template(Template_Slack, _diagnosed_context(), template_dir)

        assert text == f'{_message}\nDiagnosis ({_confidence}): {_diagnosis}\n{_link}'

# ################################################################################################################################

    def test_teams_carries_the_diagnosis_line(self, template_dir:'str') -> 'None':

        text = render_alert_template(Template_Teams, _diagnosed_context(), template_dir)

        assert text == f'{_message}\n\nDiagnosis ({_confidence}): {_diagnosis}\n\n{_link}'

# ################################################################################################################################

    def test_the_email_body_carries_the_diagnosis_line(self, template_dir:'str') -> 'None':

        body = render_alert_template(Template_Email_Body, _diagnosed_context(), template_dir)

        assert body == f'{_message}\nDiagnosis ({_confidence}): {_diagnosis}\n{_link}'

# ################################################################################################################################

    def test_the_webhook_carries_the_diagnosis_keys(self, template_dir:'str') -> 'None':

        rendered = render_alert_template(Template_Webhook, _diagnosed_context(), template_dir)
        payload = json.loads(rendered)

        assert payload['diagnosis'] == _diagnosis
        assert payload['confidence'] == _confidence
        assert payload['remediation'] == _remediation

# ################################################################################################################################

    def test_an_edited_copy_changes_the_next_alert(self, template_dir:'str') -> 'None':

        # Copied means copied - the server renders from its own files,
        # so an edit there is what the next alert says
        path = os.path.join(template_dir, Template_Slack + '.j2')

        with open(path, 'w') as file_object:
            _ = file_object.write('Edited: {{ message }}\n')

        text = render_alert_template(Template_Slack, _context(), template_dir)

        assert text == f'Edited: {_message}'

# ################################################################################################################################
# ################################################################################################################################
