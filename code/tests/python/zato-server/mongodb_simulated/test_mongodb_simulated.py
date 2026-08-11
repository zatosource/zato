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
    from containers import MongoDBServer
    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

# The database all the tests below use
_test_db_name = 'zato_test_mongodb_simulated'

# ################################################################################################################################
# ################################################################################################################################

def test_ping(mongodb_server:'MongoDBServer') -> 'None':
    """ The connection can be established over TCP and the simulator responds to a ping command.
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

def test_find_many(mongodb_server:'MongoDBServer') -> 'None':
    """ A find with a shared attribute returns all the matching documents and nothing else.
    """
    client = get_client(mongodb_server, 'test_find_many')

    db = client[_test_db_name]

    collection_name = 'invoices_' + CryptoManager.generate_hex_string()
    collection = db[collection_name]

    # Two documents share a status and one does not ..
    _ = collection.insert_one({'invoice_id': 1, 'status': 'paid'})
    _ = collection.insert_one({'invoice_id': 2, 'status': 'paid'})
    _ = collection.insert_one({'invoice_id': 3, 'status': 'overdue'})

    # .. the shared status returns both of its documents ..
    paid_invoices = list(collection.find({'status': 'paid'}))
    paid_count = len(paid_invoices)

    assert paid_count == 2, f'Expected two paid invoices, got: {paid_invoices}'

    # .. and deleting by the shared status removes both.
    delete_result = collection.delete_many({'status': 'paid'})
    assert delete_result.deleted_count == 2

    remaining_invoices = list(collection.find({}))
    remaining_count = len(remaining_invoices)

    assert remaining_count == 1, f'Expected one invoice left, got: {remaining_invoices}'
    assert remaining_invoices[0]['status'] == 'overdue'

# ################################################################################################################################
# ################################################################################################################################
