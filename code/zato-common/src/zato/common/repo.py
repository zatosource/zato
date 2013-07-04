# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, os, socket

# Bazaar
import bzrlib
from bzrlib.branch import Branch
from bzrlib.bzrdir import BzrDir
from bzrlib.workingtree import WorkingTree

# Zato
from zato.common.util import get_current_user

logger = logging.getLogger(__name__)

class RepoManager(object):
    def __init__(self, repo_location='.'):
        self.repo_location = os.path.abspath(repo_location)

    def ensure_repo_consistency(self):
        """ Makes sure the self.repo_location directory is a Bazaar branch.
        The repo and Bazaar branch will be created if they don't already exist.
        Any unknown or modified files will be commited to the branch.
        Also, 'bzr whoami' will be set to the current user so that all commands
        can be traced back to an actual person (assuming everyone has their
        own logins).
        """

        try:
            BzrDir.open(self.repo_location)
        except bzrlib.errors.NotBranchError:
            logger.info('Location [{}] is not a Bazaar branch. Will turn it into one.'.format(self.repo_location))
            BzrDir.create_branch_convenience(self.repo_location)
            
        c = Branch.open(self.repo_location).get_config_stack()
        c.set('email', '{}@{}'.format(get_current_user(), socket.getfqdn()))

        self.tree = WorkingTree.open(self.repo_location)
        delta = self.tree.changes_from(self.tree.basis_tree(), want_unversioned=True)

        logger.debug('tree [{}]'.format(self.tree))
        logger.debug('delta [{}]'.format(delta))

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
