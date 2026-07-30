# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import time
from http.client import FOUND, OK

# Zato
from zato.common.webapp import ui as webapp_ui
from zato.rule_engine_dashboard import app as dashboard_app

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Every screen must answer with a full page, and it must answer fast -
# a second is the whole budget where heavyweight rule IDEs are reported
# to take twenty or more to open a project.
Render_Budget_Seconds = 1.0

# The live-outcomes feed runs on every debounced edit, so a full pass
# over a hundred scenarios must fit in an interactive budget.
Live_Outcomes_Budget_Seconds = 1.0
Live_Outcomes_Scenarios = 100

# Each screen and the file its rendered page is stored under for jsdom.
Screens = [
    ('/rulesets/', 'rulesets.html'),
    ('/editor/', 'editor.html'),
    ('/tables/', 'tables.html'),
    ('/tests/', 'tests.html'),
    ('/versions/', 'versions.html'),
    ('/decision-log/', 'log.html'),
    ('/vocabulary/', 'vocabulary.html'),
    ('/notifications/', 'notifications.html'),
]

# Where the node side of this suite lives, relative to this file.
_here = os.path.dirname(os.path.abspath(__file__))
_node_dir = os.path.abspath(os.path.join(_here, '..', '..', '..', 'js', 'zato-rule-engine-dashboard'))

# The static roots jsdom serves scripts and stylesheets from.
_webapp_static = os.path.join(os.path.dirname(os.path.abspath(webapp_ui.__file__)), 'static', 'webapp')
_dashboard_static = os.path.join(os.path.dirname(os.path.abspath(dashboard_app.__file__)), 'static', 'rule-engine')

# ################################################################################################################################
# ################################################################################################################################

def _run_node(arguments:'any_') -> 'None':
    """ Runs one node smoke and surfaces its full output on failure.
    """
    result = subprocess.run(['node'] + arguments, capture_output=True, text=True, cwd=_node_dir)

    print(result.stdout)
    assert result.returncode == 0, result.stdout + result.stderr

# ################################################################################################################################
# ################################################################################################################################

def test_every_screen_renders_within_budget(client:'any_') -> 'None':
    """ Every screen answers with a full page under the render budget.
    """
    for url_path, _ in Screens:
        started = time.perf_counter()
        response = client.get(url_path)
        elapsed = time.perf_counter() - started

        assert response.status_code == OK, (url_path, response.status_code)
        assert elapsed <= Render_Budget_Seconds, (url_path, elapsed)

# ################################################################################################################################

def test_the_root_path_leads_to_the_rulesets_screen(client:'any_') -> 'None':
    """ The root path is a redirect to the rulesets home screen.
    """
    response:'any_' = client.get('/')
    assert response.status_code == FOUND, response.status_code
    assert response.headers['Location'] == '/rulesets/', response.headers['Location']

# ################################################################################################################################

def test_static_files_are_served_with_their_content_types(client:'any_') -> 'None':
    """ The application serves its own static files and each answers with its real content type,
    never the HTML of an error page, which browsers would refuse to run.
    """
    expected = [
        ('/static/webapp/js/shared.js', 'text/javascript'),
        ('/static/webapp/css/tokens.css', 'text/css'),
        ('/static/rule-engine/css/dashboard.css', 'text/css'),
        ('/static/webapp/assets/zato-logo-blue.svg', 'image/svg+xml'),
    ]

    for url_path, content_type in expected:
        response:'any_' = client.get(url_path)
        assert response.status_code == OK, (url_path, response.status_code)
        assert response.headers['Content-Type'].startswith(content_type), (url_path, response.headers['Content-Type'])

        # An edited asset reaches the screen on the next request, without a cache bypass by hand
        assert response.headers['Cache-Control'] == 'no-cache', (url_path, response.headers['Cache-Control'])

# ################################################################################################################################

def test_signed_out_visitors_land_on_the_sign_in_screen() -> 'None':
    """ Without a session, every screen sends the visitor to sign in first.
    """
    # Django - imported here because the client class is only usable once the application is up
    from django.test import Client

    visitor = Client()

    for url_path, _ in Screens:
        response:'any_' = visitor.get(url_path)
        assert response.status_code == FOUND, (url_path, response.status_code)
        assert response.headers['Location'].startswith('/login/'), (url_path, response.headers['Location'])

# ################################################################################################################################

def test_screens_boot_in_jsdom(client:'any_', live_server:'any_', tmp_path:'any_') -> 'None':
    """ Every screen, rendered through the test client, boots in jsdom with its
    fetch calls answered by the live test server, and the view objects respond.
    """
    pages_dir = tmp_path / 'pages'
    pages_dir.mkdir()

    for url_path, file_name in Screens:
        response = client.get(url_path)
        assert response.status_code == OK, (url_path, response.status_code)
        _ = (pages_dir / file_name).write_bytes(response.content)

    # The session and the CSRF cookie both travel - the screens POST at
    # boot and Django checks the header token against the cookie.
    cookie_parts = []
    for name, morsel in client.cookies.items():
        cookie_parts.append(f'{name}={morsel.value}')

    cookies = '; '.join(cookie_parts)

    _run_node([
        os.path.join(_node_dir, 'run_jsdom.js'),
        str(pages_dir),
        live_server,
        cookies,
        _webapp_static,
        _dashboard_static,
    ])

# ################################################################################################################################

def test_editor_scale_budgets() -> 'None':
    """ The completion list, type-to-filter, both grids, the decision log
    and the versions diff stay within their budgets at sizes where rule
    editors are commonly reported to degrade.
    """
    _run_node([
        os.path.join(_node_dir, 'check_scale.js'),
        os.path.join(_webapp_static, 'js'),
        os.path.join(_dashboard_static, 'js'),
    ])

# ################################################################################################################################

def test_live_outcomes_feed_within_budget(client:'any_', ruleset:'any_') -> 'None':
    """ A full live-outcomes pass over a hundred scenarios fits in the
    interactive budget - this is the work every debounced edit triggers.
    """
    preview = client.get(f'/rules/rulesets/{ruleset.id}/preview/')
    assert preview.status_code == OK
    documents = json.loads(preview.content)['document']['documents']

    scenarios = []
    for index in range(Live_Outcomes_Scenarios):
        scenarios.append({
            'name': f'Scenario {index}',
            'input': {'credit_score': 500 + index * 3},
            'expected': {},
        })

    body = {'documents': documents, 'test_set': {'name': 'Scale suite', 'scenarios': scenarios}}

    started = time.perf_counter()
    response = client.post('/rules/editor/outcomes/', data=json.dumps(body), content_type='application/json')
    elapsed = time.perf_counter() - started

    assert response.status_code == OK, response.content
    result = json.loads(response.content)
    assert result['total'] == Live_Outcomes_Scenarios
    assert elapsed <= Live_Outcomes_Budget_Seconds, elapsed

# ################################################################################################################################
# ################################################################################################################################
