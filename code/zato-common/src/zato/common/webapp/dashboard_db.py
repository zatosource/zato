# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite database of Dashboard, which holds the tables of Django - the users of Dashboard, their sessions
# and their preferences. Each Dashboard keeps the file in its own configuration directory.

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

    # Dummy assignments to satisfy type checkers
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The Django backend of the database of Dashboard
Django_Engine = 'django.db.backends.sqlite3'

# The name of the database file of Dashboard
DB_File_Name = 'zato.db'

# The name of the directory of Dashboard in an environment, next to the directories of its servers
Dashboard_Dir_Name = 'web-admin'

# How long a connection waits for a lock that another process holds on the database file, in seconds
Busy_Timeout_Seconds = 5.0

# ################################################################################################################################
# ################################################################################################################################

def get_dashboard_db_path(dashboard_dir:'str') -> 'str':
    """ Returns the path to the database file of the Dashboard in the given directory.
    """
    out = os.path.join(dashboard_dir, 'config', 'repo', DB_File_Name)
    return out

# ################################################################################################################################

def get_environment_dashboard_db_path(server_dir:'str') -> 'str':
    """ Returns the path to the database file of the Dashboard of the environment
    that the given server directory belongs to.
    """
    dashboard_dir = os.path.join(server_dir, '..', Dashboard_Dir_Name)
    dashboard_dir = os.path.normpath(dashboard_dir)

    out = get_dashboard_db_path(dashboard_dir)
    return out

# ################################################################################################################################

def get_django_database(dashboard_dir:'str') -> 'stranydict':
    """ Returns the entry of Django's DATABASES setting for the database of the Dashboard in the given directory.
    """
    out:'stranydict' = {
        'ENGINE': Django_Engine,
        'NAME': get_dashboard_db_path(dashboard_dir),
        'OPTIONS': {'timeout': Busy_Timeout_Seconds},
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
