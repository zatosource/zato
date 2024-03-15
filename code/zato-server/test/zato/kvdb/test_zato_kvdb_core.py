# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_string
from zato.server.connection.kvdb.api import ObjectCtx, ListRepo
from zato.server.connection.kvdb.core import KVDB

# ################################################################################################################################
# ################################################################################################################################

class ListRepoAPITestCase(TestCase):

    def test_list_internal_create_repo(self):

        repo_name1 = rand_string()
        repo_name2 = rand_string()

        zato_kvdb = KVDB()

        zato_kvdb.internal_create_list_repo(repo_name1)
        zato_kvdb.internal_create_list_repo(repo_name2)

        repo1 = zato_kvdb.get(repo_name1)
        repo2 = zato_kvdb.get(repo_name2)

        self.assertIsInstance(repo1, ListRepo)
        self.assertIsInstance(repo2, ListRepo)

        self.assertIsNot(repo1, repo2)

# ################################################################################################################################

    def test_list_get(self):

        repo_name = rand_string()

        zato_kvdb = KVDB()
        zato_kvdb.internal_create_list_repo(repo_name)

        repo = zato_kvdb.get(repo_name)

        self.assertIsInstance(repo, ListRepo)

# ################################################################################################################################

    def test_list_push_get_object(self):

        repo_name = rand_string()
        object_id = rand_string()

        ctx = ObjectCtx()
        ctx.id = object_id

        zato_kvdb = KVDB()
        zato_kvdb.internal_create_list_repo(repo_name)

        zato_kvdb.append(repo_name, ctx)
        result = zato_kvdb.get_object(repo_name, object_id)

        self.assertIsInstance(result, ObjectCtx)
        self.assertEqual(result.id, object_id)

# ################################################################################################################################

    def test_list_repo_get_list(self):

        id1 = '1-' + rand_string()
        id2 = '2-' + rand_string()
        id3 = '3-' + rand_string()

        id4 = '4-' + rand_string()
        id5 = '5-' + rand_string()
        id6 = '6-' + rand_string()

        id7 = '7-' + rand_string()
        id8 = '8-' + rand_string()
        id9 = '9-' + rand_string()

        id10 = '10-' + rand_string()
        id11 = '11-' + rand_string()
        id12 = '12-' + rand_string()

        ctx1 = ObjectCtx()
        ctx2 = ObjectCtx()
        ctx3 = ObjectCtx()
        ctx4 = ObjectCtx()
        ctx5 = ObjectCtx()
        ctx6 = ObjectCtx()
        ctx7 = ObjectCtx()
        ctx8 = ObjectCtx()
        ctx9 = ObjectCtx()
        ctx10 = ObjectCtx()
        ctx11 = ObjectCtx()
        ctx12 = ObjectCtx()

        ctx1.id = id1
        ctx2.id = id2
        ctx3.id = id3
        ctx4.id = id4
        ctx5.id = id5
        ctx6.id = id6
        ctx7.id = id7
        ctx8.id = id8
        ctx9.id = id9
        ctx10.id = id10
        ctx11.id = id11
        ctx12.id = id12

        repo_name = rand_string()
        zato_kvdb = KVDB()
        zato_kvdb.internal_create_list_repo(repo_name)

        zato_kvdb.append(repo_name, ctx1)
        zato_kvdb.append(repo_name, ctx2)
        zato_kvdb.append(repo_name, ctx3)
        zato_kvdb.append(repo_name, ctx4)
        zato_kvdb.append(repo_name, ctx5)
        zato_kvdb.append(repo_name, ctx6)
        zato_kvdb.append(repo_name, ctx7)
        zato_kvdb.append(repo_name, ctx8)
        zato_kvdb.append(repo_name, ctx9)
        zato_kvdb.append(repo_name, ctx10)
        zato_kvdb.append(repo_name, ctx11)
        zato_kvdb.append(repo_name, ctx12)

        cur_page = 2
        page_size = 3

        results = zato_kvdb.get_list(repo_name, cur_page, page_size)
        result = results['result']

        result0 = result[0] # type: ObjectCtx
        result1 = result[1] # type: ObjectCtx
        result2 = result[2] # type: ObjectCtx

        self.assertEqual(result0.id, id9)
        self.assertEqual(result1.id, id8)
        self.assertEqual(result2.id, id7)

# ################################################################################################################################

    def test_list_repo_delete(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo_name = rand_string()
        zato_kvdb = KVDB()
        zato_kvdb.internal_create_list_repo(repo_name)

        zato_kvdb.append(repo_name, ctx1)
        zato_kvdb.append(repo_name, ctx2)

        deleted_ctx = zato_kvdb.delete(repo_name, id1)
        self.assertIs(ctx1, deleted_ctx)

        try:
            zato_kvdb.get_object(repo_name, id1)
        except KeyError as e:
            self.assertEqual(e.args[0], 'Object not found `{}`'.format(id1))
        else:
            self.fail('KeyError should have been raised because object has been deleted')

# ################################################################################################################################

    def test_list_repo_clear(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo_name = rand_string()
        zato_kvdb = KVDB()
        zato_kvdb.internal_create_list_repo(repo_name)

        zato_kvdb.append(repo_name, ctx1)
        zato_kvdb.append(repo_name, ctx2)

        zato_kvdb.remove_all(repo_name)

        self.assertEqual(zato_kvdb.get_size(repo_name), 0)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
