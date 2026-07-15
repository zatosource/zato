# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from math import ceil

# Zato
from zato.common.typing_ import any_
from zato.common.util.truncate.api import truncate_json
from zato.common.util.truncate.common import drop_entry_list
from zato.common.util.truncate.measure import serialize

# ################################################################################################################################
# ################################################################################################################################

# How many characters one token is assumed to span when estimating - the industry rule of thumb for English text.
Default_Characters_Per_Token = 4.0

# What happens to a response over the cap - graceful trimming or outright refusal.
Size_Cap_Mode_Truncate = 'truncate'
Size_Cap_Mode_Block    = 'block'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TokenCapConfig:
    """ How a token-denominated size cap should behave - zeroes disable the cap and the threshold respectively.
    """

    # Responses estimated above this many tokens are over the cap - 0 means no cap at all.
    max_response_tokens: int = 0

    # Responses estimated below this many tokens skip the cap entirely - 0 means no threshold.
    min_threshold_tokens: int = 0

    # What to do with a response over the cap.
    size_cap_mode: str = Size_Cap_Mode_Truncate

    # How many characters one token is assumed to span - a float, so values like 3.5 work.
    characters_per_token: float = Default_Characters_Per_Token

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TokenCapResult:
    """ The outcome of applying a token cap to a value - the possibly trimmed value itself plus a full account of what happened.
    """

    # The value after the cap ran
    value: any_

    # Cuts recorded by graceful trimming, empty unless truncation ran
    report: drop_entry_list

    # Estimated token counts before and after
    tokens_before: int = 0
    tokens_after:  int = 0

    # Which path the cap took
    was_skipped:   bool = False
    was_blocked:   bool = False
    was_truncated: bool = False
    did_fit:       bool = False

# ################################################################################################################################
# ################################################################################################################################

def estimate_tokens(value:'any_', characters_per_token:'float') -> 'int':
    """ Estimates how many tokens the canonical JSON form of a value spans - its length in characters
    divided by the characters-per-token ratio, rounded up to a whole token count.
    """
    serialized = serialize(value)
    char_count = len(serialized)

    out = ceil(char_count / characters_per_token)

    return out

# ################################################################################################################################
# ################################################################################################################################

def apply_token_cap(value:'any_', config:'TokenCapConfig') -> 'TokenCapResult':
    """ Applies a token-denominated size cap to a JSON-serializable value - responses below the activation threshold
    or within the cap pass through untouched, oversized ones are blocked or gracefully trimmed depending on the mode.
    The input is never mutated and this function never raises - a block is expressed on the result,
    the caller decides what to do with it.
    """

    # Our response to produce
    out = TokenCapResult()
    out.value = value
    out.report = []

    tokens_before = estimate_tokens(value, config.characters_per_token)
    out.tokens_before = tokens_before
    out.tokens_after = tokens_before

    # Responses below the activation threshold skip the cap entirely.
    if config.min_threshold_tokens:
        if tokens_before < config.min_threshold_tokens:
            out.was_skipped = True
            return out

    # No cap at all, or the response already fits within it - nothing to enforce.
    if not config.max_response_tokens or tokens_before <= config.max_response_tokens:
        out.did_fit = True
        return out

    # Over the cap in block mode - the value is returned untouched, the caller rejects it.
    if config.size_cap_mode == Size_Cap_Mode_Block:
        out.was_blocked = True
        return out

    # Over the cap in truncate mode - the token budget becomes a byte budget for graceful trimming.
    max_size = int(config.max_response_tokens * config.characters_per_token)
    truncated = truncate_json(value, max_size)

    out.value = truncated.value
    out.report = truncated.report
    out.was_truncated = truncated.was_truncated
    out.did_fit = truncated.did_fit

    # The estimate is re-run on the trimmed value so the caller sees the actual outcome.
    out.tokens_after = estimate_tokens(truncated.value, config.characters_per_token)

    return out

# ################################################################################################################################
# ################################################################################################################################
