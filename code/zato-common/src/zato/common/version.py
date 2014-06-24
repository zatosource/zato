# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ##############################################################################
# Version
# ##############################################################################

major = 2
minor = 0
micro = 'pre0'
revision = '$Revision$'.split()[1][:8]

class VersionInfo(object):

    @property
    def version_raw(self):
        return '{}.{}.{}.rev-{}'.format(major, minor, micro, revision)

    @property
    def version(self):
        return 'Zato {}'.format(self.version_raw)

version_info = VersionInfo()
