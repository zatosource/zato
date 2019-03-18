# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import __main__
import sys

# Python 2/3 compatibiliy
from future.utils import raise_
from six import PY3

if PY3:
    # stdlib
    from importlib import import_module

    def import_string(name):
        name = name.split('.')
        attr_name = name[-1]
        mod_name = '.'.join(name[:-1])
        mod = import_module(mod_name)
        return getattr(mod, attr_name)

else:

# ################################################################################################################################
# ################################################################################################################################

# Code below taken from PEAK under Python Software Foundation License

# ################################################################################################################################
# ################################################################################################################################

    defaultGlobalDict = __main__.__dict__

    def import_string(name, globalDict=defaultGlobalDict):
        """Import an item specified by a string

        Example Usage::

            attribute1 = importString('some.module:attribute1')
            attribute2 = importString('other.module:nested.attribute2')

        'importString' imports an object from a module, according to an
        import specification string: a dot-delimited path to an object
        in the Python package namespace.  For example, the string
        '"some.module.attribute"' is equivalent to the result of
        'from some.module import attribute'.

        For readability of import strings, it's sometimes helpful to use a ':' to
        separate a module name from items it contains.  It's optional, though,
        as 'importString' will convert the ':' to a '.' internally anyway."""

        if ':' in name:
            name = name.replace(':','.')

        parts = filter(None,name.split('.'))
        item = __import__(parts.pop(0), globalDict, globalDict, ['__name__'])

        # Fast path for the common case, where everything is imported already
        for attr in parts:
            try:
                item = getattr(item, attr)
            except AttributeError:
                break   # either there's an error, or something needs importing
        else:
            return item

        # We couldn't get there with just getattrs from the base import.  So now
        # we loop *backwards* trying to import longer names, then shorter, until
        # we find the longest possible name that can be handled with __import__,
        # then loop forward again with getattr.  This lets us give more meaningful
        # error messages than if we only went forwards.
        attrs = []
        exc = None

        try:
            while True:
                try:
                    # Exit as soon as we find a prefix of the original `name`
                    # that's an importable *module* or package
                    item = __import__(name, globalDict, globalDict, ['__name__'])
                    break
                except ImportError:
                    if not exc:
                        # Save the first ImportError, as it's usually the most
                        # informative, especially w/Python < 2.4
                        exc = sys.exc_info()

                    if '.' not in name:
                        # We've backed up all the way to the beginning, so reraise
                        # the first ImportError we got
                        raise_(exc[0], exc[1], exc[2])

                    # Otherwise back up one position and try again
                    parts = name.split('.')
                    attrs.append(parts[-1])
                    name = '.'.join(parts[:-1])
        finally:
            exc = None

        # Okay, the module object is now in 'item', so we can just loop forward
        # to retrieving the desired attribute.
        #
        while attrs:
            attr = attrs.pop()
            try:
                item = getattr(item,attr)
            except AttributeError:
                raise ImportError("%r has no %r attribute" % (item,attr))

        return item

# ################################################################################################################################
# ################################################################################################################################
