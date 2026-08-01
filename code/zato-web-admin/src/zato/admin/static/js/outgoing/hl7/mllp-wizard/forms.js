// HL7 MLLP outgoing connection wizard - the micro-form descriptors and the
// rows that open them.
//
// The popover engine itself comes from the wizard kit - this file declares
// which micro-forms the wizard has and wires the summary links of both
// steps to them, together with the TLS switch, which is the one row whose
// state is derived rather than stored.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.outgoing.hl7.mllp.wizard;
var forms = wizard.forms;

// ////////////////////////////////////////////////////////////////////////

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
// A spec's optional width pins a field down to that many pixels.
$.fn.zato.wizard_kit.forms.setup(wizard, {

    descriptors: {

        // The bytes on the wire come first, the bounds a reply is read
        // under on a page of their own - the first page is what a receiving
        // system dictates, the second what this side is willing to accept
        'framing': {
            title: 'Framing',
            width: '430px',
            pages: [
                [
                    [
                        {field: 'start_seq', label: 'Start bytes', kind: 'text'},
                        {field: 'end_seq',   label: 'End bytes',   kind: 'text'}
                    ]
                ],
                [
                    [
                        {field: 'max_msg_size',     label: 'Max reply size (bytes)', kind: 'number', width: '190px'},
                        {field: 'read_buffer_size', label: 'Read buffer (bytes)',    kind: 'number', width: '190px'}
                    ]
                ]
            ]
        },

        'timing': {
            title: 'Timing',
            width: '430px',
            pages: [[
                [
                    {field: 'recv_timeout',  label: 'Wait for the acknowledgment (ms)', kind: 'number', width: '230px'},
                    {field: 'max_wait_time', label: 'Invoke page timeout (s)',          kind: 'number', width: '150px'}
                ]
            ]]
        },

        'tls': {
            title: 'TLS',
            width: '430px',
            pages: [[
                {field: 'tls_ca_path',   label: 'CA bundle',          kind: 'text', hint: 'Verifies the receiving system'},
                {field: 'tls_cert_path', label: 'Client certificate', kind: 'text', hint: 'For mutual TLS, where the far side asks for one'},
                {field: 'tls_key_path',  label: 'Client key',         kind: 'text'}
            ]]
        },

        'pool': {
            title: 'Connections kept open',
            pages: [[
                {field: 'pool_size', label: 'Pool size', kind: 'number'}
            ]]
        },

        'retries': {
            title: 'Retries',
            width: '430px',
            pages: [[
                [
                    {field: 'max_retries',            label: 'Attempts',        kind: 'number', width: '120px'},
                    {field: 'backoff_jitter_percent', label: 'Jitter (%)',      kind: 'number', width: '120px'}
                ],
                [
                    {field: 'backoff_base_seconds', label: 'First wait (s)',   kind: 'number', width: '180px'},
                    {field: 'backoff_cap_seconds',  label: 'Longest wait (s)', kind: 'number', width: '180px'}
                ]
            ]]
        },

        'breaker': {
            title: 'Sending pauses when it keeps failing',
            width: '430px',
            pages: [[
                [
                    {field: 'circuit_breaker_threshold_percent', label: 'Failures (%)', kind: 'number', width: '150px'},
                    {field: 'circuit_breaker_window_seconds',    label: 'Within (s)',   kind: 'number', width: '150px'}
                ],
                {field: 'circuit_breaker_reset_seconds', label: 'Try again after (s)', kind: 'number', width: '190px'}
            ]]
        },

        'logging': {
            title: 'Logging and audit',
            pages: [[
                {field: 'should_log_messages', label: 'Log each message to the server log', kind: 'checkbox'},
                {field: 'is_audit_log_active', label: 'Record each message in the audit log', kind: 'checkbox'},
                {field: 'logging_level',       label: 'Log level', kind: 'select'}
            ]]
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

forms.config_own = {

    // The rows whose summary link opens one popover, in template order
    editRows: [
        {linkId: 'mllp-outconn-wizard-edit-framing', descriptor: 'framing'},
        {linkId: 'mllp-outconn-wizard-edit-timing',  descriptor: 'timing'},
        {linkId: 'mllp-outconn-wizard-edit-tls',     descriptor: 'tls'},
        {linkId: 'mllp-outconn-wizard-edit-pool',    descriptor: 'pool'},
        {linkId: 'mllp-outconn-wizard-edit-retries', descriptor: 'retries'},
        {linkId: 'mllp-outconn-wizard-edit-breaker', descriptor: 'breaker'}
    ],

    // The switch that says whether this connection speaks TLS, and the
    // three paths behind it
    tlsToggleId: 'mllp-outconn-wizard-toggle-tls',
    tlsFields: ['tls_ca_path', 'tls_cert_path', 'tls_key_path'],

    // Turning TLS on with nothing filled in yet opens the popover on its own,
    // there being no point to a switch that is on and configures nothing
    tlsEditLinkId: 'mllp-outconn-wizard-edit-tls'
};

// ////////////////////////////////////////////////////////////////////////

// Whether this connection speaks TLS. The wrapper keys TLS off the CA
// bundle alone, so that is what the switch reflects rather than a flag of
// its own that could disagree with it.
forms.isTlsOn = function() {

    var out = wizard.field('tls_ca_path').val().trim() !== '';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Puts the switch back where the CA bundle says it belongs - a popover
// closed with the bundle cleared leaves the connection on plaintext, and a
// switch still reading as on would be saying otherwise.
forms.syncTlsToggle = function() {
    $('#' + forms.config_own.tlsToggleId).prop('checked', forms.isTlsOn());
};

// ////////////////////////////////////////////////////////////////////////

forms.initRows = function() {

    var ownConfig = forms.config_own;

    // Each summary link opens the popover its answers came from ..
    for(var rowIdx = 0; rowIdx < ownConfig.editRows.length; rowIdx++) {

        var row = ownConfig.editRows[rowIdx];

        // The descriptor name is read again when the click happens, so each
        // handler needs its own binding rather than the loop's variable
        $('#' + row.linkId).on('click', forms._buildOpener(row.descriptor));
    }

    // .. the logging card of step 2 opens the last of them ..
    $('#mllp-outconn-wizard-card-logging').on('click', forms._buildOpener('logging'));

    // .. and the TLS switch opens the paths behind it, or clears them. What
    // it starts as, and what it goes back to after the popover closes, is
    // the CA bundle's own doing through syncTlsToggle.
    $('#' + ownConfig.tlsToggleId).on('change', function() {

        if(this.checked) {

            // A switch that is on and configures nothing means nothing, so
            // the paths are asked for right away
            forms.open('tls', document.getElementById(ownConfig.tlsEditLinkId));
        }
        else {

            // Off means plaintext, and a CA bundle left behind would put
            // TLS back on the moment the connection is built
            for(var fieldIdx = 0; fieldIdx < ownConfig.tlsFields.length; fieldIdx++) {
                wizard.field(ownConfig.tlsFields[fieldIdx]).val('');
            }

            wizard.review.refreshSummaries();
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// One click handler opening one popover, anchored at the link that was
// clicked.
forms._buildOpener = function(descriptorName) {

    var out = function() {
        forms.open(descriptorName, this);
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
