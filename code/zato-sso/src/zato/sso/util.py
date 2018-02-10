# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from platform import processor

# passlib
from passlib.registry import get_crypt_handler
from passlib.utils import timer

# py-cpuinfo
from cpuinfo import get_cpu_info

# Uses code deriver from Passlib https://bitbucket.org/ecollins/passlib

"""
License for Passlib
===================
Passlib is (c) `Assurance Technologies <http://www.assurancetechnologies.com>`_,
and is released under the `BSD license <http://www.opensource.org/licenses/bsd-license.php>`_::

    Passlib
    Copyright (c) 2008-2017 Assurance Technologies, LLC.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

    * Neither the name of Assurance Technologies, nor the names of the
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# Taken from https://bitbucket.org/ecollins/passlib/raw/default/choose_rounds.py
def get_hash_rounds_info(hash_algo='pbkdf2_sha512', target=200):
    """ Returns the number of rounds required for a single password verification
    using hash_algo to take target milliseconds on current CPU.
    """
    target = target / 1000.0
    hasher = get_crypt_handler(hash_algo)

    if hasher.rounds_cost == 'log2':
        # time cost varies logarithmically with rounds parameter,
        # so speed = (2**rounds) / elapsed
        def rounds_to_cost(rounds):
            return 2 ** rounds
        def cost_to_rounds(cost):
            return math.log(cost, 2)
    elif hasher.rounds_cost == 'linear':
        rounds_to_cost = cost_to_rounds = lambda value: value
    else:
        raise ValueError('Don\'t know how to handle hasher.rounds_cost `{}`'.format(hasher.rounds_cost))

    def clamp_rounds(rounds):
        """ Convert float rounds to int value, clamped to hasher's limits.
        """
        if hasher.max_rounds and rounds > hasher.max_rounds:
            rounds = hasher.max_rounds
        rounds = int(rounds)
        if getattr(hasher, '_avoid_even_rounds', False):
            rounds |= 1
        return max(hasher.min_rounds, rounds)

    def average(seq):
        if not hasattr(seq, '__length__'):
            seq = tuple(seq)
        return sum(seq) / len(seq)

    def estimate_iters_per_sec(rounds):
        """ Estimate performance in interations/s using specified # of rounds.
        """
        secret = '3.14159 26535 89793 23846' # π number
        hash = hasher.using(rounds=rounds).hash(secret)
        def helper():
            start = timer()
            hasher.verify(secret, hash)
            return timer() - start
        elapsed = min(average(helper() for _ in range(4)) for _ in range(4))
        return rounds_to_cost(rounds) / elapsed

    #---------------------------------------------------------------
    # Get rough estimate of performance using fraction of default_rounds
    # (so we don't take crazy long amounts of time on slow systems)
    #---------------------------------------------------------------
    rounds = clamp_rounds(cost_to_rounds(.5 * rounds_to_cost(hasher.default_rounds)))
    iters_per_sec = estimate_iters_per_sec(rounds)

    #---------------------------------------------------------------
    # Re-do estimate using previous result,
    # to get more accurate sample using a larger number of rounds.
    #---------------------------------------------------------------
    for _ in range(2):
        rounds = clamp_rounds(cost_to_rounds(iters_per_sec * target))
        iters_per_sec = estimate_iters_per_sec(rounds)

    # Actual value to use in password hashing
    rounds = cost_to_rounds(iters_per_sec * target)

    # Metadata about current CPU the computation was run on
    cpu_info = get_cpu_info()

    return {
        'iters_per_sec': int(iters_per_sec),
        'rounds': int(rounds),
        'cpu_info': {
            'vendor_id': cpu_info['vendor_id'],
            'brand': cpu_info['brand'],
            'hz_advertised': cpu_info['hz_advertised'],
            'hz_actual': cpu_info['hz_actual']
        }
    }

# ################################################################################################################################

if __name__ == '__main__':
    print(get_hash_rounds_info())

# ################################################################################################################################
