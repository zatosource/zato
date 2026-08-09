// MCP gateway wizard - the micro-form descriptors and the step 2 rows.
//
// The popover engine itself comes from the wizard kit - this file declares
// which micro-forms the MCP wizard has and wires the size caps line that
// opens the first of them. The option cards under the More options line
// are wired in review.js, next to the summaries they carry.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var forms = wizard.forms;

// ////////////////////////////////////////////////////////////////////////

// A page is a list of entries. An entry is either one field spec, shown on
// its own line, or a list of field specs, shown side by side in one row.
// A spec's optional width pins a field down to that many pixels.
$.fn.zato.wizard_kit.forms.setup(wizard, {

    descriptors: {

        // The size caps live in mcp-size-caps.js - the gateway list opens
        // the very same micro-form on each of its rows
        'size_caps': $.fn.zato.gateway.mcp.size_caps_descriptor,

        'gateway_options': {
            title: 'Gateway options',
            pages: [[
                {field: 'validate_input', label: 'Validate input against each tool\'s schema', kind: 'checkbox'},
                {field: 'is_audit_log_active', label: 'Record each request in the audit log', kind: 'checkbox'}
            ]]
        },

        'compaction': {
            title: 'Compaction',
            pages: [[
                {field: 'safeguards_strip_nulls', label: 'Strip null fields', kind: 'checkbox'},
                {field: 'safeguards_collapse_whitespace', label: 'Collapse whitespace inside strings', kind: 'checkbox'},
                {field: 'safeguards_strip_base64', label: 'Strip embedded base64 blobs', kind: 'checkbox'}
            ]]
        }
    }
});

// ////////////////////////////////////////////////////////////////////////

// Wires up the step 2 rows that open micro-forms - the option cards under
// the More options line have their wiring in review.js.
forms.initRows = function() {

    $('#mcp-wizard-edit-size-caps').on('click', function() {
        forms.open('size_caps', this);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
