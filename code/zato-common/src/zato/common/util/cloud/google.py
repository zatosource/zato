# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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

    # Zato
    from zato.common.model.google import GoogleAPIDescription
    from zato.common.typing_ import cast_
    from zato.common.util.open_ import open_r
    from zato.common.util.json_ import JSONParser

    # Response to produce
    out = []

    # A reusable parser
    parser = JSONParser()

    # A cache to make it easier to find out which APIs
    # have only non-GA APIs.
    version_cache = {}

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
            desc.title_full = '{} ({})'.format(desc.title, desc.version)

            api_version_entry = version_cache.setdefault(desc.name, []) # type: list
            api_version_entry.append(desc)

            out.append(desc)

    # Go through each API in the cache ..
    for desc_list in version_cache.values():

        # .. if the list of descriptions contains more than one
        # .. we need to remove all the non-GA ones from the output list ..
        if len(desc_list) > 1:
            for item in desc_list:
                item = cast_('GoogleAPIDescription', item)
                if ('alpha' in item.version) or ('beta' in item.version):
                    out.remove(item)

    out.sort(key=itemgetter('title'))

    return out

# ################################################################################################################################
# ################################################################################################################################
