# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from re import compile as re_compile

# Zato
from zato.common.typing_ import any_, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - the classes are defined below in this module.
signal_dict = dict[str, 'SafeguardSignal']

# ################################################################################################################################
# ################################################################################################################################

# A string must be at least this many characters long to be considered a base64 blob.
Base64_Min_Length = 256

# The shape of a base64 blob - an optional data URI prefix followed by base64 alphabet characters and optional padding.
Base64_Pattern = re_compile(r'(?:data:[\w.+-]+/[\w.+-]+;base64,)?[A-Za-z0-9+/]+={0,2}')

# Marker replacing a removed base64 blob, naming the original size.
Base64_Marker_Template = '[binary content removed: {size} characters]'

# Runs of whitespace collapse into a single space.
Whitespace_Pattern = re_compile(r'\s+')

# Marker replacing a removed URL.
Url_Marker = '[link removed]'

# What a stage does when it finds something - clean it and continue, or refuse the whole document.
Mode_Clean  = 'clean'
Mode_Reject = 'reject'

# What happens to a URL outside the allow list.
Url_Mode_Remove     = 'remove'
Url_Mode_Neutralize = 'neutralize'
Url_Mode_Reject     = 'reject'

# Kinds of security findings that can appear among signals.
Kind_Unicode = 'unicode'
Kind_Markup  = 'markup'
Kind_Url     = 'url'

# At most this many example paths are kept per signal kind - further findings only increment the count.
Max_Signal_Paths = 5

# At most this many compiled PII cleaners are kept in the cache.
Max_Cleaner_Cache_Entries = 100

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SafeguardConfig:
    """ What the safeguards should do to a document - every behavior is off by default.
    The list fields carry no defaults - a caller that enables a stage assigns its lists first,
    possibly as empty ones.
    """

    # Noise stripping
    strip_nulls:         bool = False
    collapse_whitespace: bool = False
    strip_base64:        bool = False

    # PII removal - lands select detector groups, explicit detector names win over lands,
    # exclusions are removed from whatever the other two selected.
    pii_enabled:       bool = False
    pii_lands:         strlist
    pii_detectors:     strlist
    pii_exclude:       strlist
    pii_validate:      bool = True
    pii_stable_tokens: bool = False

    # Unicode normalization
    normalize_unicode: bool = False
    unicode_mode:      str  = Mode_Clean

    # Markup sanitization
    sanitize_markup: bool = False
    markup_mode:     str  = Mode_Clean

    # URL policy
    url_policy_enabled: bool = False
    url_allow_list:     strlist
    url_mode:           str  = Url_Mode_Remove

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SafeguardSignal:
    """ A summary of security findings of one kind - how many there were and where the first few of them happened.
    """
    count: int = 0
    paths: strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SafeguardResult:
    """ The outcome of applying safeguards to a value - the possibly modified value itself plus a full account of what happened.
    """

    # The value after all the enabled stages ran
    value: any_

    # Sizes of the serialized document before and after
    size_before: int = 0
    size_after:  int = 0

    # Whether anything changed and whether the document was refused outright
    was_modified: bool = False
    was_rejected: bool = False
    reject_kind:  str  = ''

    # Per-stage counters
    nulls_removed:            int = 0
    whitespace_chars_removed: int = 0
    base64_blobs_removed:     int = 0
    base64_chars_removed:     int = 0
    unicode_chars_removed:    int = 0
    markup_items_removed:     int = 0
    urls_flagged:             int = 0

    # PII matches by detector name
    pii_removed: strintdict

    # Security findings by kind
    signals: signal_dict

# ################################################################################################################################
# ################################################################################################################################

def add_signal(signals:'signal_dict', kind:'str', count:'int', path:'str') -> 'None':
    """ Records a security finding, accumulating into the signal for its kind if one exists already.
    The path sample per kind is bounded - further findings only increment the count.
    """

    # An existing signal grows its count and, while there is room, its path sample -
    # a path already in the sample is not repeated, e.g. when one string holds many findings ..
    if signal := signals.get(kind):
        signal.count += count

        path_count = len(signal.paths)

        if path_count < Max_Signal_Paths:
            if path not in signal.paths:
                signal.paths.append(path)

    # .. and the first finding of a kind creates the signal.
    else:
        signal = SafeguardSignal()
        signal.count = count
        signal.paths = [path]
        signals[kind] = signal

# ################################################################################################################################
# ################################################################################################################################
