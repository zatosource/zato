# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import re

# Zato
from zato.common.hot_deploy_ import pickup_order_patterns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strdict, strintdict, strlist, strset
    anydict = anydict
    strdict = strdict
    strintdict = strintdict
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The group of operations whose paths have no literal segment to name a group after
    Default_Tag = 'General'

    # Versions, e.g. /v1 or /1.0, name no resource and are left out of group names
    Version_Pattern = re.compile(r'^v?\d+(\.\d+)*$')

    # Actions, e.g. get-identification, submit or GetForecast, are what is done with a resource, never the resource itself,
    # as in the <system>.<entity>.<action> convention of service names
    Action_Verbs = {
        'add', 'approve', 'authenticate', 'cancel', 'check', 'confirm', 'create', 'decode', 'delete', 'encode', 'export',
        'fetch', 'find', 'generate', 'get', 'import', 'invoke', 'list', 'lookup', 'notify', 'process', 'read', 'receive',
        'refresh', 'register', 'reject', 'remove', 'reset', 'resolve', 'run', 'search', 'send', 'set', 'submit', 'sync',
        'update', 'upload', 'validate', 'write',
    }
    First_Word_Pattern = re.compile(r'^[A-Za-z][a-z0-9]*')

    # Opaque identifiers, e.g. /4ed32368 or a UUID, are hexadecimal with at least one digit and name no resource either
    Opaque_ID_Pattern = re.compile(r'^(?=[0-9a-f-]*\d)[0-9a-f]{4,}(-[0-9a-f]+)*$')

    # Dotted names, e.g. /channel.sales.submit, are one segment per dotted part
    Dotted_Name_Separator = '.'

    # How the role words are read from the hot-deploy patterns, e.g. channel out of channel*/**
    Pattern_Wildcard = '*'
    Plural_Suffix = 's'

    # Placeholders in URL paths, e.g. {patient_id}
    Placeholder_Prefix = '{'

    # A section with more operations than this is divided into groups by the path segment that follows it
    Max_Group_Size = 8

    # Separates a section from its group in a group name, e.g. Healthcare / Patients
    Group_Separator = ' / '

    # Separates a section from a group's words in the keys that compound group names are looked up by
    Group_Key_Separator = '/'

    # Joins two segments into one compound name, e.g. restricted and access into restricted-access
    Compound_Separator = '-'

    # Hyphens and underscores separate the words of a path segment
    Word_Separator_Pattern = re.compile(r'[-_]+')

    # A sentence ends with a period followed by whitespace and a capital letter, so abbreviations such as e.g. do not end it
    Sentence_End_Pattern = re.compile(r'(?<=\.)\s+(?=[A-Z])')

    # Everything other than letters and digits separates the words of an operation ID
    Operation_ID_Separator_Pattern = re.compile(r'[^A-Za-z0-9]+')
    Operation_ID_Separator = '_'

# ################################################################################################################################
# ################################################################################################################################

def _build_role_words() -> 'strset':
    """ Returns the roles that services have in a project, e.g. api, channel or adapter, in the singular and the plural.
    The roles are the directory prefixes that hot deployment deploys in order.
    """
    out:'strset' = set()

    for pattern in pickup_order_patterns:
        word = pattern.strip().split(ModuleCtx.Pattern_Wildcard)[0]

        # Patterns of files rather than directories name no role
        if not word.isalpha():
            continue

        out.add(word)
        out.add(word + ModuleCtx.Plural_Suffix)

        if word.endswith(ModuleCtx.Plural_Suffix):
            out.add(word[:-1])

    return out

_role_words = _build_role_words()

# ################################################################################################################################
# ################################################################################################################################

def get_group_segments(path:'str') -> 'strlist':
    """ Returns the literal segments of a URL path that precede its first placeholder,
    without the segments that name no resource.
    """
    # Our response to produce
    out:'strlist' = []

    for segment in path.split('/'):

        # Leading, trailing and repeated slashes produce empty segments ..
        if not segment:
            continue

        # .. a placeholder ends the part of the path that names the resource ..
        if segment.startswith(ModuleCtx.Placeholder_Prefix):
            break

        # .. a version is dotted itself, so it is recognized before dotted names are divided ..
        if ModuleCtx.Version_Pattern.match(segment):
            continue

        # .. and the roles of services, e.g. api, channel or adapter, opaque identifiers and actions name no resource at all.
        for part in segment.split(ModuleCtx.Dotted_Name_Separator):

            if not part:
                continue

            if part.lower() in _role_words:
                continue

            if ModuleCtx.Opaque_ID_Pattern.match(part):
                continue

            if is_action(part):
                continue

            out.append(part)

    return out

# ################################################################################################################################

def is_action(part:'str') -> 'bool':
    """ Whether a path segment names an action, i.e. whether its first word is a verb.
    """
    match = ModuleCtx.First_Word_Pattern.match(part)

    # A segment that starts with something other than a letter names no action
    if not match:
        return False

    first_word = match.group(0).lower()

    out = first_word in ModuleCtx.Action_Verbs
    return out

# ################################################################################################################################

def get_display_name(segment:'str') -> 'str':
    """ Returns a path segment as a name to display, e.g. decision-support becomes Decision support.
    """
    words = ModuleCtx.Word_Separator_Pattern.sub(' ', segment)

    out = words[:1].upper() + words[1:]
    return out

# ################################################################################################################################

def get_words(segment:'str') -> 'str':
    """ Returns the words of a path segment in lower case, separated by spaces, e.g. Restricted-Access becomes restricted access.
    """
    words = ModuleCtx.Word_Separator_Pattern.sub(' ', segment)

    out = words.lower()
    return out

# ################################################################################################################################

def get_opaque_key(path:'str') -> 'str':
    """ Returns the part of a path up to and including its first opaque identifier, or an empty string if it has none.
    Paths with the same opaque identifier at the same place are exposed as one integration.
    """
    leading:'strlist' = []

    for segment in path.split('/'):
        leading.append(segment)

        if ModuleCtx.Opaque_ID_Pattern.match(segment):
            out = '/'.join(leading)
            return out

    return ''

# ################################################################################################################################

def _get_section_sizes(paths:'strlist', segments_by_path:'anydict') -> 'strintdict':
    """ Returns how many operations each section has, a section being the first group segment of a path
    and a path being listed once per operation.
    """
    out:'strintdict' = {}

    for path in paths:
        segments = segments_by_path[path]

        if segments:
            section = segments[0]

            if section not in out:
                out[section] = 0

            out[section] += 1

    return out

# ################################################################################################################################

def _get_group_words(segments_by_path:'anydict', section_sizes:'strintdict') -> 'strset':
    """ Returns the section and the words of each group that the paths of large sections name directly.
    """
    out:'strset' = set()

    for segments in segments_by_path.values():
        if len(segments) > 1:
            section = segments[0]

            if section_sizes[section] > ModuleCtx.Max_Group_Size:
                group_key = section + ModuleCtx.Group_Key_Separator + get_words(segments[1])
                out.add(group_key)

    return out

# ################################################################################################################################

def _get_group_segment(segments:'strlist', group_words:'strset') -> 'str':
    """ Returns the segment a path is grouped by in a large section, joined with the next one when the two
    are a compound name that another path has as a single segment, e.g. /restricted/access and /restricted-access.
    """
    section = segments[0]
    group = segments[1]

    if len(segments) > 2:
        compound = group + ModuleCtx.Compound_Separator + segments[2]
        compound_key = section + ModuleCtx.Group_Key_Separator + get_words(compound)

        if compound_key in group_words:
            return compound

    return group

# ################################################################################################################################

def get_tags(paths:'strlist') -> 'strdict':
    """ Returns the name of the group of operations each path belongs to, the paths being listed once per operation.
    A path is grouped by its section,
    and a section with more operations than fit one group is divided by the resource that follows it,
    e.g. Healthcare / Patients.
    """
    # Our response to produce
    out:'strdict' = {}

    segments_by_path:'anydict' = {}

    for path in paths:
        segments_by_path[path] = get_group_segments(path)

    section_sizes = _get_section_sizes(paths, segments_by_path)
    group_words = _get_group_words(segments_by_path, section_sizes)

    # The group of each opaque identifier, for the paths that name no resource past it ..
    tag_by_opaque_key:'strdict' = {}
    ungrouped:'strlist' = []

    for path in sorted(segments_by_path):
        segments = segments_by_path[path]

        # .. a path with no literal segments has nothing to be grouped by ..
        if not segments:
            out[path] = ModuleCtx.Default_Tag
            continue

        section = segments[0]
        section_name = get_display_name(section)

        # .. a small section is a single group ..
        if section_sizes[section] <= ModuleCtx.Max_Group_Size:
            out[path] = section_name
            continue

        # .. a path that ends at its section in a large one is grouped once all the other paths are ..
        if len(segments) == 1:
            ungrouped.append(path)
            continue

        # .. and any other path in a large section is grouped by the resource that follows the section.
        group_segment = _get_group_segment(segments, group_words)
        tag = section_name + ModuleCtx.Group_Separator + get_display_name(group_segment)
        out[path] = tag

        opaque_key = get_opaque_key(path)

        if opaque_key:
            if opaque_key not in tag_by_opaque_key:
                tag_by_opaque_key[opaque_key] = tag

    # A path that names no resource joins the group of another path with the same opaque identifier, if there is one,
    # and the section's general group otherwise.
    for path in ungrouped:
        opaque_key = get_opaque_key(path)

        if opaque_key in tag_by_opaque_key:
            out[path] = tag_by_opaque_key[opaque_key]
        else:
            section_name = get_display_name(segments_by_path[path][0])
            out[path] = section_name + ModuleCtx.Group_Separator + ModuleCtx.Default_Tag

    return out

# ################################################################################################################################

def get_summary(docstring:'str') -> 'str':
    """ Returns the first sentence of a docstring whose whitespace is already collapsed.
    """
    sentences = ModuleCtx.Sentence_End_Pattern.split(docstring, maxsplit=1)

    out = sentences[0]
    return out

# ################################################################################################################################

def get_operation_id(http_method:'str', path:'str') -> 'str':
    """ Returns a unique ID of an operation, made of its method and its URL path.
    """
    words = ModuleCtx.Operation_ID_Separator_Pattern.sub(ModuleCtx.Operation_ID_Separator, path)
    words = words.strip(ModuleCtx.Operation_ID_Separator)

    out = http_method + ModuleCtx.Operation_ID_Separator + words
    return out

# ################################################################################################################################
# ################################################################################################################################
