# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This function is a replacement for ws4py.framing.Frame:unmask
def unmask(self, data):

    cdef int i
    cdef int current_mask_elem

    masked = bytearray(data)
    key = self.masking_key

    for i in range(len(data)):
        current_mask_elem = i % 4
        xor_with = key[current_mask_elem]
        masked[i] = masked[i] ^ xor_with

    return masked
