# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.common.rule_engine.demo_data import seed_demo_definitions
from zato.common.rule_engine.sql.constants import Definition_Type_Decision_Table, Definition_Type_Ruleset, \
    Definition_Type_Test_Set, Definition_Type_Vocabulary
from zato.common.util.logging_ import count_text
from zato.rule_engine_dashboard.app.storage import get_backend, get_manager, init_storage
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

# Set in an environment that brings its own definitions, a test suite above all,
# so that the screens open on that content alone and on nothing else.
Env_Skip_Demo_Data = 'Zato_Rule_Engine_Dashboard_Skip_Demo_Data'

# The Django settings module this application runs with
_settings_module = 'zato.rule_engine_dashboard.app.settings'

# Every kind of definition the screens open on, with the noun the startup inventory calls it by.
_definition_kinds = [
    (Definition_Type_Ruleset,        'ruleset',        'rulesets'),
    (Definition_Type_Vocabulary,     'vocabulary',     'vocabularies'),
    (Definition_Type_Decision_Table, 'decision table', 'decision tables'),
    (Definition_Type_Test_Set,       'test set',       'test sets'),
]

# How many definitions of one kind the startup inventory names one by one.
_inventory_limit = 1_000

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

def seed_demo() -> 'None':
    """ Fills a brand-new environment with the demo definitions. Idempotent - an environment
    that already holds definitions of its own is left alone.
    """
    # An environment that says it brings its own definitions starts out empty
    if Env_Skip_Demo_Data in os.environ:
        logger.info('Demo data is turned off in %s, nothing to seed', Env_Skip_Demo_Data)
        return

    seed_demo_definitions(get_backend(), get_manager())

# ################################################################################################################################

def log_contents() -> 'None':
    """ The inventory of what the store holds when the application starts serving - what
    the screens will show, named kind by kind so an empty screen is never a mystery.
    """
    backend = get_backend()

    for object_type, singular, plural in _definition_kinds:
        records = backend.definitions.list(object_type=object_type, limit=_inventory_limit)
        records_text = count_text(len(records), singular, plural)

        logger.info('Rule engine storage holds %s', records_text)

        for record in records:
            logger.info('.. `%s` (id=%s, current version %s, live version %s)', record.name, record.id,
                record.current_version, record.live_version)

# ################################################################################################################################

def bootstrap() -> 'None':
    """ Everything the application needs before it can serve anyone - Django itself,
    its tables, the root account, the rule engine's own storage and what a new environment starts with.
    """
    setup_django()
    create_tables()
    ensure_root_admin()
    init_storage()
    seed_demo()
    log_contents()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    bootstrap()

# ################################################################################################################################
# ################################################################################################################################
