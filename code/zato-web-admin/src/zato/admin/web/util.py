# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Django
from django.template.response import TemplateResponse

# Zato
from zato.common.util.platform_ import is_windows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

windows_disabled = [
    'abc123',
    'zxc456'
]

# Where a server directory keeps user configuration
user_conf_path = os.path.join('config', 'repo', 'user-conf')

# The environment variable that points to the server directory
_server_env_key = 'ZATO_SERVER_BASE_DIR'

# The server of an environment that the dashboard reads user configuration of
# when the environment does not say which server directory to use
_default_server_name = 'server1'

# Names of built-in security definitions that pub/sub pages never display
PubSub_Excluded_Sec_Names = {
    'admin.invoke',
    'ide_publisher'
}

# ################################################################################################################################
# ################################################################################################################################

def get_server_directory() -> 'str':
    """ The server directory whose user configuration the dashboard works with. The environment
    variable that Zato starts its own commands with is used if it is set, otherwise it is the
    default server of the environment that the dashboard runs in, which is the directory next
    to the dashboard's own one.
    """
    server_directory = os.environ.get(_server_env_key, '')

    if server_directory:
        return server_directory

    # config_dir is a lowercase setting, which Django's settings proxy does not expose,
    # so it is read from the settings module directly.
    from zato.admin import settings as admin_settings

    config_dir:'any_' = admin_settings.config_dir
    env_directory = os.path.dirname(config_dir)

    out = os.path.join(env_directory, _default_server_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_server_user_conf_directory() -> 'str':
    """ The user configuration directory of the server whose files the dashboard works with.
    """
    server_directory = get_server_directory()

    out = os.path.join(server_directory, user_conf_path)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_template_response(req, template_name, return_data):

    if is_windows:
        for name in windows_disabled:
            if name in template_name:
                return_data['is_disabled'] = True
                return_data['disabled_template_name'] = template_name

    return TemplateResponse(req, template_name, return_data)

# ################################################################################################################################
# ################################################################################################################################

def get_user_profile(user, needs_logging=False):

    if needs_logging:
        logger.debug('Getting profile for user `%s`', user)

    from zato.admin.web.models import UserProfile

    try:
        user_profile = UserProfile.objects.get(user=user)
        if needs_logging:
            logger.debug('Found an existing profile for user `%s`', user)
    except UserProfile.DoesNotExist:

        if needs_logging:
            logger.info('Did not find an existing profile for user `%s`', user)

        user_profile = UserProfile(user=user)
        user_profile.save()

        if needs_logging:
            logger.info('Created a profile for user `%s`', user)

    finally:
        if needs_logging:
            logger.debug('Returning a user profile for `%s`', user)
        return user_profile

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

def get_pubsub_security_definitions(request:'any_', form_type:'str'='edit', context:'str'='subscription') -> 'list':

    response = request.zato.client.invoke('zato.security.basic-auth.get-list', {
        'cluster_id': request.zato.cluster_id,
    })

    # Get already used security definitions based on context
    choices = []
    used_sec_ids = set()

    if form_type == 'create':
        if context == 'subscription':
            # For subscriptions, exclude definitions used by other subscriptions ..
            subscriptions_response = request.zato.client.invoke('zato.pubsub.subscription.get-list', {
                'cluster_id': request.zato.cluster_id,
            })

            # .. create a mapping of security names to IDs ..
            sec_name_to_id = {}
            for sec_def in response.data:
                sec_name_to_id[sec_def['name']] = sec_def['id']

            # .. and collect used IDs.
            for item in subscriptions_response.data:
                sec_id = None
                if item.get('security_id'):
                    sec_id = item['security_id']
                elif item.get('sec_name'):
                    sec_name = item['sec_name']
                    sec_id = sec_name_to_id.get(sec_name)

                if sec_id:
                    used_sec_ids.add(sec_id)

        elif context in ('permission', 'client'):
            # For permissions and clients, exclude definitions already in use.
            permissions_response = request.zato.client.invoke('zato.pubsub.permission.get-list', {
                'cluster_id': request.zato.cluster_id,
            })
            for item in permissions_response.data:
                used_sec_ids.add(item['sec_base_id'])

    for item in response.data:
        is_not_used = item['id'] not in used_sec_ids
        is_not_filtered = item['name'] not in PubSub_Excluded_Sec_Names
        is_not_zato = not item['name'].startswith('zato')

        if is_not_used and is_not_filtered and is_not_zato:
            choices.append({
                'id': item['id'],
                'name': item['name']
            })

    return choices

def get_pubsub_security_choices(request:'any_', form_type:'str'='edit', context:'str'='subscription') -> 'list':
    """ Get filtered security definitions for Django form choices (tuples format).
    """
    definitions = get_pubsub_security_definitions(request, form_type, context)

    out = []
    for item in definitions:
        out.append((item['id'], item['name']))

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_service_list(request):

    response = request.zato.client.invoke('zato.service.get-list', {
        'cluster_id': request.zato.cluster_id,
    })

    services = []
    for item in response.data:
        services.append({
            'service_name': item['name']
        })

    return services

# ################################################################################################################################
# ################################################################################################################################
