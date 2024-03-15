# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.kvdb.api import ObjectCtx, ListRepo


# ################################################################################################################################
# ################################################################################################################################

sync_threshold = 1
sync_interval  = 1

# ################################################################################################################################
# ################################################################################################################################

class TransientRepositoryTestCase(TestCase):

    def test_repo_init(self):

        name = rand_string()
        data_path = rand_string()
        max_size = rand_int()

        repo = ListRepo(name, data_path, max_size)

        self.assertEqual(repo.name, name)
        self.assertEqual(repo.data_path, data_path)
        self.assertEqual(repo.max_size, max_size)

# ################################################################################################################################

    def test_repo_push_max_size(self):

        name = rand_string()
        data_path = rand_string()
        max_size = 2

        repo = ListRepo(name, data_path, max_size)

        # Push more object than the max size allows ..
        for _x in range(max_size + 1):
            repo.append(None)

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

        repo = ListRepo()

        repo.append(ctx1)
        repo.append(ctx2)
        repo.append(ctx3)

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

        repo = ListRepo()

        repo.append(ctx1)
        repo.append(ctx2)

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

        repo = ListRepo()

        repo.append(ctx1)
        repo.append(ctx2)

        repo.remove_all()

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

        repo = ListRepo()

        repo.append(ctx1)
        repo.append(ctx2)
        repo.append(ctx3)
        repo.append(ctx4)
        repo.append(ctx5)
        repo.append(ctx6)
        repo.append(ctx7)
        repo.append(ctx8)
        repo.append(ctx9)
        repo.append(ctx10)
        repo.append(ctx11)
        repo.append(ctx12)

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

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
