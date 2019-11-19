# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import os
import socket

# Zato
from zato.common.util import get_current_user

# Python 2/3 compatibility
from six import PY2

# ################################################################################################################################

logger = logging.getLogger(__name__)

logger_bzr = logging.getLogger('bzr')
logger_bzr.setLevel(logging.WARN)

logger_sh = logging.getLogger('sh.command')
logger_sh.setLevel(logging.WARN)

# ################################################################################################################################

# We use Bazaar under Zato 3.0 with Python 2.7. Any newer version of Zato, or Zato 3.0 with Python 3.x, uses git.

# ################################################################################################################################
# ################################################################################################################################

class _BaseRepoManager(object):
    def __init__(self, repo_location='.'):
        self.repo_location = os.path.abspath(os.path.expanduser(repo_location))

# ################################################################################################################################
# ################################################################################################################################

class BazaarRepoManager(_BaseRepoManager):

    def ensure_repo_consistency(self):
        """ Makes sure the self.repo_location directory is a Bazaar branch.
        The repo and Bazaar branch will be created if they don't already exist.
        Any unknown or modified files will be commited to the branch.
        Also, 'bzr whoami' will be set to the current user so that all commands
        can be traced back to an actual person (assuming everyone has their
        own logins).
        """
        # Bazaar
        import bzrlib
        from bzrlib.branch import Branch
        from bzrlib.bzrdir import BzrDir
        from bzrlib.workingtree import WorkingTree

        try:
            BzrDir.open(self.repo_location)
        except bzrlib.errors.NotBranchError:
            BzrDir.create_branch_convenience(self.repo_location)

        c = Branch.open(self.repo_location).get_config_stack()
        c.set('email', '{}@{}'.format(get_current_user(), socket.getfqdn()))

        self.tree = WorkingTree.open(self.repo_location)
        delta = self.tree.changes_from(self.tree.basis_tree(), want_unversioned=True)

        logger.debug('tree `{}`'.format(self.tree))
        logger.debug('delta `{}`'.format(delta))

        for file_info in delta.unversioned:
            logger.debug('unversioned [{}]'.format(file_info))
            file_name = file_info[0]
            self.tree.add(file_name)

        if delta.unversioned:
            self.tree.commit('Added new unversioned files')
        else:
            logger.debug('No unversioned files found')

        if delta.modified:
            self.tree.commit('Committed modified files')
        else:
            logger.debug('No modified files found')

# ################################################################################################################################
# ################################################################################################################################

class GitRepoManager(_BaseRepoManager):
    def ensure_repo_consistency(self):

        # Use sh for git commands
        import sh

        # Always work in the same directory as the repository is in
        sh.cd(self.repo_location)

        # (Re-)init the repository
        sh.git.init(self.repo_location)

        # Set user info
        current_user = get_current_user()
        sh.git.config('user.name', current_user)
        sh.git.config('user.email', '{}@{}'.format(current_user, socket.getfqdn()))

        # Default branch is called 'main'
        sh.git.checkout('-B', 'main')

        # Add all files
        sh.git.add('-A', self.repo_location)

        has_channges = 'nothing to commit' not in sh.git.status()

        # And commit changes if there are any
        if has_channges:
            sh.git.commit('-m', 'Committing latest changes')

# ################################################################################################################################
# ################################################################################################################################

if PY2:
    RepoManager = BazaarRepoManager
else:
    RepoManager = GitRepoManager

# ################################################################################################################################
# ################################################################################################################################
