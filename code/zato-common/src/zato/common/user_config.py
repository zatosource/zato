# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist

    any_ = any_
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # A file that keeps this section is a list of the values that are accepted, one value
    # per key. A file without it maps the codes of one party per section to the values
    # that are accepted here.
    Codes_Section = 'codes'

# ################################################################################################################################
# ################################################################################################################################

class AmbiguousTarget(Exception):
    """ A target keeps one value under more than one of its own codes, so there is no single
    code to send that value as. Either the target's section says which code to use for it
    or the caller reads the keys out of the file itself.
    """

# ################################################################################################################################
# ################################################################################################################################

class UserConfigFile(Bunch):
    """ One user config file, read as it always was, with two questions asked of it on top -
    whether a value is one that is accepted here, and what a value of another party's means here.
    """

    # What belongs to the object rather than to the file's own contents - the name of the file,
    # which is what an error says it went wrong in, and every other file of the server, which
    # is where a list to check a translation against is found.
    zato_file_name:'str'
    zato_store:'anydict'

# ################################################################################################################################

    def __init__(self, file_name:'str', store:'anydict', data:'anydict') -> 'None':

        super().__init__(data)

        # These two are set the way Python sets any attribute, which is what keeps them out
        # of the file - a plain assignment would put them into it as keys of its own.
        object.__setattr__(self, 'zato_file_name', file_name)
        object.__setattr__(self, 'zato_store', store)

# ################################################################################################################################

    def validate(self, value:'any_') -> 'bool':
        """ Whether the value is one of the ones this file accepts. A file that has no list
        of them accepts nothing, which is what a file of mappings answers.
        """
        if ModuleCtx.Codes_Section not in self:
            return False

        code_list = self[ModuleCtx.Codes_Section]

        # The keys of a file are always text, while a value read out of one may have been
        # turned into a number by the config reader, so the two are compared as text.
        value = self._zato_as_text(value)

        out = value in code_list
        return out

# ################################################################################################################################

    def translate(self, *, source:'str', code:'str', codes:'str'='', target:'str'='') -> 'any_':
        """ What the code of one party means here, or what another party sends it as when
        a target is given. Anything this file knows nothing about comes back as None, which
        is an outcome the caller decides about rather than an error.
        """
        # Who the code belongs to is a section of this file, and the code is a key of it ..
        if source not in self:
            return None

        section = self[source]

        if code not in section:
            return None

        # .. what it means here is what that key holds ..
        value = section[code]

        # .. a list to check it against makes sure this file cannot quietly produce
        # something the rest of the system does not know ..
        if codes:
            if not self._zato_is_in_codes(codes, value):
                return None

        # .. and a target is the same file read the other way round, so the answer becomes
        # the code that target keeps this value under.
        if target:
            out = self._zato_to_target(target, value)
            return out

        return value

# ################################################################################################################################

    def _zato_is_in_codes(self, codes:'str', value:'any_') -> 'bool':
        """ Whether the value is accepted by the file the name points to. A name that is
        no file of the server accepts nothing.
        """
        if codes not in self.zato_store:
            return False

        other = self.zato_store[codes]
        out = other.validate(value)

        return out

# ################################################################################################################################

    def _zato_to_target(self, target:'str', value:'any_') -> 'any_':
        """ The code the target keeps the value under. A target that has no code for it, and
        a name that is no section of this file, are each nothing to send, while a target that
        keeps it under several codes is an error - there is no one code to pick out of them.
        """
        if target not in self:
            return None

        key_list = self._zato_get_target_keys(target, value)

        if not key_list:
            return None

        key_count = len(key_list)
        has_one_key = key_count == 1

        if not has_one_key:
            error_text = self._zato_build_ambiguous_text(target, value, key_list)
            raise AmbiguousTarget(error_text)

        out = key_list[0]
        return out

# ################################################################################################################################

    def _zato_get_target_keys(self, target:'str', value:'any_') -> 'strlist':
        """ Every code the target keeps the value under, in name order, so what comes back
        reads the same way each time it is asked for.
        """
        section = self[target]
        out:'strlist' = []

        for key, target_value in section.items():
            if target_value == value:
                out.append(key)

        out.sort()

        return out

# ################################################################################################################################

    def _zato_build_ambiguous_text(self, target:'str', value:'any_', key_list:'strlist') -> 'str':
        """ What went wrong, in the terms the file itself is written in - which file it was,
        which of its targets, which value, and the codes that value turned out to be under.
        """
        file_name = self.zato_file_name
        value = self._zato_as_text(value)
        key_count = len(key_list)
        key_text = ', '.join(key_list)

        out = f'{file_name}, target {target}, value {value} maps to {key_count} keys: {key_text}'
        return out

# ################################################################################################################################

    def _zato_as_text(self, value:'any_') -> 'str':
        """ The value as the file itself spells it - the config reader turns what looks like
        a number into one, while a code is always text, digits included.
        """
        if isinstance(value, str):
            out = value
        else:
            out = str(value)

        return out

# ################################################################################################################################
# ################################################################################################################################
