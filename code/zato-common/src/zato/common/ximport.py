# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# What follows is a slight modification of mod_python's modules' importing code
# used under the terms of the following license:

#
#
# Copyright 2004 Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# Originally developed by Gregory Trubetskoy.
#
# $Id: apache.py 468216 2006-10-27 00:54:12Z grahamd $

# stdlib
import os
import imp
import logging
from inspect import getfile

logger = logging.getLogger(__name__)

def import_module(module_name, autoreload=True, path=None):
    """
    Get the module to handle the request. If
    autoreload is on, then the module will be reloaded
    if it has changed since the last import.
    """

    # nlehuen: this is a big lock, we'll have to refine it later to get better performance.
    # For now, we'll concentrate on thread-safety.
    imp.acquire_lock()
    try:

        # Import the module
        if path:
            s = '(Re)importing module [{}] with path set to [{}]'.format(module_name, path)
        else:
            s = '(Re)importing module [{}]'.format(module_name)
        logger.debug(s)

        parent = None
        parts = module_name.split('.')
        for i in range(len(parts)):
            f, p, d = imp.find_module(parts[i], path)
            try:
                mname = ".".join(parts[:i+1])
                module = imp.load_module(mname, f, p, d)
                if parent:
                    setattr(parent,parts[i],module)
                parent = module
            finally:
                if f: f.close()
            if hasattr(module, "__path__"):
                path = module.__path__
                
            #if mtime == 0:
            mtime = module_mtime(module)

            module.__mtime__ = mtime

        if logger.isEnabledFor(logging.DEBUG):
            msg = '(Re)importing module:[{}] from:[{}]'.format(module_name, getfile(module))
            logger.debug(msg)

        return module
    finally:
        imp.release_lock()

def module_mtime(module):
    """Get modification time of module"""
    mtime = 0
    if module.__dict__.has_key("__file__"):

        filepath = module.__file__

        try:
            # this try/except block is a workaround for a Python bug in
            # 2.0, 2.1 and 2.1.1. See
            # http://sourceforge.net/tracker/?group_id=5470&atid=105470&func=detail&aid=422004

            if os.path.exists(filepath):
                mtime = os.path.getmtime(filepath)

            if os.path.exists(filepath[:-1]) :
                mtime = max(mtime, os.path.getmtime(filepath[:-1]))

        except OSError: pass

    return mtime

def resolve_object(module, object_str, arg=None, silent=0):
    """
    This function traverses the objects separated by .
    (period) to find the last one we're looking for:

       From left to right, find objects, if it is
       an unbound method of a class, instantiate the
       class passing the request as single argument

    'arg' is sometimes req, sometimes filter,
    sometimes connection
    """

    obj = module

    for obj_str in  object_str.split('.'):

        parent = obj

        # don't throw attribute errors when silent
        if silent and not hasattr(obj, obj_str):
            return None

        # this adds a little clarity if we have an attriute error
        if obj == module and not hasattr(module, obj_str):
            if hasattr(module, "__file__"):
                s = "module '%s' contains no '%s'" % (module.__file__, obj_str)
                raise AttributeError, s

        obj = getattr(obj, obj_str)

        if hasattr(obj, "im_self") and not obj.im_self:
            # this is an unbound method, its class
            # needs to be instantiated
            instance = parent(arg)
            obj = getattr(instance, obj_str)

    return obj
