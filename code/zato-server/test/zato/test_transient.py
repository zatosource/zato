# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.transient.core import ObjectCtx, TransientAPI, TransientListRepo

# ################################################################################################################################
# ################################################################################################################################

class TransientRepositoryTestCase(TestCase):

    def test_repo_init(self):

        name = rand_string()
        max_size = rand_int()

        repo = TransientListRepo(name, max_size)

        self.assertEqual(repo.name, name)
        self.assertEqual(repo.max_size, max_size)

# ################################################################################################################################

    def test_repo_push_max_size(self):

        name = rand_string()
        max_size = 2

        repo = TransientListRepo(name, max_size)

        # Push more object than the max size allows ..
        for x in range(max_size + 1):
            repo.push(None)

        # .. we have reached the maximum size but it should not be greater than that.
        self.assertEqual(repo.get_size(), max_size)

# ################################################################################################################################

    def test_repo_get(self):

        id1 = rand_string()
        id2 = rand_string()
        id3 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        ctx3 = ObjectCtx()
        ctx3.id = id3

        repo = TransientListRepo()

        repo.push(ctx1)
        repo.push(ctx2)
        repo.push(ctx3)

        given_ctx = repo.get(id1)
        self.assertIs(given_ctx, ctx1)

# ################################################################################################################################

    def test_repo_delete(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo = TransientListRepo()

        repo.push(ctx1)
        repo.push(ctx2)

        deleted_ctx = repo.delete(id1)
        self.assertIs(ctx1, deleted_ctx)

        try:
            repo.get(id1)
        except KeyError as e:
            self.assertEqual(e.args[0], 'Object not found `{}`'.format(id1))
        else:
            self.fail('KeyError should have been raised because object has been deleted')

# ################################################################################################################################

    def test_repo_clear(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo = TransientListRepo()

        repo.push(ctx1)
        repo.push(ctx2)

        repo.clear()

        self.assertEqual(repo.get_size(), 0)

# ################################################################################################################################

    def test_repo_get_list(self):

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

        repo = TransientListRepo()

        repo.push(ctx1)
        repo.push(ctx2)
        repo.push(ctx3)
        repo.push(ctx4)
        repo.push(ctx5)
        repo.push(ctx6)
        repo.push(ctx7)
        repo.push(ctx8)
        repo.push(ctx9)
        repo.push(ctx10)
        repo.push(ctx11)
        repo.push(ctx12)

        cur_page = 2
        page_size = 3

        results = repo.get_list(cur_page, page_size)
        result = results['result']

        result0 = result[0] # type: ObjectCtx
        result1 = result[1] # type: ObjectCtx
        result2 = result[2] # type: ObjectCtx

        self.assertEqual(result0.id, id9)
        self.assertEqual(result1.id, id8)
        self.assertEqual(result2.id, id7)

# ################################################################################################################################
# ################################################################################################################################

class TransientAPITestCase(TestCase):

    def test_internal_create_repo(self):

        repo_name1 = rand_string()
        repo_name2 = rand_string()

        transient_api = TransientAPI()

        transient_api.internal_create_list_repo(repo_name1)
        transient_api.internal_create_list_repo(repo_name2)

        repo1 = transient_api.get(repo_name1)
        repo2 = transient_api.get(repo_name2)

        self.assertIsInstance(repo1, TransientListRepo)
        self.assertIsInstance(repo2, TransientListRepo)

        self.assertIsNot(repo1, repo2)

# ################################################################################################################################

    def test_get(self):

        repo_name = rand_string()

        transient_api = TransientAPI()
        transient_api.internal_create_list_repo(repo_name)

        repo = transient_api.get(repo_name)

        self.assertIsInstance(repo, TransientListRepo)

# ################################################################################################################################

    def test_push_get_object(self):

        repo_name = rand_string()
        object_id = rand_string()

        ctx = ObjectCtx()
        ctx.id = object_id

        transient_api = TransientAPI()
        transient_api.internal_create_list_repo(repo_name)

        transient_api.push(repo_name, ctx)
        result = transient_api.get_object(repo_name, object_id)

        self.assertIsInstance(result, ObjectCtx)
        self.assertEqual(result.id, object_id)

# ################################################################################################################################

    def test_repo_get_list(self):

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
        transient_api = TransientAPI()
        transient_api.internal_create_list_repo(repo_name)

        transient_api.push(repo_name, ctx1)
        transient_api.push(repo_name, ctx2)
        transient_api.push(repo_name, ctx3)
        transient_api.push(repo_name, ctx4)
        transient_api.push(repo_name, ctx5)
        transient_api.push(repo_name, ctx6)
        transient_api.push(repo_name, ctx7)
        transient_api.push(repo_name, ctx8)
        transient_api.push(repo_name, ctx9)
        transient_api.push(repo_name, ctx10)
        transient_api.push(repo_name, ctx11)
        transient_api.push(repo_name, ctx12)

        cur_page = 2
        page_size = 3

        results = transient_api.get_list(repo_name, cur_page, page_size)
        result = results['result']

        result0 = result[0] # type: ObjectCtx
        result1 = result[1] # type: ObjectCtx
        result2 = result[2] # type: ObjectCtx

        self.assertEqual(result0.id, id9)
        self.assertEqual(result1.id, id8)
        self.assertEqual(result2.id, id7)

# ################################################################################################################################

    def test_repo_delete(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo_name = rand_string()
        transient_api = TransientAPI()
        transient_api.internal_create_list_repo(repo_name)

        transient_api.push(repo_name, ctx1)
        transient_api.push(repo_name, ctx2)

        deleted_ctx = transient_api.delete(repo_name, id1)
        self.assertIs(ctx1, deleted_ctx)

        try:
            transient_api.get_object(repo_name, id1)
        except KeyError as e:
            self.assertEqual(e.args[0], 'Object not found `{}`'.format(id1))
        else:
            self.fail('KeyError should have been raised because object has been deleted')

# ################################################################################################################################

    def test_repo_clear(self):

        id1 = rand_string()
        id2 = rand_string()

        ctx1 = ObjectCtx()
        ctx1.id = id1

        ctx2 = ObjectCtx()
        ctx2.id = id2

        repo_name = rand_string()
        transient_api = TransientAPI()
        transient_api.internal_create_list_repo(repo_name)

        transient_api.push(repo_name, ctx1)
        transient_api.push(repo_name, ctx2)

        transient_api.clear(repo_name)

        self.assertEqual(transient_api.get_size(repo_name), 0)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
