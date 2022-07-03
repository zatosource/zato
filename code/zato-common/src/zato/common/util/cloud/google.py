# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.model.google import GoogleAPIDescription
    from zato.common.typing_ import list_

# ################################################################################################################################
# ################################################################################################################################

def get_api_list() -> 'list_[GoogleAPIDescription]':
    """ Returns a list of all the APIs that the Google client library supports.
    """
    # stdlib
    import os
    from operator import itemgetter

    # google-api-client
    from googleapiclient.discovery_cache import DISCOVERY_DOC_DIR as root_dir

    # pysimdjson
    from simdjson import Parser as SIMDJSONParser

    # Zato
    from zato.common.model.google import GoogleAPIDescription
    from zato.common.util.open_ import open_r

    # Response to produce
    out = []

    # A reusable parser
    parser = SIMDJSONParser()

    # .. build a full path to the schema ..
    full_path = os.path.join(root_dir, 'index.json')

    with open_r(full_path) as f:

        # .. read the contents and parse it ..
        index = f.read().encode('utf8')

        # .. parse it ..
        doc = parser.parse(index)

        # .. and extract only the required keys ..
        for item in doc['items']:

            api_id = item.at_pointer('/id')
            api_name = item.at_pointer('/name')
            api_title = item.at_pointer('/title')
            api_version = item.at_pointer('/version')

            desc = GoogleAPIDescription()
            desc.id = api_id
            desc.name = api_name
            desc.title = api_title
            desc.version = api_version

            out.append(desc)

    out.sort(key=itemgetter('title'))

    return out

# ################################################################################################################################
# ################################################################################################################################
