// HL7 MLLP outgoing connections - the per-field help texts behind the
// "How does it work?" badges, keyed by the Django form field ids.
//
// They live apart from any one page so that a field is always explained
// with the same words no matter which page shows it - the wizard re-keys
// them onto its popover inputs rather than writing its own.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.field_descriptions = {

    // Where messages go
    'id_name': 'A unique name for this connection.<br>Services send messages through it with<br>self.mllp[name].send(data).',
    'id_address': 'The remote MLLP endpoint as host:port,<br>e.g. 10.20.30.40:2575.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',

    // Framing and timing
    'id_start_seq': 'MLLP frame start bytes, in hex, e.g. 0b.<br>Sent before each message. The default<br>matches the MLLP standard.',
    'id_end_seq': 'MLLP frame end bytes, in hex, e.g. 1c 0d.<br>Sent after each message. The default<br>matches the MLLP standard.',
    'id_max_msg_size': 'The biggest acknowledgment accepted, in bytes.<br>Larger replies are rejected.',
    'id_read_buffer_size': 'Size of the socket read buffer, in bytes.<br>The default of 32768 rarely needs changing.',
    'id_recv_timeout': 'How long to wait for the acknowledgment,<br>in milliseconds. Default is 250.',
    'id_max_wait_time': 'Default timeout in seconds for test messages<br>sent from the dashboard\'s Invoke screen.<br>Default is 5.',

    // TLS
    'id_tls_ca_path': 'Path to the CA bundle used to verify the server.<br>Setting it turns TLS on, minimum version 1.2.<br>Leave empty for a plaintext connection.',
    'id_tls_cert_path': 'Path to the client certificate presented<br>to the server, for mutual TLS.<br>Requires the CA path to be set too.',
    'id_tls_key_path': 'Path to the private key matching<br>the client certificate, for mutual TLS.',

    // Delivery options
    'id_pool_size': 'How many connections the pool keeps open<br>to the remote endpoint. Each concurrent send<br>uses one connection. Default is 10.',
    'id_max_retries': 'How many times a failed send is retried<br>before giving up. Default is 5.',
    'id_backoff_base_seconds': 'Delay in seconds before the first retry.<br>Each further retry doubles the delay,<br>up to the backoff cap. Default is 1.',
    'id_backoff_cap_seconds': 'Upper limit in seconds for the delay<br>between retries, no matter how many attempts<br>have been made already. Default is 300.',
    'id_backoff_jitter_percent': 'Random percentage applied to each retry delay<br>so that many senders do not all retry<br>at the same moment. Default is 10.',
    'id_circuit_breaker_threshold_percent': 'Failure percentage within the window that opens<br>the circuit and pauses sending to the endpoint.<br>Default is 50.',
    'id_circuit_breaker_window_seconds': 'Length in seconds of the rolling window<br>the failure percentage is computed over.<br>Default is 60.',
    'id_circuit_breaker_reset_seconds': 'How long in seconds the circuit stays open<br>before a trial message is let through again.<br>Default is 60.',

    // Logging and audit
    'id_should_log_messages': 'When on, outgoing messages and acknowledgments<br>are logged in full. Development only -<br>HL7 messages contain patient data.',
    'id_logging_level': 'Log level this connection uses for<br>its own log entries, e.g. INFO or DEBUG.',
    'id_is_audit_log_active': 'When on, each message this connection sends<br>and each acknowledgment it receives is<br>recorded in the audit log.'
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
