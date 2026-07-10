# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# PyMongo
from pymongo.errors import OperationFailure

# Zato
from common import All_Letters, get_client
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import MongoDBServer
    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

# The database all the tests below use
_test_db_name = 'zato_test_mongodb'

# ################################################################################################################################
# ################################################################################################################################

def test_ping(mongodb_server:'MongoDBServer') -> 'None':
    """ The connection can be established and the server responds to a ping command.
    """
    client = get_client(mongodb_server, 'test_ping')
    _ = client.admin.command('ping')

# ################################################################################################################################

def test_insert_find_update_delete(mongodb_server:'MongoDBServer') -> 'None':
    """ A full round trip on one collection, with letters from four alphabets
    in the collection name and in the document contents.
    """
    client = get_client(mongodb_server, 'test_insert_find_update_delete')

    db = client[_test_db_name]

    collection_name = 'orders_' + All_Letters + '_' + CryptoManager.generate_hex_string()
    collection = db[collection_name]

    # Insert a document whose contents use all four alphabets ..
    document = {
        'order_id': 123,
        'customer_name': 'Test customer ' + All_Letters,
        'status': 'ready',
    }
    insert_result = collection.insert_one(document)

    # .. find it back and confirm the Unicode round trip was exact ..
    found = collection.find_one({'order_id': 123})
    assert found is not None
    assert found['_id'] == insert_result.inserted_id
    assert found['customer_name'] == 'Test customer ' + All_Letters
    assert found['status'] == 'ready'

    # .. update it, again with all the alphabets in the new value ..
    update_result = collection.update_one({'order_id': 123}, {'$set': {'status': 'shipped ' + All_Letters}})
    assert update_result.modified_count == 1

    found = collection.find_one({'order_id': 123})
    assert found is not None
    assert found['status'] == 'shipped ' + All_Letters

    # .. delete it ..
    delete_result = collection.delete_one({'order_id': 123})
    assert delete_result.deleted_count == 1

    # .. and confirm it is gone.
    found = collection.find_one({'order_id': 123})
    assert found is None

# ################################################################################################################################

def test_multi_line_server_list(mongodb_server:'MongoDBServer') -> 'None':
    """ A server list with one host:port pair per line is split into per-line seeds.
    Both lines point at the same standalone server because a standalone accepts
    a single distinct seed only - the point here is that a multi-line value is parsed
    line by line instead of being handed to the client as one unparseable string.
    """
    one_seed = f'{mongodb_server.host}:{mongodb_server.port}'
    server_list = one_seed + '\n' + one_seed
    client = get_client(mongodb_server, 'test_multi_line_server_list', server_list=server_list)

    # The two identical lines must have collapsed into the one seed the client knows about ..
    seeds = client.topology_description.server_descriptions()
    assert len(seeds) == 1

    # .. and the connection is fully usable.
    _ = client.admin.command('ping')

# ################################################################################################################################

def test_wrong_password(mongodb_server:'MongoDBServer') -> 'None':
    """ A connection with a wrong password must fail to authenticate.
    """
    client = get_client(mongodb_server, 'test_wrong_password', secret='wrong-password-on-purpose')

    with pytest.raises(OperationFailure):
        _ = client.admin.command('ping')

# ################################################################################################################################
# ################################################################################################################################
