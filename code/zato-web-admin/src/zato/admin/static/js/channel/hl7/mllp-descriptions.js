// HL7 MLLP channel - the per-field help texts behind the "How does it work?"
// badges, keyed by the Django form field ids. One map shared by the
// full-page editor and the creation wizard, so a field is always
// explained with the same words no matter which page shows it.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.field_descriptions = {

    // Main tab
    'id_name': 'A unique name for this MLLP channel.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this channel accepts connections.<br>Inactive channels do not route messages.',
    'id_service': 'The service invoked for each<br>incoming HL7 message.',
    'id_use_rest': 'When on, HL7 messages can also be received<br>over REST in addition to MLLP.',
    'id_rest_only': 'When on, messages are received only over REST.<br>When off, messages are received over both<br>MLLP and REST.',
    'id_rest_url_path': 'URL path for the REST channel,<br>e.g. /api/hl7/v2.',
    'id_rest_security_id': 'Security definition used to authenticate<br>incoming REST requests.',
    'id_rest_security_groups': 'Security groups that can access<br>the REST channel.',

    // Destinations tab
    'destinations-respond-from-create': 'What the caller receives in response -<br>what the service returns or the response<br>of one, synchronously delivered, destination.',
    'destinations-respond-from-edit': 'What the caller receives in response -<br>what the service returns or the response<br>of one, synchronously delivered, destination.',

    // Routing tab
    'id_is_default': 'When enabled, this channel receives all messages<br>that no other channel claimed. Only one channel<br>can be the default at a time.',
    'id_msh3_sending_app': 'Only accept messages where MSH-3<br>(sending application) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh4_sending_facility': 'Only accept messages where MSH-4<br>(sending facility) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh5_receiving_app': 'Only accept messages where MSH-5<br>(receiving application) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh6_receiving_facility': 'Only accept messages where MSH-6<br>(receiving facility) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh9_message_type': 'Only accept messages where MSH-9.1<br>(message type, e.g. ADT, ORM) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh9_trigger_event': 'Only accept messages where MSH-9.2<br>(trigger event, e.g. A01, O01) equals this value.<br>Empty means any. Case-insensitive.',
    'id_msh11_processing_id': 'Only accept messages where MSH-11<br>(P=production, T=training, D=debugging)<br>equals this value. Empty means any. Case-insensitive.',
    'id_msh12_version_id': 'Only accept messages where MSH-12<br>(HL7 version, e.g. 2.5) equals this value.<br>Empty means any. Case-insensitive.',

    // Protocol tab
    'id_use_msh18_encoding': 'When on, the server reads the character encoding<br>from the MSH-18 field of each incoming message.<br>When off, or if MSH-18 is empty, the Encoding<br>setting is used instead.',
    'id_default_character_encoding': 'Character encoding used to decode raw bytes<br>when MSH-18 is absent or the MSH-18 toggle is off.',
    'id_recv_timeout': 'Per-recv timeout in milliseconds.<br>The connection stays open between messages.',
    'id_max_msg_size': 'Maximum allowed message size.<br>Frames exceeding this are rejected.',
    'id_start_seq': 'MLLP start-of-block byte in hex.<br>Standard: 0b.',
    'id_end_seq': 'MLLP end-of-block bytes in hex.<br>Standard: 1c 0d.',

    // Tolerance tab - wire-level preprocessing
    'id_normalize_line_endings': 'Converts CRLF and LF to CR<br>as required by HL7 v2.',
    'id_force_standard_delimiters': 'Rewrites MSH-2 to standard delimiters<br>(^~\\&amp;).',
    'id_repair_truncated_msh': 'Recovers messages with a corrupted<br>or malformed MSH segment.',
    'id_split_concatenated_messages': 'Splits a TCP payload containing multiple<br>MSH segments into separate messages.',

    // Tolerance tab - parser-level fixups
    'id_normalize_obx2_value_type': 'When OBX-2 is empty but OBX-5 has data,<br>fills OBX-2 with ST so the observation<br>value can be accessed.',
    'id_replace_invalid_obx2_value_type': 'Replaces unrecognized OBX-2 data types<br>with ST. Prevents parse failures from<br>nonstandard value type codes.',
    'id_normalize_invalid_escape_sequences': 'Removes stray backslash characters that<br>do not form a valid HL7 escape sequence.<br>Prevents parse errors from malformed escapes.',
    'id_normalize_obx8_abnormal_flags': 'Clears OBX-8 (Abnormal Flags) when it<br>contains the literal string "null" instead<br>of a valid flag value.',
    'id_normalize_quadruple_quoted_empty': 'Strips sequences of two or more consecutive<br>double-quote characters that some systems<br>emit as empty-field placeholders.',
    'id_allow_short_encoding_characters': 'Pads MSH-2 with standard encoding characters<br>when the sender provides fewer than the<br>required four.',
    'id_fix_off_by_one_field_index': 'Removes a spurious empty first field from<br>non-MSH segments. Fixes messages where a<br>leading separator shifts all field indices.',

    // Deduplication tab
    'id_dedup_ttl_value': 'How long to remember message control IDs (MSH-10).<br>Duplicates within this window are acknowledged<br>but not delivered to the service.<br>Zero turns deduplication off.',
    'id_dedup_ttl_unit': 'Time unit for the dedup window<br>(minutes, hours, or days).',

    // Logging tab
    'id_should_return_errors': 'When on, error details are included<br>in NAK responses sent to the sender (ERR segment).<br>When off, the NAK code is sent without details.',
    'id_should_log_messages': 'When on, each incoming message body and<br>routing decision is written to the server log<br>(server.log in the server directory).',
    'id_logging_level': 'Verbosity level for this channel\'s entries<br>in the server log (server.log).'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
