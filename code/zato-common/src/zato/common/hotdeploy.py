# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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