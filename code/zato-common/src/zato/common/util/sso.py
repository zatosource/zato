# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from math import ceil
from uuid import uuid4

# Base32 Crockford
from base32_crockford import encode as crockford_encode

# Bunch
from bunch import bunchify

# py-cpuinfo
from cpuinfo import get_cpu_info

# hashlib
from passlib import hash as passlib_hash

# ################################################################################################################################

def _new_id(prefix, _uuid4=uuid4, _crockford_encode=crockford_encode):
    return '%s%s' % (prefix, _crockford_encode(_uuid4().int).lower())

# ################################################################################################################################

def new_confirm_token(_new_id=_new_id):
    return _new_id('zcnt')

# ################################################################################################################################

def new_user_id(_new_id=_new_id):
    return _new_id('zusr')

# ################################################################################################################################

def get_hash_rounds(target_ms, scheme='pbkdf2_sha512'):
    print(target_ms, scheme)

# ################################################################################################################################

class HashParamsComputer(object):
    """ Computes parameters for hashing purposes, e.g. number of rounds in PBKDF2.
    """
    def __init__(self, goal, header_func=None, progress_func=None, footer_func=None, scheme='pbkdf2_sha512', loops=10,
            iters_per_loop=10, salt_size=128, rounds_per_iter=20000):
        self.goal = goal
        self.header_func = header_func
        self.progress_func = progress_func
        self.footer_func = footer_func
        self.scheme = scheme
        self.loops = loops
        self.iters_per_loop = iters_per_loop
        self.iters = self.loops * self.iters_per_loop
        self.salt_size = salt_size
        self.rounds_per_iter = rounds_per_iter
        self.report_per_cent = 5.0
        self.report_once_in = self.iters * self.report_per_cent / 100.0
        self.hash_scheme = getattr(passlib_hash, scheme).using(salt_size=salt_size, rounds=rounds_per_iter)
        self.cpu_info = self.get_cpu_info()
        self._round_to_nearest = 5000

# ################################################################################################################################

    def get_cpu_info(self):
        """ Returns metadata about current CPU the computation is executed on.
        """
        cpu_info = get_cpu_info()
        return bunchify({
            'vendor_id': cpu_info['vendor_id'],
            'brand': cpu_info['brand'],
            'hz_actual': cpu_info['hz_actual']
        })

# ################################################################################################################################

    def get_info(self, _utcnow=datetime.utcnow):

        if self.header_func:
            header_func(self.cpu_info, self.goal)

        all_results = []
        current_iter = 0
        current_loop = 0

        # We have several iterations to take into account sudden and unexpected CPU usage spikes,
        # outliers stemming from such cases which will be rejected.
        while current_loop < self.loops:
            current_loop += 1
            current_loop_iter = 0
            current_loop_result = []

            while current_loop_iter < self.iters_per_loop:
                current_iter += 1
                current_loop_iter += 1

                start = _utcnow()
                self.hash_scheme.hash(well_known_data)
                current_loop_result.append((_utcnow() - start).total_seconds())

                if self.progress_func:
                    if current_iter % self.report_once_in == 0:
                        per_cent = int((current_iter / self.iters) * 100)
                        self.progress_func(per_cent)

            all_results.append(sum(current_loop_result) / len(current_loop_result))

        # On average, that many seconds were needed to create a hash with self.rounds rounds ..
        sec_needed = min(all_results)

        # .. we now need to extrapolate it to get the desired self.goal seconds.
        rounds_per_second = int(self.rounds_per_iter / sec_needed)
        rounds_per_second = self.round_down(rounds_per_second)

        rounds_per_goal = int(rounds_per_second * self.goal)
        rounds_per_goal = self.round_up(rounds_per_goal)

        rounds_per_second_str = '{:,d}'.format(rounds_per_second)
        rounds_per_goal_str = '{:,d}'.format(rounds_per_goal).rjust(len(rounds_per_second_str))

        if self.footer_func:
            footer_func(rounds_per_second_str, rounds_per_goal_str)

        return {
            'rounds_per_second': int(rounds_per_second),
            'rounds_per_second_str': rounds_per_second_str,
            'rounds_per_goal': int(rounds_per_goal),
            'rounds_per_goal_str': rounds_per_goal_str,
            'cpu_info': self.cpu_info,
        }

# ################################################################################################################################

    def round_down(self, value):
        return int(round(value / self._round_to_nearest) * self._round_to_nearest)

# ################################################################################################################################

    def round_up(self, value):
        return int(ceil(value / self._round_to_nearest) * self._round_to_nearest)

# ################################################################################################################################

def header_func(cpu_info, goal):
    print('-' * 70)
    print('CPU brand ........... {}'.format(cpu_info.brand))
    print('CPU frequency........ {}'.format(cpu_info.hz_actual))
    print('Goal ................ {} sec'.format(goal))
    print('-' * 70)

def footer_func(rounds_per_second_str, rounds_per_goal_str):
    print('-' * 70)
    print('Performance ......... {} rounds/s'.format(rounds_per_second_str))
    print('Required for goal ... {} rounds'.format(rounds_per_goal_str))
    print('-' * 70)

# ################################################################################################################################

def progress_func(current_per_cent):
    if current_per_cent >= 100:
        current_per_cent = 100

    print('Done % .............. {:<3}'.format(current_per_cent))

# ################################################################################################################################

if __name__ == '__main__':
    goal = 0.2
    computer = HashParamsComputer(goal, header_func, progress_func, footer_func)
    info = computer.get_info()
