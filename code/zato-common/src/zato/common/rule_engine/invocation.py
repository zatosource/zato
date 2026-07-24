# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from time import monotonic
from typing import NamedTuple

# Zato
from zato.common.rule_engine.ingestion import DecisionRecorder
from zato.common.rule_engine.loading import documents_from_version
from zato.common.rule_engine.semantics import validate_data
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.sql.errors import RecordNotFoundError
from zato.common.rule_engine.testing import load_documents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import DecisionBatchWriter, RuleDefinitionRecord, RuleSQLBackend
    from zato.common.rule_engine.testing import LoadedRules
    from zato.common.typing_ import anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

version_key           = tuple[int, int]
resolved_name_dict    = dict[str, '_ResolvedName']
loaded_version_dict   = dict[version_key, '_LoadedVersion']
vocabulary_cache_dict = dict[int, '_CachedVocabulary']

# ################################################################################################################################
# ################################################################################################################################

# How long resolved names, live pointers and vocabulary documents stay cached before they are re-read,
# which is also how quickly a publish or a rename becomes visible to callers.
Default_Cache_TTL_Seconds = 0.5

# The key under which a stored ruleset document optionally names the vocabulary its inputs are validated against.
Vocabulary_Key = 'vocabulary_id'

# The URL segment that separates a ruleset name from an explicitly requested version.
Version_Separator = '/versions/'

# The pattern that grants access to every ruleset.
Match_All_Pattern = '*'

# The suffix that makes a grant pattern match a whole subtree of ruleset names.
Match_Prefix_Suffix = '.*'

# ################################################################################################################################

# What one invocation attempt ended with - the REST boundary maps these to HTTP statuses.
class InvocationStatus:
    OK              = 'ok'
    Unknown_Ruleset = 'unknown-ruleset'
    Ambiguous_Name  = 'ambiguous-name'
    No_Live_Version = 'no-live-version'
    Unknown_Version = 'unknown-version'
    Invalid_Input   = 'invalid-input'

# ################################################################################################################################

# The one message unknown and unauthorized rulesets share, so credentials cannot be used
# to tell apart what exists from what is merely not granted.
Message_Unknown_Ruleset = 'Ruleset `{name}` is not available'

Message_Ambiguous_Name  = 'More than one ruleset is named `{name}` - rename one of them to invoke either'
Message_No_Live_Version = 'Ruleset `{name}` has no published version'
Message_Unknown_Version = 'Ruleset `{name}` has no version {version}'
Message_Invalid_Version = 'A version has to be a positive number, not `{version}`'
Message_Invalid_Path    = 'Only `{separator}` followed by a number may follow a ruleset name'

# ################################################################################################################################
# ################################################################################################################################

class ParsedRulesetPath(NamedTuple):
    """ What one {ruleset} path parameter carries - a name, an optional pinned version and a parse error, if any.
    """
    name:    'str'
    version: 'int | None'
    error:   'str | None'

# ################################################################################################################################

class _ResolvedName(NamedTuple):
    """ One cached name lookup - the definition it maps to, whether the name is ambiguous and when it was read.
    """
    definition:   'RuleDefinitionRecord | None'
    is_ambiguous: 'bool'
    checked_at:   'float'

# ################################################################################################################################

class _LoadedVersion(NamedTuple):
    """ One compiled, immutable ruleset snapshot and the vocabulary its inputs are validated against.
    """
    loaded:        'LoadedRules'
    vocabulary_id: 'int | None'

# ################################################################################################################################

class _CachedVocabulary(NamedTuple):
    """ One cached vocabulary document and when it was read.
    """
    document:   'anydict'
    checked_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InvocationResult:
    """ The complete outcome of one invocation attempt.
    """

    status:   'str'
    ruleset:  'str'
    version:  'int | None'
    message:  'str'
    errors:   'dictlist'
    decision: 'anydict | None'

    def __init__(self) -> 'None':
        self.status   = InvocationStatus.OK
        self.ruleset  = ''
        self.version  = None
        self.message  = ''
        self.errors   = []
        self.decision = None

# ################################################################################################################################
# ################################################################################################################################

def parse_ruleset_path(value:'str') -> 'ParsedRulesetPath':
    """ Splits one {ruleset} path parameter into a name and an optionally pinned version.

    The parameter is everything after the API's base path, so `payments.discounts` invokes
    the live version and `payments.discounts/versions/3` pins version 3.
    """
    # A parameter without the separator is a bare name that runs the live version ..
    if Version_Separator not in value:

        # .. and a slash inside it can never be part of a ruleset name.
        if '/' in value:
            error = Message_Invalid_Path.format(separator=Version_Separator)
            out = ParsedRulesetPath('', None, error)
            return out

        out = ParsedRulesetPath(value, None, None)
        return out

    # .. otherwise the name ends where the separator begins ..
    name, _, version_text = value.partition(Version_Separator)

    # .. a slash in either part means the path has more segments than the API defines ..
    if '/' in name or '/' in version_text:
        error = Message_Invalid_Path.format(separator=Version_Separator)
        out = ParsedRulesetPath('', None, error)
        return out

    # .. and the version has to be a positive number.
    if not version_text.isdigit():
        error = Message_Invalid_Version.format(version=version_text)
        out = ParsedRulesetPath('', None, error)
        return out

    version = int(version_text)

    if version < 1:
        error = Message_Invalid_Version.format(version=version_text)
        out = ParsedRulesetPath('', None, error)
        return out

    out = ParsedRulesetPath(name, version, None)
    return out

# ################################################################################################################################

def _flatten_into(data:'anydict', prefix:'str', out:'anydict') -> 'None':
    """ Walks one nesting level, joining keys with dots along the way.
    """
    for key, value in data.items():

        if prefix:
            path = prefix + '.' + key
        else:
            path = key

        # A mapping is one more nesting level, anything else is a leaf value.
        if isinstance(value, dict):
            _flatten_into(value, path, out)
        else:
            out[path] = value

# ################################################################################################################################

def flatten_for_validation(data:'anydict') -> 'anydict':
    """ Turns nested caller input into the dotted paths a vocabulary speaks.
    Rules receive the input exactly as the caller sent it - this flat form exists for validation only,
    so `{"customer": {"creditScore": 720}}` is checked as `customer.creditScore`.
    """
    out:'anydict' = {}
    _flatten_into(data, '', out)
    return out

# ################################################################################################################################

def is_ruleset_allowed(name:'str', patterns:'strlist') -> 'bool':
    """ Returns whether one ruleset name matches any of the granted patterns.

    A grant is either an exact name (`payments.discounts`), a subtree (`payments.*`)
    or everything (`*`).
    """
    for pattern in patterns:

        # A lone star grants every ruleset ..
        if pattern == Match_All_Pattern:
            out = True
            break

        # .. a subtree pattern grants everything under its prefix ..
        if pattern.endswith(Match_Prefix_Suffix):
            prefix_length = len(Match_Prefix_Suffix) - 1
            prefix = pattern[:-prefix_length]

            if name.startswith(prefix):
                out = True
                break

        # .. and anything else is an exact grant for one ruleset.
        elif pattern == name:
            out = True
            break

    # No pattern matched, so the ruleset is not granted.
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

class RulesetInvoker:
    """ Runs published rulesets by name over the SQL store, with short-lived caches in front of it.

    Names and live-version pointers are re-read once per TTL window, so a publish or a rename
    in the dashboard is visible here within a fraction of a second, no matter the traffic.
    Version snapshots are immutable so once compiled they are kept for the invoker's lifetime.
    """

    def __init__(
        self,
        backend:'RuleSQLBackend',
        writer:'DecisionBatchWriter',
        cache_ttl_seconds:'float' = Default_Cache_TTL_Seconds,
        ) -> 'None':

        self.backend = backend
        self.writer = writer
        self.cache_ttl_seconds = cache_ttl_seconds

        # One entry per ruleset name, including names that resolved to nothing,
        # so unknown names cannot force a database read per request.
        self._resolved:'resolved_name_dict' = {}

        # One compiled ruleset per (definition id, version) - versions are immutable so entries never expire.
        self._loaded:'loaded_version_dict' = {}

        # One entry per vocabulary the loaded rulesets validate against.
        self._vocabularies:'vocabulary_cache_dict' = {}

# ################################################################################################################################

    def _resolve_name(self, name:'str') -> '_ResolvedName':
        """ Returns the definition one ruleset name maps to, re-reading it once per TTL window.
        """
        now = monotonic()

        # A fresh cached answer is the common case and costs no database work ..
        if entry := self._resolved.get(name):
            age = now - entry.checked_at

            if age < self.cache_ttl_seconds:
                return entry

        # .. otherwise read the current state of that name from the store ..
        matches = self.backend.definitions.find_by_name(name=name, object_type=Definition_Type_Ruleset)
        match_count = len(matches)

        # .. no match and more than one match are both cached, so they are as cheap as a hit ..
        if match_count == 0:
            entry = _ResolvedName(None, False, now)
        elif match_count == 1:
            entry = _ResolvedName(matches[0], False, now)
        else:
            entry = _ResolvedName(None, True, now)

        # .. and remember the answer for the next TTL window.
        self._resolved[name] = entry

        return entry

# ################################################################################################################################

    def _load_version(self, definition_id:'int', version:'int') -> '_LoadedVersion':
        """ Returns one compiled version snapshot, building it on first use.
        """
        key = (definition_id, version)

        # Snapshots are immutable, so a compiled entry is valid for as long as this invoker lives ..
        if entry := self._loaded.get(key):
            return entry

        # .. otherwise read the immutable snapshot - the store raises if the version does not exist ..
        record = self.backend.versions.get(definition_id, version)

        # .. extract its canonical rule documents ..
        documents = documents_from_version(record)

        # .. remember which vocabulary this snapshot's inputs are validated against, if any ..
        payload = deserialize_document(record.document)
        vocabulary_id = payload.get(Vocabulary_Key)

        # .. compile the documents into a manager of their own ..
        loaded = load_documents(documents)

        # .. and keep the compiled snapshot for every later request.
        entry = _LoadedVersion(loaded, vocabulary_id)
        self._loaded[key] = entry

        return entry

# ################################################################################################################################

    def _get_vocabulary(self, vocabulary_id:'int') -> 'anydict':
        """ Returns one vocabulary document, re-reading it once per TTL window so edits apply quickly.
        """
        now = monotonic()

        # A fresh cached document is the common case ..
        if entry := self._vocabularies.get(vocabulary_id):
            age = now - entry.checked_at

            if age < self.cache_ttl_seconds:
                out = entry.document
                return out

        # .. otherwise read the current document and cache it for the next TTL window.
        document = self.backend.definitions.get_document(vocabulary_id)
        self._vocabularies[vocabulary_id] = _CachedVocabulary(document, now)

        out = document
        return out

# ################################################################################################################################

    def invoke(
        self,
        name:'str',
        data:'anydict',
        version:'int | None' = None,
        caller:'str | None' = None,
        ) -> 'InvocationResult':
        """ Evaluates one input against a published ruleset and logs the complete decision.

        Without an explicit version the live one runs, so a publish in the dashboard changes
        what this method runs within the cache TTL. The optional caller is the name of the
        authenticated system this evaluation runs for and it lands in the decision log.
        """

        # Our response to produce
        out = InvocationResult()
        out.ruleset = name

        # Resolve the name to its one definition ..
        resolved = self._resolve_name(name)

        # .. a name shared by more than one ruleset cannot be invoked by name at all ..
        if resolved.is_ambiguous:
            out.status = InvocationStatus.Ambiguous_Name
            out.message = Message_Ambiguous_Name.format(name=name)
            return out

        # .. a name that maps to nothing is simply not available ..
        definition = resolved.definition

        if definition is None:
            out.status = InvocationStatus.Unknown_Ruleset
            out.message = Message_Unknown_Ruleset.format(name=name)
            return out

        # .. without a pinned version the live pointer decides what runs ..
        if version is None:
            version = definition.live_version

            # .. and a ruleset that was never published has nothing to run.
            if version is None:
                out.status = InvocationStatus.No_Live_Version
                out.message = Message_No_Live_Version.format(name=name)
                return out

        out.version = version

        # .. load the immutable snapshot of that version ..
        try:
            entry = self._load_version(definition.id, version)
        except RecordNotFoundError:
            out.status = InvocationStatus.Unknown_Version
            out.message = Message_Unknown_Version.format(name=name, version=version)
            return out

        # .. when the snapshot names a vocabulary, the input is validated against it first,
        # so a caller gets domain-term errors rather than an evaluation failure - the vocabulary
        # speaks flat dotted paths while the rules read the nested input as sent, hence the flattening ..
        if entry.vocabulary_id:
            vocabulary = self._get_vocabulary(entry.vocabulary_id)
            flat_data = flatten_for_validation(data)
            errors = validate_data(flat_data, vocabulary)

            if errors:
                out.status = InvocationStatus.Invalid_Input
                out.errors = errors
                return out

        # .. evaluate the input and log the complete decision through the non-blocking writer ..
        recorder = DecisionRecorder(self.writer, ruleset_id=definition.id, rules_version=version)
        decision = recorder.record(entry.loaded, data, caller)

        # .. and return the outcome together with the id the decision log carries.
        out.decision = decision
        return out

# ################################################################################################################################
# ################################################################################################################################
