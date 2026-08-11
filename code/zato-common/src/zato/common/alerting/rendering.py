# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What every notification says comes from Jinja templates on disk, not from strings
# in code - the defaults ship with zato-common and each environment gets its own
# copy under the server's config/repo/alert-templates when it is created, so editing
# a file there changes the very next alert. The engine renders through here at
# dispatch time, one template per channel - Slack and Teams texts, email and digest
# subjects and bodies, and the whole JSON body of the plain webhook.

from __future__ import annotations

# stdlib
import os

# Jinja
from jinja2 import Environment, FileSystemLoader

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The directory each server keeps its own copy of the templates under,
# relative to the server's config/repo directory.
Template_Dir_Name = 'alert-templates'

# The templates that ship - one file per channel and purpose.
Template_Slack          = 'slack'
Template_Teams          = 'teams'
Template_Email_Subject  = 'email-subject'
Template_Email_Body     = 'email-body'
Template_Digest_Subject = 'digest-subject'
Template_Digest_Body    = 'digest-body'
Template_Webhook        = 'webhook'

template_names = [
    Template_Slack,
    Template_Teams,
    Template_Email_Subject,
    Template_Email_Body,
    Template_Digest_Subject,
    Template_Digest_Body,
    Template_Webhook,
]

# The extension every template file carries on disk.
_template_suffix = '.j2'

# ################################################################################################################################
# ################################################################################################################################

def get_default_template_dir() -> 'str':
    """ Where the shipped default templates live - the source create_server copies
    into each new environment, and what renders when no per-server directory is given.
    """
    out = os.path.join(os.path.dirname(__file__), 'templates')
    return out

# ################################################################################################################################

def render_alert_template(name:'str', context:'stranydict', template_dir:'str'='') -> 'str':
    """ Renders one alert template by name with the given context - from the server's
    own directory when one is given, from the shipped defaults otherwise.
    """
    if not template_dir:
        template_dir = get_default_template_dir()

    # Block tags own their lines, so conditional lines vanish whole when their
    # condition does not hold, instead of leaving blank lines behind.
    environment = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

    template = environment.get_template(name + _template_suffix)
    rendered = template.render(context)

    # The trailing newline is the file's own, not part of the message
    out = rendered.rstrip('\n')
    return out

# ################################################################################################################################
# ################################################################################################################################
