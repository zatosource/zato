# vim: set fileencoding=utf-8 :
"""
~~~~~~~
Classes
~~~~~~~

Contains :class:`DictableModel` that can be used as a base class for
:meth:`sqlalchemy.ext.declarative_base`.

"""

from __future__ import absolute_import, division

"""
This module is a modified vendor copy of the DictAlchemy package from https://pypi.org/project/dictalchemy/

The MIT License (MIT)

Copyright (c) 2015 Daniel Holmstrom

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from dictalchemy import utils


class DictableModel(object):
    """Can be used as a base class for :meth:`sqlalchemy.ext.declarative`

    Contains the methods :meth:`DictableModel.__iter__`,
    :meth:`DictableModel.asdict` and :meth:`DictableModel.fromdict`.

    :ivar dictalchemy_exclude: List of properties that should always be \
            excluded.
    :ivar dictalchemy_exclude_underscore: If True properties starting with an \
            underscore will always be excluded.
    :ivar dictalchemy_fromdict_allow_pk: If True the primary key can be \
            updated by :meth:`DictableModel.fromdict`.
    :ivar dictalchemy_asdict_include: List of properties that should always \
            be included when calling :meth:`DictableModel.asdict`
    :ivar dictalchemy_fromdict_include: List of properties that should always \
            be included when calling :meth:`DictableModel.fromdict`

    """

    asdict = utils.asdict

    fromdict = utils.fromdict

    __iter__ = utils.iter
