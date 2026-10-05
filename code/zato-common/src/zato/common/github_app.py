# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module has no Zato imports on purpose, the same file is also part of the Azure deploy program.

# stdlib
import base64
import json
import os
import re
import time
from datetime import datetime, timezone
from logging import getLogger
from subprocess import PIPE, run
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

anydict = dict[str, Any]
strlist = list[str]

# ################################################################################################################################
# ################################################################################################################################

class GitHub_App:
    """ The GitHub App that a dashboard creates for itself, and the files it keeps about it in the link directory.
    """
    Config_File = 'github-app.json'
    Key_File    = 'github-app.pem'

    API_URL     = 'https://api.github.com'
    API_Version = '2022-11-28'
    User_Agent  = 'zato-dashboard'

    Create_URL  = 'https://github.com/settings/apps/new'
    Install_URL = 'https://github.com/apps/{slug}/installations/new'
    Home_URL    = 'https://zato.io'

    Name_Prefix = 'Zato Dashboard'
    Permissions = {'contents': 'write', 'metadata': 'read'}

    # Git authenticates with this user name and the installation token as the password.
    Token_User = 'x-access-token'

    Repo_Git_URL = 'https://github.com/{owner}/{name}.git'

    # In seconds
    Timeout = 30

    # A token that has less than this left is not reused.
    Token_Margin = 300

    # The token is issued this far in the past, in case the clock is ahead of GitHub's.
    JWT_Skew = 60
    JWT_Lifetime = 540

# ################################################################################################################################
# ################################################################################################################################

_HTTPS_URL_Pattern = re.compile(r'^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git$')

# The keys of GitHub's response to the code exchange that are kept, the private key goes to its own file.
_App_Keys = ('id', 'client_id', 'slug', 'name', 'html_url')

_Expires_Format = '%Y-%m-%dT%H:%M:%SZ'

# Tokens minted so far, keyed by the link directory.
_tokens:'dict[str, tuple[float, str]]' = {}

# ################################################################################################################################
# ################################################################################################################################

class GitHubAppError(Exception):
    def __init__(self, message:'str', status:'int'=0) -> 'None':
        super().__init__(message)
        self.message = message
        self.status  = status

# ################################################################################################################################
# ################################################################################################################################

def is_https_url(url:'str') -> 'bool':

    out = bool(_HTTPS_URL_Pattern.match(url))
    return out

# ################################################################################################################################

def get_repo_git_url(owner:'str', name:'str') -> 'str':

    out = GitHub_App.Repo_Git_URL.format(owner=owner, name=name)
    return out

# ################################################################################################################################

def get_app_name(suffix:'str') -> 'str':

    out = f'{GitHub_App.Name_Prefix} {suffix}'
    return out

# ################################################################################################################################

def build_manifest(name:'str', redirect_url:'str', setup_url:'str') -> 'anydict':
    """ Returns what the browser posts to GitHub to create the App - access to repository contents and nothing else,
    no webhook, and the two addresses of this dashboard that GitHub sends the browser back to.
    """
    out:'anydict' = {
        'name':                name,
        'url':                 GitHub_App.Home_URL,
        'redirect_url':        redirect_url,
        'setup_url':           setup_url,
        'setup_on_update':     True,
        'public':              False,
        'default_permissions': GitHub_App.Permissions,
        'default_events':      [],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _call_api(method:'str', path:'str', auth:'str', data:'anydict | None'=None) -> 'Any':
    """ Calls the GitHub API and returns the JSON it answers with, no token ever appears in an error.
    """
    url = GitHub_App.API_URL + path
    body = None

    headers = {
        'Accept':               'application/vnd.github+json',
        'X-GitHub-Api-Version': GitHub_App.API_Version,
        'User-Agent':           GitHub_App.User_Agent,
    }

    if auth:
        headers['Authorization'] = auth

    if data is not None:
        body = json.dumps(data).encode('utf8')
        headers['Content-Type'] = 'application/json'

    request = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(request, timeout=GitHub_App.Timeout) as response:
            text = response.read().decode('utf8')

    except HTTPError as exception:
        message = _get_error_message(exception)
        raise GitHubAppError(f'GitHub answered {exception.code} to {method} {path}: {message}', exception.code)

    except URLError as exception:
        raise GitHubAppError(f'GitHub could not be reached for {method} {path}: {exception.reason}')

    except OSError as exception:
        raise GitHubAppError(f'GitHub could not be reached for {method} {path}: {exception}')

    if not text:
        return None

    try:
        out = json.loads(text)
    except ValueError:
        raise GitHubAppError(f'GitHub did not answer {method} {path} with JSON')

    return out

# ################################################################################################################################

def _get_error_message(exception:'HTTPError') -> 'str':

    try:
        text = exception.read().decode('utf8')
        data = json.loads(text)
        out = str(data['message'])
    except Exception:
        out = exception.reason

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_config_path(link_dir:'str') -> 'str':
    out = os.path.join(link_dir, GitHub_App.Config_File)
    return out

# ################################################################################################################################

def _get_key_path(link_dir:'str') -> 'str':
    out = os.path.join(link_dir, GitHub_App.Key_File)
    return out

# ################################################################################################################################

def _write_config(link_dir:'str', app:'anydict') -> 'None':

    path = _get_config_path(link_dir)
    temp_path = path + '.tmp'

    with open(temp_path, 'w') as output_file:
        json.dump(app, output_file, indent=2)

    os.replace(temp_path, path)

# ################################################################################################################################

def read_app(link_dir:'str') -> 'anydict | None':
    """ Returns what is known about the App, or None if this dashboard has not created one yet.
    """
    path = _get_config_path(link_dir)

    if not os.path.exists(path):
        return None

    with open(path) as input_file:
        text = input_file.read()

    try:
        out = json.loads(text)
    except ValueError:
        logger.warning('File %s is not JSON', path)
        return None

    if not os.path.exists(_get_key_path(link_dir)):
        logger.warning('File %s has no key next to it', path)
        return None

    return out

# ################################################################################################################################

def forget_app(link_dir:'str') -> 'None':
    """ Removes what is kept about the App, which is what happens once GitHub says the App is gone.
    """
    for path in (_get_config_path(link_dir), _get_key_path(link_dir)):
        if os.path.exists(path):
            os.remove(path)

    _ = _tokens.pop(link_dir, None)

    logger.info('GitHub App forgotten in %s', link_dir)

# ################################################################################################################################

def is_installed(app:'anydict | None') -> 'bool':

    out = bool(app and app.get('installation_id'))
    return out

# ################################################################################################################################

def get_install_url(app:'anydict') -> 'str':
    """ Returns the page where the App is installed or, once it is, where its repositories are chosen.
    """
    if is_installed(app):
        out = app['installation_url']
    else:
        out = GitHub_App.Install_URL.format(slug=app['slug'])

    return out

# ################################################################################################################################

def convert_code(code:'str') -> 'anydict':
    """ Exchanges the code that GitHub sent the browser back with for the App's credentials.
    """
    out = _call_api('POST', f'/app-manifests/{code}/conversions', '')

    if not isinstance(out, dict) or 'pem' not in out:
        raise GitHubAppError('GitHub did not answer the code exchange with the App\'s key')

    return out

# ################################################################################################################################

def save_app(link_dir:'str', data:'anydict') -> 'anydict':
    """ Keeps the App's details and its private key in the link directory, the key readable by its owner only.
    """
    os.makedirs(link_dir, exist_ok=True)

    key_path = _get_key_path(link_dir)

    with open(key_path, 'w', opener=_open_private) as output_file:
        _ = output_file.write(data['pem'])

    os.chmod(key_path, 0o600)

    out:'anydict' = {}

    for key in _App_Keys:
        out[key] = data[key]

    out['installation_id']  = 0
    out['installation_url'] = ''
    out['account']          = ''

    _write_config(link_dir, out)
    _ = _tokens.pop(link_dir, None)

    logger.info('GitHub App %s saved to %s', out['slug'], link_dir)

    return out

# ################################################################################################################################

def _open_private(path:'str', flags:'int') -> 'int':
    out = os.open(path, flags, 0o600)
    return out

# ################################################################################################################################

def save_installation(link_dir:'str', app:'anydict', installation_id:'int') -> 'anydict':
    """ Confirms with GitHub that the installation is of this App and keeps it, or raises GitHubAppError.
    """
    jwt = _get_jwt(link_dir, app)
    installation = _call_api('GET', f'/app/installations/{installation_id}', f'Bearer {jwt}')

    if not isinstance(installation, dict):
        raise GitHubAppError(f'GitHub did not describe installation {installation_id}')

    app['installation_id']  = installation_id
    app['installation_url'] = installation['html_url']
    app['account']          = installation['account']['login']

    _write_config(link_dir, app)
    _ = _tokens.pop(link_dir, None)

    logger.info('GitHub App %s installed as %s on %s', app['slug'], installation_id, app['account'])

    return app

# ################################################################################################################################
# ################################################################################################################################

def _encode(data:'bytes') -> 'str':

    out = base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')
    return out

# ################################################################################################################################

def _get_jwt(link_dir:'str', app:'anydict') -> 'str':
    """ Returns a token signed with the App's key that lets us act as the App itself for a few minutes.
    """
    now = int(time.time())

    header  = {'alg': 'RS256', 'typ': 'JWT'}
    payload = {'iat': now - GitHub_App.JWT_Skew, 'exp': now + GitHub_App.JWT_Lifetime, 'iss': app['client_id']}

    signing_input = _encode(json.dumps(header).encode('utf8')) + '.' + _encode(json.dumps(payload).encode('utf8'))

    command = ['openssl', 'dgst', '-sha256', '-sign', _get_key_path(link_dir)]

    try:
        result = run(command, input=signing_input.encode('ascii'), stdout=PIPE, stderr=PIPE, timeout=GitHub_App.Timeout)
    except OSError as exception:
        raise GitHubAppError(f'The App\'s key could not be used: {exception}')

    if result.returncode != 0:
        raise GitHubAppError(f'The App\'s key could not be used, openssl exit code {result.returncode}')

    out = signing_input + '.' + _encode(result.stdout)
    return out

# ################################################################################################################################

def _handle_gone(link_dir:'str', app:'anydict', jwt:'str') -> 'None':
    """ Asks GitHub whether the App itself still exists - if not, everything about it is forgotten, and if it does,
    only its installation is, so the next Connect leads to the install page and not to a new App.
    """
    try:
        _ = _call_api('GET', '/app', f'Bearer {jwt}')
    except GitHubAppError as exception:
        if exception.status == 404:
            forget_app(link_dir)
            raise GitHubAppError(f'GitHub App {app["name"]} no longer exists on GitHub, click Connect to create a new one', 404)
        raise

    app['installation_id']  = 0
    app['installation_url'] = ''
    app['account']          = ''

    _write_config(link_dir, app)
    _ = _tokens.pop(link_dir, None)

    logger.info('GitHub App %s is no longer installed, installation forgotten in %s', app['slug'], link_dir)

    raise GitHubAppError(f'GitHub App {app["name"]} is no longer installed, click Connect to install it', 404)

# ################################################################################################################################

def uninstall_app(link_dir:'str') -> 'None':
    """ Removes the App's installation on GitHub, so it reads nothing any more, and forgets it here. The App itself stays,
    the next Connect installs it again. An installation already gone on GitHub counts as removed.
    """
    app = read_app(link_dir)

    if not app or not is_installed(app):
        return

    jwt = _get_jwt(link_dir, app)

    try:
        _ = _call_api('DELETE', f'/app/installations/{app["installation_id"]}', f'Bearer {jwt}')
    except GitHubAppError as exception:
        if exception.status != 404:
            raise

    app['installation_id']  = 0
    app['installation_url'] = ''
    app['account']          = ''

    _write_config(link_dir, app)
    _ = _tokens.pop(link_dir, None)

    logger.info('GitHub App %s uninstalled, installation forgotten in %s', app['slug'], link_dir)

# ################################################################################################################################

def get_installation_token(link_dir:'str') -> 'str':
    """ Returns a token that reads the repositories the App was installed for, minting one only when the last one is about to expire.
    """
    cached = _tokens.get(link_dir)

    if cached and cached[0] - time.time() > GitHub_App.Token_Margin:
        return cached[1]

    app = read_app(link_dir)

    if not app or not is_installed(app):
        raise GitHubAppError('The GitHub App is not installed')

    jwt = _get_jwt(link_dir, app)

    # A 404 here means the App or its installation was deleted on GitHub, and which of the two it was decides what is kept.
    try:
        response = _call_api('POST', f'/app/installations/{app["installation_id"]}/access_tokens', f'Bearer {jwt}')
    except GitHubAppError as exception:
        if exception.status == 404:
            _handle_gone(link_dir, app, jwt)
        raise

    if not isinstance(response, dict) or 'token' not in response:
        raise GitHubAppError('GitHub did not answer with an installation token')

    out = str(response['token'])

    _tokens[link_dir] = (_get_expires_at(response), out)

    logger.info('Installation token minted for GitHub App %s on %s', app['slug'], app['account'])

    return out

# ################################################################################################################################

def _get_expires_at(response:'anydict') -> 'float':
    """ Returns when the token expires as GitHub says, which is an hour from now unless it says otherwise.
    """
    text = str(response.get('expires_at') or '')

    try:
        out = datetime.strptime(text, _Expires_Format).replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        out = time.time() + 3600

    return out

# ################################################################################################################################

def list_repositories(token:'str') -> 'strlist':
    """ Returns the full names of the repositories the installation may read, the newest first.
    """
    out:'strlist' = []
    found:'list[tuple[str, str]]' = []
    page = 1

    while True:
        response = _call_api('GET', f'/installation/repositories?per_page=100&page={page}', f'token {token}')

        if not isinstance(response, dict):
            raise GitHubAppError('GitHub did not answer with a list of repositories')

        repositories = response.get('repositories') or []

        for item in repositories:
            found.append((str(item['created_at']), str(item['full_name'])))

        if len(repositories) < 100:
            break

        page += 1

    found.sort(reverse=True)

    for _, full_name in found:
        out.append(full_name)

    return out

# ################################################################################################################################

def get_git_auth_arguments(token:'str') -> 'strlist':
    """ Returns what goes in front of the git command for it to authenticate with the token, without the token ever being stored.
    """
    credentials = f'{GitHub_App.Token_User}:{token}'.encode('utf8')
    encoded = base64.b64encode(credentials).decode('ascii')

    out = ['-c', f'http.extraheader=Authorization: basic {encoded}']
    return out

# ################################################################################################################################

def get_git_auth_for_url(link_dir:'str', url:'str') -> 'strlist':
    """ Returns the git arguments that authenticate for the address, which is nothing unless the App is installed
    and the address is an HTTPS one.
    """
    if not is_https_url(url):
        return []

    if not is_installed(read_app(link_dir)):
        return []

    token = get_installation_token(link_dir)

    out = get_git_auth_arguments(token)
    return out

# ################################################################################################################################
# ################################################################################################################################
