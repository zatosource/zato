# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import zipfile
from traceback import format_exc

# Zato
from zato.common.util import TRACE1

logger = logging.getLogger("zato.common.hotdeploy")

forbidden_prefix = ["/", ".."]

def validate_egg(stream):
    try:
        # XXX: Add closing of the zip_file
        zip_file = zipfile.ZipFile(stream)
    except Exception:
        logger.error("Caught an exception [%s]" % format_exc())
    else:
        for zip_info in zip_file.infolist():
            logger.log(TRACE1, "zip_info.filename [%s]" % zip_info.filename)

            for prefix in forbidden_prefix:
                if zip_info.filename.startswith(prefix):
                    msg = "zip_info.filename [%s] must not start with [%s]"  % (zip_info.filename, prefix)
                    logger.error(msg)
                    return False
        return True

def get_pkg_info(pkg_info):
    info = {}
    attrs = ("Name", "Version")

    for line in pkg_info.split("\n"):
        line = line.split(":")
        for attr in attrs:
            if line[0] == attr:
                info[attr] = line[1].strip()
    return info