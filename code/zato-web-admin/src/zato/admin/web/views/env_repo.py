# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import time
from datetime import datetime, timezone
from json import dumps
from logging import getLogger
from secrets import token_hex
from urllib.parse import urlencode

# Django
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

# Zato
from zato.admin.web.env_repo_local import ensure_key, handle_request as handle_request_locally, handle_request_now
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.base import SettingsBaseView
from zato.admin.web.views.settings.config import env_repo_page_config
from zato.admin.web.views.settings.utils import json_response
from zato.common.env_repo import Env_Repo, get_link_dir, get_new_repo_url, is_host_mode, parse_repo_name, read_current, \
    read_public_key, read_status, set_local_dir, write_request
from zato.common.github_app import build_manifest, convert_code, get_app_name, get_install_url, get_installation_token, \
    GitHub_App, GitHubAppError, is_installed, list_repositories, read_app, save_app, save_installation
from zato.common.util.updates import Updater, UpdaterConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest, HttpResponse, QueryDict
    from zato.common.typing_ import anydict, anydictnone, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

current_dir = os.path.dirname(os.path.abspath(__file__))

updater_config = UpdaterConfig(current_dir=current_dir)
updater = Updater(updater_config)

_Branch_Pattern = re.compile(r'^[A-Za-z0-9_./-]+$')

# The session key with the value that GitHub must send back with the code.
_Session_State = 'env_repo_github_app_state'

# What the App's state on this dashboard reads as in the page.
_App_None      = 'none'
_App_Created   = 'created'
_App_Installed = 'installed'

# How long the page waits for a host to check the address before it is served, in seconds.
_Host_Check_Timeout = 20
_Host_Check_Interval = 0.25

# What the page's button does first, decided here so the page comes out that way and does not get there in the browser.
_Mode_Connect = 'connect'
_Mode_Allow   = 'allow'
_Mode_Switch  = 'switch'
_Mode_Pull    = 'pull'

# ################################################################################################################################
# ################################################################################################################################

def _get_param(query:'QueryDict', name:'str') -> 'str':

    value = query.get(name, '')

    out = str(value).strip()
    return out

# ################################################################################################################################

def _redirect_to_index(**params:'str') -> 'HttpResponseRedirect':

    url = reverse('env-repo')

    if params:
        url = url + '?' + urlencode(params)

    out = HttpResponseRedirect(url)
    return out

# ################################################################################################################################

def _get_app_state(app:'anydictnone') -> 'str':

    if not app:
        out = _App_None
    elif is_installed(app):
        out = _App_Installed
    else:
        out = _App_Created

    return out

# ################################################################################################################################

def _set_local_dir() -> 'None':
    """ Points the link directory at a directory under the dashboard's base directory, with the dashboard's own deploy key in it.
    """
    # config_dir is set at startup, after this module is imported.
    from zato.admin import settings as admin_settings

    path = os.path.join(admin_settings.config_dir, Env_Repo.Local_Dir_Name)
    set_local_dir(path)

    if not is_host_mode():
        ensure_key()

# ################################################################################################################################
# ################################################################################################################################

class EnvRepoView(SettingsBaseView):

    def __init__(self) -> 'None':
        super().__init__(env_repo_page_config, updater, 'zato/env-repo/index.html')

# ################################################################################################################################

    def get_index_context(self) -> 'anydict':

        _set_local_dir()

        current = read_current() or {}
        current_repo = parse_repo_name(current.get('url', ''))

        context = super().get_index_context()
        context['public_key'] = read_public_key()
        context['new_repo_url'] = get_new_repo_url()
        context['new_repo_name'] = Env_Repo.New_Repo_Name
        context['current_branch'] = current.get('branch', '')

        # The address is shown the way a browser shows it.
        context['current_url'] = current_repo.https_url if current_repo else ''

        return context

# ################################################################################################################################

    def _add_app_context(self, req:'HttpRequest', context:'anydict') -> 'None':
        """ Adds what the page needs to create the GitHub App, or to send the browser to install it.
        """
        app = read_app(get_link_dir())

        # The value GitHub sends back with the code, it is in the session so the setup view can compare the two.
        state = token_hex(16)
        session = getattr(req, 'session')
        session[_Session_State] = state

        # The addresses GitHub sends the browser back to are the ones the browser reached this page with, so they work
        # from wherever the browser is, localhost or behind NAT included.
        redirect_url = req.build_absolute_uri(reverse('env-repo-github-app-setup'))
        setup_url    = req.build_absolute_uri(reverse('env-repo-github-app-installed'))

        manifest = build_manifest(get_app_name(token_hex(3)), redirect_url, setup_url)

        repos = self._list_repos(app)

        # The one repository the App may read is the address, unless the environment runs one already.
        context['address'] = context['current_url']

        if len(repos) == 1 and not context['address']:
            only_repo = parse_repo_name(repos[0])
            context['address'] = only_repo.https_url if only_repo else ''

        context['repos']           = repos
        context['app_state']       = _get_app_state(read_app(get_link_dir()))
        context['app_install_url'] = get_install_url(app) if app else ''
        context['app_new_install_url'] = GitHub_App.Install_URL.format(slug=app['slug']) if app else ''
        context['manifest_action'] = f'{GitHub_App.Create_URL}?state={state}'
        context['manifest']        = dumps(manifest)

# ################################################################################################################################

    def _list_repos(self, app:'anydictnone') -> 'strlist':
        """ Returns the repositories the App may read, newest first, or nothing if there is no App or GitHub cannot be asked.
        An App deleted on GitHub is forgotten here while at it.
        """
        out:'strlist' = []

        if not is_installed(app):
            return out

        try:
            token = get_installation_token(get_link_dir())
            out = list_repositories(token)
        except GitHubAppError as exception:
            logger.warning('Repositories not listed: %s', exception.message)

        return out

# ################################################################################################################################

    def _check_now(self, address:'str') -> 'anydictnone':
        """ Checks the address with GitHub before the page is served, so the page comes out with the branches in it.
        A host does the check itself, and the page waits for its answer for a while.
        """
        repo = parse_repo_name(address)

        if not repo:
            return None

        if is_installed(read_app(get_link_dir())):
            url = repo.git_url
        else:
            url = repo.ssh_url

        if not is_host_mode():
            out = handle_request_now(Env_Repo.Action_Check, url, '')
            return out

        started = datetime.now(timezone.utc)
        write_request(Env_Repo.Action_Check, url, '')

        deadline = time.time() + _Host_Check_Timeout

        while time.time() < deadline:
            time.sleep(_Host_Check_Interval)
            status = read_status()

            if not status or status.get('url') != url:
                continue

            if datetime.fromisoformat(status['time']) < started:
                continue

            if status['state'] in (Env_Repo.State_OK, Env_Repo.State_Error):
                return status

        logger.info('Host did not check %s in %s seconds', url, _Host_Check_Timeout)
        return None

# ##############################################################################################################################

    def _add_connection_context(self, context:'anydict') -> 'None':
        """ Adds what the page shows about the address it opens with - the branches, the one chosen, and what the button does.
        """
        status = None
        address = context['address']

        if address:
            status = self._check_now(address)

        branches = (status or {}).get('branches') or []
        is_checked = bool(status) and status['state'] == Env_Repo.State_OK

        # The branch that runs now comes first, then main, then whatever is first.
        selected = ''

        if context['current_branch'] in branches:
            selected = context['current_branch']
        elif Env_Repo.Default_Branch in branches:
            selected = Env_Repo.Default_Branch
        elif branches:
            selected = branches[0]

        if not address:
            mode = _Mode_Connect
        elif not status or not is_checked:
            mode = _Mode_Allow if status else _Mode_Connect
        elif not is_host_mode():
            mode = _Mode_Pull
        elif address == context['current_url'] and selected == context['current_branch']:
            mode = _Mode_Pull
        else:
            mode = _Mode_Switch

        context['mode']            = mode
        context['is_host']         = is_host_mode()
        context['is_checked']      = is_checked
        context['branches']        = branches
        context['selected_branch'] = selected
        context['initial_status']  = dumps(status) if status else ''

# ##############################################################################################################################

    @method_allowed('GET')
    def index(self, req:'HttpRequest') -> 'HttpResponse':

        context = self.get_index_context()
        self._add_app_context(req, context)
        self._add_connection_context(context)

        return TemplateResponse(req, self.template_name, context)

# ################################################################################################################################

    @method_allowed('GET')
    def github_app_setup(self, req:'HttpRequest') -> 'HttpResponse':
        """ Where GitHub sends the browser once the App is created - the code is exchanged for the App's credentials
        and the browser goes on to GitHub's page to install the App.
        """
        _set_local_dir()

        code  = _get_param(req.GET, 'code')
        state = _get_param(req.GET, 'state')

        if not code:
            return _redirect_to_index(error='GitHub did not send the code for the new App')

        session = getattr(req, 'session')

        if not state or state != session.get(_Session_State):
            return _redirect_to_index(error='The App was not created from this page, start over')

        del session[_Session_State]

        try:
            data = convert_code(code)
            app = save_app(get_link_dir(), data)
        except GitHubAppError as exception:
            logger.warning('GitHub App not created: %s', exception.message)
            return _redirect_to_index(error=exception.message)
        except OSError as exception:
            logger.warning('GitHub App not saved to %s: %s', get_link_dir(), exception)
            return _redirect_to_index(error=f'The App could not be saved: {exception}')

        return HttpResponseRedirect(get_install_url(app))

# ################################################################################################################################

    @method_allowed('GET')
    def github_app_installed(self, req:'HttpRequest') -> 'HttpResponse':
        """ Where GitHub sends the browser once the App is installed, or its repositories change.
        """
        _set_local_dir()

        installation_id = _get_param(req.GET, 'installation_id')
        app = read_app(get_link_dir())

        if not app:
            return _redirect_to_index(error='The App was not created from this page, start over')

        if not installation_id.isdigit():
            return _redirect_to_index(error='GitHub did not say which installation this is')

        try:
            _ = save_installation(get_link_dir(), app, int(installation_id))
        except GitHubAppError as exception:
            logger.warning('GitHub App installation %s not accepted: %s', installation_id, exception.message)
            return _redirect_to_index(error=exception.message)

        return _redirect_to_index(installed='1')

# ################################################################################################################################

    @method_allowed('GET')
    def github_app_repos(self, req:'HttpRequest') -> 'HttpResponse':
        """ Returns the repositories that the App may read.
        """
        _set_local_dir()

        repos = self._list_repos(read_app(get_link_dir()))
        app_state = _get_app_state(read_app(get_link_dir()))

        return json_response({'repos': repos, 'app_state': app_state})

# ################################################################################################################################

    @method_allowed('GET')
    def get_status(self, req:'HttpRequest') -> 'HttpResponse':

        _set_local_dir()

        data = {
            'status':  read_status(),
            'current': read_current(),
        }

        return json_response(data)

# ################################################################################################################################

    def _handle_request(self, req:'HttpRequest', action:'str') -> 'HttpResponse':
        """ Writes the request for the host if there is one, otherwise handles it in this process.
        """
        _set_local_dir()

        repo = parse_repo_name(_get_param(req.POST, 'url'))
        branch = _get_param(req.POST, 'branch')

        if not repo:
            return json_response({'error': 'Repository address must look like https://github.com/owner/name'}, success=False)

        if action in (Env_Repo.Action_Switch, Env_Repo.Action_Pull) and not _Branch_Pattern.match(branch):
            return json_response({'error': 'Branch name is not valid'}, success=False)

        # The App reads over HTTPS with its token, without one the deploy key reads over SSH.
        if is_installed(read_app(get_link_dir())):
            url = repo.git_url
        else:
            url = repo.ssh_url

        try:
            if is_host_mode():
                write_request(action, url, branch)
            else:
                handle_request_locally(action, url, branch, getattr(req, 'zato').client)
        except OSError as exception:
            logger.warning('Request not written to %s: %s', get_link_dir(), exception)
            return json_response({'error': f'Request could not be written: {exception}'}, success=False)

        data = {
            'full_name': repo.full_name,
            'url':       url,
            'https_url': repo.https_url,
        }

        return json_response(data)

# ################################################################################################################################

    @method_allowed('POST')
    def check(self, req:'HttpRequest') -> 'HttpResponse':
        return self._handle_request(req, Env_Repo.Action_Check)

# ################################################################################################################################

    @method_allowed('POST')
    def switch(self, req:'HttpRequest') -> 'HttpResponse':
        return self._handle_request(req, Env_Repo.Action_Switch)

# ################################################################################################################################

    def _handle_current(self, req:'HttpRequest', action:'str', is_current_needed:'bool'=True) -> 'HttpResponse':
        """ Writes a request about the repository the environment runs now, or about the one in the page if none does
        and the action does not need one.
        """
        _set_local_dir()

        current = read_current() or {}
        url     = current.get('url', '')
        branch  = current.get('branch', '')

        if not url:
            if is_current_needed:
                return json_response({'error': 'No repository is connected'}, success=False)

            repo = parse_repo_name(_get_param(req.POST, 'url'))
            url  = repo.git_url if repo else ''

        try:
            if is_host_mode():
                write_request(action, url, branch)
            else:
                handle_request_locally(action, url, branch, getattr(req, 'zato').client)
        except OSError as exception:
            logger.warning('Request not written to %s: %s', get_link_dir(), exception)
            return json_response({'error': f'Request could not be written: {exception}'}, success=False)

        return json_response({'url': url})

# ################################################################################################################################

    @method_allowed('POST')
    def disconnect(self, req:'HttpRequest') -> 'HttpResponse':
        """ Disconnects from GitHub entirely, a host that ran a repository goes back to the public blueprint.
        """
        return self._handle_current(req, Env_Repo.Action_Disconnect, is_current_needed=False)

# ################################################################################################################################

    @method_allowed('POST')
    def pull(self, req:'HttpRequest') -> 'HttpResponse':
        """ Brings the checkout of the repository and branch in the page up to date, without a restart.
        """
        return self._handle_request(req, Env_Repo.Action_Pull)

# ################################################################################################################################
# ################################################################################################################################

env_repo_view = EnvRepoView()

# ################################################################################################################################
# ################################################################################################################################
