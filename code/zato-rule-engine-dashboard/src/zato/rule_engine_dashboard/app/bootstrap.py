# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.rule_engine_dashboard.app.user_rules import Root_Username

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

Env_Admin_Password = 'Zato_Rule_Engine_Dashboard_Admin_Password'

# The Django settings module this application runs with
_settings_module = 'zato.rule_engine_dashboard.app.settings'

# ################################################################################################################################
# ################################################################################################################################

def setup_django() -> 'None':
    """ Points Django at this application's settings and initializes it. Idempotent.
    """
    # Django
    import django
    from django.apps import apps

    _ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', _settings_module)

    # A second call to django.setup would raise, hence the readiness check first
    if not apps.ready:
        django.setup()

# ################################################################################################################################

def create_tables() -> 'None':
    """ Creates Django's own tables in the application's database if they are not there yet.
    Despite the name, migrate is Django's only table-creation mechanism - nothing is migrated
    from anywhere and every start after the first one is a no-op. The run_syncdb flag also
    creates the tables of this application's own models, which carry no migration files.
    """
    # Django
    from django.core.management import call_command

    _ = call_command('migrate', run_syncdb=True, interactive=False, verbosity=0)

# ################################################################################################################################

def ensure_root_admin() -> 'None':
    """ Creates the root account if it does not exist yet. Idempotent.
    """
    # Django
    from django.contrib.auth.models import User

    # The account already exists, so there is nothing to do ..
    if User.objects.filter(username=Root_Username).exists():
        logger.info('Root account `%s` already exists', Root_Username)
        return

    # .. otherwise, the password has to be configured explicitly ..
    if password := os.environ.get(Env_Admin_Password):
        pass
    else:
        raise Exception(f'Cannot create the `{Root_Username}` account - set the password in {Env_Admin_Password}')

    # .. and the account comes into being now.
    user:'any_' = User(username=Root_Username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    logger.info('Created the root account `%s`', Root_Username)

# ################################################################################################################################

def bootstrap() -> 'None':
    """ Everything the application needs before it can serve anyone - Django itself,
    its tables and the root account.
    """
    setup_django()
    create_tables()
    ensure_root_admin()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    bootstrap()

# ################################################################################################################################
# ################################################################################################################################
