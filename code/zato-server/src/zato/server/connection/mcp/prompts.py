# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.skills.api import load_skill

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.skills.api import SkillDocument
    from zato.common.typing_ import strdictlist, strlist, strnone

    SkillDocument = SkillDocument

# ################################################################################################################################
# ################################################################################################################################

# Default page size for prompts/list pagination, the same size tools/list pages by
_default_page_size = 100

# ################################################################################################################################
# ################################################################################################################################

class InvalidCursor(Exception):
    """ Raised when a prompts/list cursor is not a valid integer.
    """

# ################################################################################################################################
# ################################################################################################################################

class SkillPrompts:
    """ Serves the user-authored skills an MCP gateway is allowed to serve as prompts.
    The allow list comes from the gateway's configuration and the files themselves are
    read from disk on each request, never cached. Each MCP gateway has its own instance
    with its own allow list.
    """
    def __init__(self, repo_location:'str', allowed_skills:'strlist') -> 'None':
        self.repo_location = repo_location
        self.allowed_skills = allowed_skills

# ################################################################################################################################

    def has_prompts(self) -> 'bool':
        """ Whether the gateway serves any prompts at all, which is what decides
        whether initialize advertises the prompts capability.
        """
        out = bool(self.allowed_skills)
        return out

# ################################################################################################################################

    def get_prompts_page(self, cursor:'strnone'=None) -> 'tuple[strdictlist, strnone]':
        """ Returns a page of prompts starting from the given cursor - names and
        descriptions only, the instructions do not travel here. The cursor is an opaque
        string representing the start index, the same scheme tools/list pages by.
        Raises InvalidCursor if the cursor is not a valid integer.
        """

        # Names and descriptions come off the files as they are on disk right now,
        # and a skill whose file is gone has no line in the listing
        all_prompts:'strdictlist' = []

        for name in sorted(self.allowed_skills):

            document = load_skill(self.repo_location, name)

            if document is None:
                continue

            all_prompts.append({'name': name, 'description': document.description})

        total = len(all_prompts)

        # Decode the cursor into a start index ..
        if cursor is None:
            start = 0
        else:
            # Non-numeric cursors are rejected
            try:
                start = int(cursor)
            except ValueError:
                raise InvalidCursor(f'Invalid cursor value: `{cursor}`')

            # Clamp to the valid range of [0, total]
            upper_bound = min(start, total)
            start = max(0, upper_bound)

        # .. slice out the current page ..
        end = start + _default_page_size
        page = all_prompts[start:end]

        # .. if there are more prompts beyond this page, produce a next cursor ..
        if end < total:
            next_cursor = str(end)
        else:
            next_cursor = None

        # .. and return both the page and the cursor for the next one.
        out = (page, next_cursor)
        return out

# ################################################################################################################################

    def get_prompt(self, name:'str') -> 'SkillDocument | None':
        """ Returns the skill of this name, read from disk now. A name outside the
        gateway's allow list, or one whose file is gone, returns None.
        """

        # The allow list is checked first, so a skill that exists on disk
        # but was not selected for this gateway is never served
        if name not in self.allowed_skills:
            return None

        out = load_skill(self.repo_location, name)
        return out

# ################################################################################################################################
# ################################################################################################################################
