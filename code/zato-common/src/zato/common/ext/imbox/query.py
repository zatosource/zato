"""
This module is a modified vendor copy of the Imbox package from https://pypi.org/project/imbox/

The MIT License (MIT)

Copyright (c) 2013 Martin Rusev

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

import datetime


def build_search_query(imap_attribute_lookup, **kwargs):
    query = []
    for name, value in kwargs.items():
        if value is not None:
            if isinstance(value, datetime.date):
                value = value.strftime('%d-%b-%Y')
            if isinstance(value, str) and '"' in value:
                value = value.replace('"', "'")
            query.append(imap_attribute_lookup[name].format(value))

    if query:
        return " ".join(query)

    return "(ALL)"
