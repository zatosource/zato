# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'
_Channel_Url_Pattern = '/zato/http-soap/?cluster=1&connection=channel&transport=plain_http'
_Outgoing_Url_Pattern = '/zato/http-soap/?cluster=1&connection=outgoing&transport=plain_http'
_Groups_Url_Pattern = '/zato/groups/group/zato-api-creds/?cluster=1'

_Test_Name_Prefix = 'test.xpage.' + os.urandom(4).hex() + '.'

# ################################################################################################################################
# ################################################################################################################################

def _create_definition_via_ui(page:'Page', base_url:'str', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the dashboard UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + os.urandom(8).hex()

    # Navigate to basic auth page ..
    _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
    page.wait_for_selector('#data-table', state='visible')

    # .. open and fill the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    # .. submit and wait ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'username': username,
        'realm': realm,
        'password': password,
    }

    return out

# ################################################################################################################################

def _create_definition_via_api(api_client:'object', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the Zato API and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    password = 'password.' + os.urandom(8).hex()

    response = api_client.invoke('zato.security.basic-auth.create', {
        'cluster_id': 1,
        'name': name,
        'username': username,
        'realm': 'realm.' + name,
        'is_active': True,
    })

    item_id = response['id']

    # .. also set the password.
    api_client.invoke('zato.security.basic-auth.change-password', {
        'id': item_id,
        'password': password,
    })

    out = {
        'id': item_id,
        'name': name,
        'username': username,
    }

    return out

# ################################################################################################################################

def _delete_definition_via_api(api_client:'object', item_id:'int') -> 'None':
    """ Deletes a basic auth definition via the Zato API.
    """
    api_client.invoke('zato.security.basic-auth.delete', {
        'id': item_id,
        'cluster_id': 1,
    })

# ################################################################################################################################

def _find_security_option(page:'Page', select_id:'str', name:'str') -> 'bool':
    """ Returns True if the security select contains an option matching the given name.
    """

    out = page.evaluate(f"""
    (() => {{
        var select = document.querySelector('{select_id}');
        if (!select) return false;
        var options = select.querySelectorAll('option');
        for (var idx = 0; idx < options.length; idx++) {{
            if (options[idx].textContent.indexOf('{name}') !== -1) return true;
        }}
        return false;
    }})()
    """)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthCrossPage:
    """ Tests for cross-page visibility of basic auth definitions in channels, outgoing, and groups.
    """

    def test_57_def_in_channel_security_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to REST channels, opens create dialog,
        and verifies the security dropdown contains the def as 'Basic Auth/{name}'.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'chan-drop')

        # .. navigate to REST channels ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}', timeout=60000)
        page.wait_for_selector('#data-table', state='visible', timeout=15000)

        # .. open the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the security select to be populated (SSE may take a moment) ..
        time.sleep(1)

        # .. verify the security dropdown contains our definition.
        expected_label = f'Basic Auth/{defn["name"]}'
        found = _find_security_option(page, '#id_security', defn['name'])
        assert found, f'Expected "{expected_label}" in channel security dropdown'

# ################################################################################################################################

    def test_58_def_in_outgoing_security_dropdown(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to outgoing REST, opens create dialog,
        and verifies the security select contains the def.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'out-drop')

        # .. navigate to outgoing REST ..
        _ = page.goto(f'{base_url}{_Outgoing_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog ..
        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        time.sleep(1)

        # .. verify the security dropdown contains our definition.
        found = _find_security_option(page, '#id_security', defn['name'])
        assert found, f'Expected Basic Auth/{defn["name"]} in outgoing security dropdown'

# ################################################################################################################################

    def test_59_sse_live_updates_channel_dropdown(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'object',
    ) -> 'None':
        """ Navigates to REST channels, opens the create dialog (starts SSE).
        Then creates a new basic auth def via the API.
        Verifies the new def appears in the security dropdown without closing the dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Inject console log capture so we can see what SSE is doing ..
        page.evaluate("""
        (() => {
            window._sse_logs = [];
            var orig = console.log;
            console.log = function() {
                var msg = Array.prototype.join.call(arguments, ' ');
                if (msg.indexOf('live_form_updates') !== -1) {
                    window._sse_logs.push(msg);
                }
                orig.apply(console, arguments);
            };
            var origErr = console.error;
            console.error = function() {
                var msg = Array.prototype.join.call(arguments, ' ');
                if (msg.indexOf('live_form_updates') !== -1) {
                    window._sse_logs.push('ERROR: ' + msg);
                }
                origErr.apply(console, arguments);
            };
        })()
        """)

        # Navigate to REST channels and open the create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}', timeout=60000)
        page.wait_for_selector('#data-table', state='visible', timeout=15000)

        # Re-inject console capture after navigation ..
        page.evaluate("""
        (() => {
            window._sse_logs = [];
            var orig = console.log;
            console.log = function() {
                var msg = Array.prototype.join.call(arguments, ' ');
                if (msg.indexOf('live_form_updates') !== -1) {
                    window._sse_logs.push(msg);
                }
                orig.apply(console, arguments);
            };
            var origErr = console.error;
            console.error = function() {
                var msg = Array.prototype.join.call(arguments, ' ');
                if (msg.indexOf('live_form_updates') !== -1) {
                    window._sse_logs.push('ERROR: ' + msg);
                }
                origErr.apply(console, arguments);
            };
        })()
        """)

        # Log 1: Check what live_form_updates configs are registered ..
        has_create_config = page.evaluate('$.fn.zato.live_form_updates.has_config("create")')
        create_configs = page.evaluate("""
        (() => {
            var cfgs = $.fn.zato.live_form_updates._get_configs('create');
            return JSON.stringify(cfgs.map(function(c) { return {object_type: c.object_type, handler: c.handler || 'select'}; }));
        })()
        """)
        print(f'[SSE-DEBUG-1] has_config(create)={has_create_config}, configs={create_configs}')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')

        # Log 2: Check if dialog opened and SSE was started (look at captured logs) ..
        time.sleep(0.5)
        sse_logs_after_open = page.evaluate('JSON.stringify(window._sse_logs || [])')
        print(f'[SSE-DEBUG-2] SSE logs after dialog open: {sse_logs_after_open}')

        # Log 3: Check the security select state right after dialog open ..
        select_state = page.evaluate("""
        (() => {
            var sel = document.querySelector('#id_security');
            if (!sel) return 'SELECT_NOT_FOUND';
            return JSON.stringify({
                optionCount: sel.options.length,
                id: sel.id,
                name: sel.name,
                disabled: sel.disabled
            });
        })()
        """)
        print(f'[SSE-DEBUG-3] Security select state: {select_state}')

        # .. wait for SSE to connect ..
        time.sleep(2)

        # Log 4: Check connection state via captured logs after 2s ..
        sse_logs_after_wait = page.evaluate('JSON.stringify(window._sse_logs || [])')
        print(f'[SSE-DEBUG-4] SSE logs after 2s wait: {sse_logs_after_wait}')

        # Log 5: Captured SSE console logs so far ..
        sse_logs = page.evaluate('JSON.stringify(window._sse_logs || [])')
        print(f'[SSE-DEBUG-5] SSE console logs before API create: {sse_logs}')

        # Log 6: Current dropdown options before API create ..
        options_before = page.evaluate("""
        (() => {
            var sel = document.querySelector('#id_security');
            if (!sel) return 'SELECT NOT FOUND';
            var opts = [];
            for (var idx = 0; idx < sel.options.length; idx++) {
                opts.push(sel.options[idx].textContent);
            }
            return JSON.stringify(opts);
        })()
        """)
        print(f'[SSE-DEBUG-6] Dropdown options before API create: {options_before}')

        # .. create a new basic auth definition via the API ..
        defn = _create_definition_via_api(api_client, 'sse-create')
        print(f'[SSE-DEBUG-7] Created def via API: id={defn["id"]}, name={defn["name"]}')

        # .. wait for the SSE update to arrive (up to 15s) ..
        found = False

        for attempt in range(30):
            time.sleep(0.5)
            found = _find_security_option(page, '#id_security', defn['name'])

            # Log 8: Periodic check ..
            if attempt in (1, 3, 5, 9, 14, 19, 29):
                sse_logs_now = page.evaluate('JSON.stringify((window._sse_logs || []).slice(-5))')
                option_count = page.evaluate('document.querySelector("#id_security") ? document.querySelector("#id_security").options.length : -1')
                print(f'[SSE-DEBUG-8] Attempt {attempt}: found={found}, options={option_count}, recent_logs={sse_logs_now}')

            if found:
                break

        # Log 9: Final state ..
        sse_logs_final = page.evaluate('JSON.stringify(window._sse_logs || [])')
        print(f'[SSE-DEBUG-9] All SSE console logs: {sse_logs_final}')

        options_after = page.evaluate("""
        (() => {
            var sel = document.querySelector('#id_security');
            if (!sel) return 'SELECT NOT FOUND';
            var opts = [];
            for (var idx = 0; idx < sel.options.length; idx++) {
                opts.push(sel.options[idx].textContent);
            }
            return JSON.stringify(opts);
        })()
        """)
        print(f'[SSE-DEBUG-10] Dropdown options after polling: {options_after}')

        # Log 11: Check if the select was modified at all during the test ..
        has_config_final = page.evaluate('$.fn.zato.live_form_updates.has_config("create")')
        print(f'[SSE-DEBUG-11] has_config(create) at end: {has_config_final}')

        # Log 12-15: Read dashboard server.log, filter to SSE generator PID only ..
        dashboard_dir = zato_dashboard['dashboard_dir']
        log_dir = os.path.join(dashboard_dir, 'logs')
        server_log_path = os.path.join(log_dir, 'server.log')

        if os.path.isfile(server_log_path):
            with open(server_log_path, 'r', encoding='utf-8', errors='replace') as fh:
                all_lines = fh.read().splitlines()

            # Find the PID of the SSE generator worker - it's the one that logged "VIEW CALLED" ..
            sse_pid = None
            for line in all_lines:
                if 'VIEW CALLED' in line:
                    # Format: "... - INFO - 12345:MainThread - ..."
                    parts = line.split(' - ')
                    for part in parts:
                        if ':MainThread' in part:
                            sse_pid = part.split(':')[0].strip()
                            break

            if sse_pid:
                print(f'[SSE-DEBUG-12] SSE generator PID: {sse_pid}')
                pid_lines = [line for line in all_lines if sse_pid in line]
                print(f'[SSE-DEBUG-12] Total lines from SSE PID: {len(pid_lines)}')
                for pid_line in pid_lines:
                    print(f'[SSE-DEBUG-13]   {pid_line}')
            else:
                print('[SSE-DEBUG-12] Could not find SSE PID')

        # Log 14: Also check server logs for the SSE-related service invocations ..
        server_dir = zato_dashboard['server_dir']
        server_log_dir = os.path.join(server_dir, 'logs')
        server_log_files = glob.glob(os.path.join(server_log_dir, '*.log'))
        for log_file in server_log_files:
            if not os.path.isfile(log_file):
                continue
            with open(log_file, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
            relevant_lines = [line for line in content.splitlines() if 'security.get-list' in line or 'live_form' in line.lower()]
            log_basename = os.path.basename(log_file)
            if relevant_lines:
                print(f'[SSE-DEBUG-14] Server log {log_basename}: {len(relevant_lines)} relevant lines')
                for line in relevant_lines:
                    print(f'[SSE-DEBUG-15]   {line}')

        # .. verify the new def appeared in the dropdown without dialog close.
        assert found, f'Expected "{defn["name"]}" to appear in security dropdown via SSE'

        # .. clean up.
        _delete_definition_via_api(api_client, defn['id'])

# ################################################################################################################################

    def test_60_def_in_groups_badge_picker(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a basic auth def, navigates to security groups, opens create dialog,
        and verifies the badge picker contains a badge with the def name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the UI ..
        defn = _create_definition_via_ui(page, base_url, 'grp-badge')

        # .. navigate to security groups ..
        _ = page.goto(f'{base_url}{_Groups_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. open the create dialog via the JS function ..
        page.evaluate('$.fn.zato.groups.create()')
        page.wait_for_selector('#create-div', state='visible')

        # .. wait for the badge picker to load ..
        time.sleep(2)

        # .. find a badge with our definition name in the available zone.
        found = page.evaluate(f"""
        (() => {{
            var badges = document.querySelectorAll('#badge-zone-available-create .security-badge');
            for (var idx = 0; idx < badges.length; idx++) {{
                var nameSpan = badges[idx].querySelector('.security-badge-name');
                if (nameSpan && nameSpan.textContent.indexOf('{defn["name"]}') !== -1) return true;
            }}
            return false;
        }})()
        """)

        assert found, f'Expected badge with name "{defn["name"]}" in groups badge picker'

# ################################################################################################################################

    def test_61_deleted_def_removed_from_channel_dropdown(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'object',
    ) -> 'None':
        """ Creates a def, verifies it appears in the channel security dropdown,
        deletes it, and verifies it is gone from the dropdown after reload.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via the API ..
        defn = _create_definition_via_api(api_client, 'del-drop')

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify it is present ..
        found_before = _find_security_option(page, '#id_security', defn['name'])
        assert found_before, f'Expected "{defn["name"]}" in dropdown before delete'

        # .. close the dialog ..
        page.evaluate('$("#create-div").dialog("close")')
        page.wait_for_function('!document.querySelector("#create-div").offsetParent')

        # .. delete the definition via API ..
        _delete_definition_via_api(api_client, defn['id'])

        # .. reload the channels page and open the dialog again ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify the def is gone.
        found_after = _find_security_option(page, '#id_security', defn['name'])
        assert not found_after, f'Expected "{defn["name"]}" removed from dropdown after delete'

# ################################################################################################################################

    def test_62_sse_live_removes_deleted_def(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'object',
    ) -> 'None':
        """ Opens the REST channel create dialog (starts SSE).
        Creates a def via API, waits for it to appear, then deletes it via API.
        Verifies the def disappears from the dropdown without closing the dialog.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via API first ..
        defn = _create_definition_via_api(api_client, 'sse-del')

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify the def is present in the dropdown ..
        found_before = _find_security_option(page, '#id_security', defn['name'])
        assert found_before, f'Expected "{defn["name"]}" in dropdown before SSE delete'

        # .. delete via API ..
        _delete_definition_via_api(api_client, defn['id'])

        # .. wait for SSE to remove it (up to 5s) ..
        removed = False

        for _ in range(10):
            time.sleep(0.5)
            still_there = _find_security_option(page, '#id_security', defn['name'])
            if not still_there:
                removed = True
                break

        assert removed, f'Expected "{defn["name"]}" to disappear from dropdown via SSE'

# ################################################################################################################################

    def test_63_sse_live_renames_def_in_dropdown(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'object',
    ) -> 'None':
        """ Opens the REST channel create dialog (starts SSE).
        Edits a basic auth def's name via API.
        Verifies the option text in the dropdown changes to reflect the new name.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a definition via API ..
        defn = _create_definition_via_api(api_client, 'sse-rename')
        old_name = defn['name']
        new_name = _Test_Name_Prefix + 'sse-renamed'

        # .. navigate to REST channels and open create dialog ..
        _ = page.goto(f'{base_url}{_Channel_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        page.click('#markup .page_prompt a')
        page.wait_for_selector('#create-div', state='visible')
        time.sleep(1)

        # .. verify old name is in the dropdown ..
        found_old = _find_security_option(page, '#id_security', old_name)
        assert found_old, f'Expected "{old_name}" in dropdown before rename'

        # .. edit the name via API ..
        api_client.invoke('zato.security.basic-auth.edit', {
            'id': defn['id'],
            'cluster_id': 1,
            'name': new_name,
            'username': defn['username'],
            'realm': f'realm.{defn["name"]}',
            'is_active': True,
        })

        # .. wait for SSE to update (up to 5s) ..
        found_new = False

        for _ in range(10):
            time.sleep(0.5)
            found_new = _find_security_option(page, '#id_security', new_name)
            if found_new:
                break

        assert found_new, f'Expected "{new_name}" to appear in dropdown via SSE after rename'

        # .. clean up.
        _delete_definition_via_api(api_client, defn['id'])

# ################################################################################################################################
# ################################################################################################################################
