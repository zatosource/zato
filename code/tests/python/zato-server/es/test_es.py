# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import All_Letters, get_client
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from es_server import ESServer
    ESServer = ESServer

# ################################################################################################################################
# ################################################################################################################################

def test_ping(es_server:'ESServer') -> 'None':
    """ The connection can be established and the server responds to an info request,
    which is the same call the dashboard's ping button makes.
    """
    client = get_client(es_server, 'test_ping')
    _ = client.info()

# ################################################################################################################################

def test_index_search_update_delete(es_server:'ESServer') -> 'None':
    """ A full round trip on one index, with letters from four alphabets in the document contents.
    Index names must be lowercase in Elasticsearch, which is why the Unicode letters
    live in the documents rather than in the index name.
    """
    client = get_client(es_server, 'test_index_search_update_delete')

    index_name = 'orders-' + CryptoManager.generate_hex_string().lower()

    # Index a document whose contents use all four alphabets ..
    document = {
        'order_id': 123,
        'customer_name': 'Test customer ' + All_Letters,
        'status': 'ready',
    }
    index_response = client.index(index=index_name, id='order-123', document=document)
    assert index_response['result'] == 'created'

    # .. read it back by ID and confirm the Unicode round trip was exact ..
    found = client.get(index=index_name, id='order-123')
    assert found['_source']['customer_name'] == 'Test customer ' + All_Letters
    assert found['_source']['status'] == 'ready'

    # .. a search must find it too once the index is refreshed ..
    _ = client.indices.refresh(index=index_name)
    search_response = client.search(index=index_name, query={'match': {'order_id': 123}})
    assert search_response['hits']['total']['value'] == 1

    # .. update it, again with all the alphabets in the new value ..
    _ = client.update(index=index_name, id='order-123', doc={'status': 'shipped ' + All_Letters})

    found = client.get(index=index_name, id='order-123')
    assert found['_source']['status'] == 'shipped ' + All_Letters

    # .. delete it ..
    delete_response = client.delete(index=index_name, id='order-123')
    assert delete_response['result'] == 'deleted'

    # .. and confirm it is gone.
    assert not client.exists(index=index_name, id='order-123')

    # Clean up the index itself
    _ = client.indices.delete(index=index_name)

# ################################################################################################################################

def test_multi_line_address_list(es_server:'ESServer') -> 'None':
    """ An address list with one URL per line is split into per-line addresses
    instead of being handed to the client as one unparseable string.
    """
    one_address = f'{es_server.scheme}://{es_server.host}:{es_server.port}'
    address_list = one_address + '\n' + one_address
    client = get_client(es_server, 'test_multi_line_address_list', address_list=address_list)

    # The connection built out of a multi-line list is fully usable
    _ = client.info()

# ################################################################################################################################
# ################################################################################################################################
