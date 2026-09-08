// HL7 MLLP channel - the per-field help texts behind the "How does it work?"
// badges, keyed by the Django form field ids. One map for every page that
// shows a channel's fields, so a field is always explained with the same
// words wherever it appears.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.field_descriptions = {

    // Main
    'id_name': 'A unique name for this MLLP channel. Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel accepts connections. Inactive channels do not route messages.',
    'id_service': 'The service invoked for each incoming HL7 message.',
    'id_use_rest': 'When on, HL7 messages can also be received over REST in addition to MLLP.',
    'id_rest_only': 'When on, messages are received only over REST. ' +
        'When off, messages are received over both MLLP and REST.',
    'id_rest_url_path': 'URL path for the REST channel, e.g. /api/hl7/v2.',
    'id_rest_security_id': 'Security definition used to authenticate incoming REST requests.',
    'id_rest_security_groups': 'Security groups that can access the REST channel.',

    // Destinations
    'destinations-respond-from': 'What the caller receives in response - what the service returns ' +
        'or the response of one, synchronously delivered, destination.',

    // Routing
    'id_is_default': 'When enabled, this channel receives all messages that no other channel claimed. ' +
        'Only one channel can be the default at a time.',
    'id_msh3_sending_app': 'Only accept messages where MSH-3 (sending application) equals this value. ' +
        'Empty means any. Case-insensitive.',
    'id_msh4_sending_facility': 'Only accept messages where MSH-4 (sending facility) equals this value. ' +
        'Empty means any. Case-insensitive.',
    'id_msh5_receiving_app': 'Only accept messages where MSH-5 (receiving application) equals this value. ' +
        'Empty means any. Case-insensitive.',
    'id_msh6_receiving_facility': 'Only accept messages where MSH-6 (receiving facility) equals this value. ' +
        'Empty means any. Case-insensitive.',
    'id_msh9_message_type': 'Only accept messages where MSH-9.1 (message type, e.g. ADT, ORM) ' +
        'equals this value. Empty means any. Case-insensitive.',
    'id_msh9_trigger_event': 'Only accept messages where MSH-9.2 (trigger event, e.g. A01, O01) ' +
        'equals this value. Empty means any. Case-insensitive.',
    'id_msh11_processing_id': 'Only accept messages where MSH-11 (P=production, T=training, D=debugging) ' +
        'equals this value. Empty means any. Case-insensitive.',
    'id_msh12_version_id': 'Only accept messages where MSH-12 (HL7 version, e.g. 2.5) equals this value. ' +
        'Empty means any. Case-insensitive.',

    // Protocol
    'id_use_msh18_encoding': 'When on, the server reads the character encoding from the MSH-18 field ' +
        'of each incoming message. When off, or if MSH-18 is empty, the Encoding setting is used instead.',
    'id_default_character_encoding': 'Character encoding used to decode raw bytes when MSH-18 is absent ' +
        'or the MSH-18 toggle is off.',
    'id_recv_timeout': 'Per-recv timeout in milliseconds. The connection stays open between messages.',
    'id_max_msg_size': 'Maximum allowed message size. Frames exceeding this are rejected.',
    'id_start_seq': 'MLLP start-of-block byte in hex. Standard: 0b.',
    'id_end_seq': 'MLLP end-of-block bytes in hex. Standard: 1c 0d.',

    // Tolerance - parsing
    'id_should_parse_on_input': 'When on, each incoming message is parsed into a structured HL7 object ' +
        'before the service receives it. When off, the service receives the raw ER7 text.',
    'id_should_validate': 'When on, each parsed message is validated against the HL7 v2 grammar ' +
        'and a message that fails validation is rejected with an AE. Applies only when parsing is on.',

    // Tolerance - wire-level preprocessing
    'id_normalize_line_endings': 'Converts CRLF and LF to CR as required by HL7 v2.',
    'id_force_standard_delimiters': 'Rewrites MSH-2 to standard delimiters (^~\\&amp;).',
    'id_restore_truncated_msh': 'Recovers messages with a corrupted or malformed MSH segment.',
    'id_split_concatenated_messages': 'Splits a TCP payload containing multiple MSH segments ' +
        'into separate messages.',

    // Tolerance - parser-level fixups
    'id_normalize_obx2_value_type': 'When OBX-2 is empty but OBX-5 has data, fills OBX-2 with ST ' +
        'so the observation value can be accessed.',
    'id_replace_invalid_obx2_value_type': 'Replaces unrecognized OBX-2 data types with ST. ' +
        'Prevents parse failures from nonstandard value type codes.',
    'id_normalize_invalid_escape_sequences': 'Removes stray backslash characters that do not form ' +
        'a valid HL7 escape sequence. Prevents parse errors from malformed escapes.',
    'id_normalize_obx8_abnormal_flags': 'Clears OBX-8 (Abnormal Flags) when it contains the literal string ' +
        '"null" instead of a valid flag value.',
    'id_normalize_quadruple_quoted_empty': 'Strips sequences of two or more consecutive double-quote ' +
        'characters that some systems emit as empty-field placeholders.',
    'id_allow_short_encoding_characters': 'Pads MSH-2 with standard encoding characters when the sender ' +
        'provides fewer than the required four.',
    'id_fix_off_by_one_field_index': 'Removes a spurious empty first field from non-MSH segments. ' +
        'Fixes messages where a leading separator shifts all field indices.',

    // Deduplication
    'id_dedup_ttl_value': 'How long to remember message control IDs (MSH-10). ' +
        'Duplicates within this window are acknowledged but not delivered to the service. ' +
        'Zero turns deduplication off.',
    'id_dedup_ttl_unit': 'Time unit for the dedup window (minutes, hours, or days).',

    // Logging
    'id_should_return_errors': 'When on, error details are included in NAK responses sent to the sender ' +
        '(ERR segment). When off, the NAK code is sent without details.',
    'id_should_log_messages': 'When on, each incoming message body and routing decision is written ' +
        'to the server log (server.log in the server directory).',
    'id_is_audit_log_active': 'When on, each message this channel receives and each acknowledgment it sends ' +
        'is recorded in the audit log.',

    // Security
    'id_security_id': 'The mTLS definition naming the client certificate a sender has to connect with. ' +
        'Without one, a sender is accepted regardless of the certificate it presented.',
    'id_allowed_networks': 'Comma-separated addresses and CIDR blocks a sender\'s address has to fall inside, ' +
        'e.g. 10.0.0.0/8, 192.168.1.5. Empty allows any address.'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
