
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MCP gateway - the help texts behind every "How does it work?" badge.
// One text describes a field wherever it is shown - the gateway list and
// the wizard both read this map. The texts flow and wrap on their own,
// <br><br> only separates paragraphs.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.field_descriptions = {
    'id_name': 'A unique name for this gateway. Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this gateway accepts requests. MCP clients cannot reach inactive gateways.',
    'id_url_path': 'URL path the MCP endpoint is exposed under, e.g. /mcp/. This is the address MCP clients, ' +
        'such as AI assistants, connect to in order to discover and invoke the assigned services.',
    'id_validate_input': 'Whether tool call arguments are validated against each tool\'s input schema before the tool runs - ' +
        'required fields present, no unknown fields, types matching what tools/list advertises. ' +
        'Invalid calls are refused with an error naming the offending field.',
    'id_is_audit_log_active': 'Whether this gateway\'s traffic is recorded in the audit log - one event per request ' +
        'with the method, tool, caller and outcome. Payloads themselves are never recorded, only their sizes are.',

    'id_allow_client_filters': 'Adds an optional response_filter parameter to every tool, letting an AI agent ' +
        'pass its own JSONata expression per call. The expression runs on the server and the agent receives ' +
        'only the fields it asked for, which cuts its context usage on every invocation.',
    'id_max_response_size': 'The maximum size of a tool response in tokens, empty means no cap. ' +
        'Oversized tool responses are the main way context windows get flooded - one unbounded call ' +
        'can crowd out everything the agent learned before it.<br><br>' +
        'In truncate mode the cap must span at least 4,000 bytes, i.e. 1,000 tokens at 4 characters per token - ' +
        'trimming needs room for both a meaningful payload and the truncation report, so smaller caps are ignored.',
    'id_size_cap_mode': 'Truncate degrades an over-cap JSON response structurally - array tails and longest strings ' +
        'are dropped first, the document stays valid and a report states what was removed. ' +
        'Block refuses the response with an error naming the size and the cap, for endpoints where ' +
        'a partial answer would be misleading.',
    'id_min_size_threshold': 'Responses smaller than this many tokens skip all shaping and are delivered as they are, ' +
        'so ordinary small responses pay no processing cost.',
    'id_characters_per_token': 'How many characters one token is assumed to span when token counts are estimated - ' +
        'about 4 for English text. Fractional values like 3.5 work too.',

    'id_safeguards_strip_nulls': 'Removes keys whose value is null from objects at every nesting level. ' +
        'Array elements are kept, so positions never shift. Null-heavy API responses shrink substantially, ' +
        'which lowers the token cost of every tool call.',
    'id_safeguards_collapse_whitespace': 'Collapses runs of spaces, tabs and line breaks inside string values ' +
        'into a single space. Formatting whitespace carries no meaning for a model, ' +
        'yet it is billed as tokens like any other content.',
    'id_safeguards_strip_base64': 'Replaces long base64-encoded strings, such as embedded images or attachments, ' +
        'with a short marker stating the original size. A single encoded file can otherwise consume ' +
        'thousands of tokens without giving the model anything it can use.',

    'id_safeguards_pii_enabled': 'Scans string values for personally identifiable information, ' +
        'such as national identity numbers or IBANs, and replaces each match with a replacement naming the detector. ' +
        'The underlying data never reaches the client or its model.',
    'id_safeguards_pii_lands': 'The lands whose detectors run, e.g. Spain, Germany or International. ' +
        'Nothing is scanned until at least one land or detector is picked.',
    'id_safeguards_pii_detectors': 'Explicit detectors to run, picked by name. ' +
        'When set, this selection takes precedence over the lands.',
    'id_safeguards_pii_exclude': 'Detectors excluded from the selection made by lands and detectors. ' +
        'Use it to keep one detector out of an otherwise broad selection.',
    'id_safeguards_pii_validate': 'Verifies each match with its checksum algorithm before it is replaced. ' +
        'A number that merely looks like an identifier but fails its checksum is left untouched, ' +
        'which prevents false positives.',
    'id_safeguards_pii_stable_replacements': 'The same value receives the same numbered replacement throughout one response, ' +
        'so the model can still correlate occurrences of one person or account ' +
        'without ever seeing the underlying value.',

    'id_safeguards_normalize_unicode': 'Removes zero-width and bidirectional control characters ' +
        'and applies NFC normalization to string values. Such characters can smuggle hidden instructions ' +
        'into text and can split patterns that later detection stages need to match.',
    'id_safeguards_unicode_mode': 'Clean removes the characters and delivers the response. ' +
        'Reject refuses the whole response with an error, because zero-width and bidirectional ' +
        'control characters are a known prompt-injection vector - they can hide instructions ' +
        'inside otherwise normal text.',

    'id_safeguards_sanitize_markup': 'Removes script and style elements with their content, ' +
        'event handler attributes and javascript: URIs from HTML and Markdown in string values. ' +
        'These are the primary carriers of instructions a model could be tricked into following.',
    'id_safeguards_markup_mode': 'Clean removes the findings and delivers the response. ' +
        'Reject refuses the whole response with an error, treating active content ' +
        'in a tool response as a potential attack.',

    'id_safeguards_secrets_enabled': 'Scans string values for credential-shaped secrets, such as API tokens, ' +
        'private key blocks, AWS access keys, JWTs, bearer tokens or connection strings with inline passwords, ' +
        'and replaces each match with a stable replacement naming the detector.',

    'id_safeguards_url_policy_enabled': 'Checks every URL found in string values against the allow list. ' +
        'Unexpected URLs in tool responses can be used to exfiltrate data or to lure the model ' +
        'into fetching hostile content.',
    'id_safeguards_url_allow_list': 'Host suffixes whose URLs pass untouched, ' +
        'e.g. example.com also covers api.example.com. When empty, every URL is subject to the policy.',
    'id_safeguards_url_mode': 'Remove replaces the URL with a marker. ' +
        'Defang rewrites it so it cannot be followed, https becomes hxxps and dots become [.], ' +
        'which keeps the URL visible for analysis. Reject refuses the whole response.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
