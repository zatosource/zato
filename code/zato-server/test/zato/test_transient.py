# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.transient.core import ObjectCtx, TransientRepository

# ################################################################################################################################
# ################################################################################################################################

class TransientRepositoryTestCase(TestCase):

    def test_repo_init(self):

        name = rand_string()
        max_size = rand_int()

        repo = TransientRepository(name, max_size)

        self.assertEqual(repo.name, name)
        self.assertEqual(repo.max_size, max_size)

# ################################################################################################################################

    def test_repo_push_max_size(self):

        name = rand_string()
        max_size = 2

        repo = TransientRepository(name, max_size)

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

        repo = TransientRepository()

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

        repo = TransientRepository()

        repo.push(ctx1)
        repo.push(ctx2)

        repo.delete(id1)

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

        repo = TransientRepository()

        repo.push(ctx1)
        repo.push(ctx2)

        repo.clear()

        self.assertEqual(repo.get_size(), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
