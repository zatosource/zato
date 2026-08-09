
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MCPGateway = new Class({
    toString: function() {
        var s = '<MCPGateway id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MCPGateway;
    $.fn.zato.data_table.parse();
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Creating and editing happen in the wizard on its own page - this file holds
// only what the list edits where it stands: the two flags each row turns over
// and the size caps popover, opened on the very micro-form the wizard uses.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.config = {
    cluster_id: '1',

    // Where a row goes when it is edited where it stands, its id following it
    inline_edit_url: '/zato/gateway/mcp/inline-edit/',

    // What the two flags read as, in the order a boolean puts them
    flag_labels: ['No', 'Yes'],

    // How long a confirmation takes to fade once it has been read
    confirmation_fade_ms: 200
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Everything a row changes without leaving the page, worded the way every inline edit is
$.fn.zato.gateway.mcp.inline = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Says beside a row that it went through, for as long as that takes to read
$.fn.zato.gateway.mcp.inline.flash = function(link, message) {

    var config = $.fn.zato.inline_edit.config;

    var instance = tippy(link, {
        content: message,
        theme: 'dark',
        trigger: 'manual',
        placement: config.confirmation_placement,
        hideOnClick: false,
        allowHTML: false
    });

    instance.show();

    // The tooltip leaves nothing of itself behind
    setTimeout(function() {
        instance.hide();
        setTimeout(function() {
            instance.destroy();
        }, $.fn.zato.gateway.mcp.config.confirmation_fade_ms);
    }, config.saved_hide_ms);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Sends what one row changed and hands the answer over to whoever asked for the save
$.fn.zato.gateway.mcp.inline.save = function(link, id, data, on_saved, saved_label) {

    var config = $.fn.zato.inline_edit.config;
    var url = $.fn.zato.gateway.mcp.config.inline_edit_url + id + '/';

    $.fn.zato.action_runner.run({
        link_elem: link,
        url: url,
        data: data,
        spinner_label: config.saving_label,
        details_modal_title: config.details_modal_title,
        show_delay_ms: config.saving_lead_in_ms,

        // The endpoint answers with JSON when it saved and with an error page when it did not
        parse: function(jqXHR) {

            var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

            return {
                is_success: is_http_ok,
                label: is_http_ok ? saved_label : config.error_label,
                details_title: config.error_label,
                details_body: jqXHR.responseText,
                details_lexer: '',
                status_code: jqXHR.status,
                jqXHR: jqXHR
            };
        },

        on_success: function(instance, result) {

            // The spinner makes way for the confirmation
            instance.hide();
            instance.destroy();

            on_saved(JSON.parse(result.jqXHR.responseText));

            $.fn.zato.gateway.mcp.inline.flash(link, saved_label);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Yes or No, the way a row shows a flag of its own
$.fn.zato.gateway.mcp.flag_label = function(value) {
    var out = $.fn.zato.gateway.mcp.config.flag_labels[value ? 1 : 0];
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Turns one flag of one row over, the opposite of what the row stands at being what is sent
$.fn.zato.gateway.mcp.toggle_flag = function(id, link, name) {

    var mcp = $.fn.zato.gateway.mcp;
    var instance = $.fn.zato.data_table.data[id];

    var data = {};
    data[name] = !$.fn.zato.to_bool(instance[name]);

    var on_saved = function(saved) {

        // The row stands at what came back
        instance[name] = saved[name];
        link.textContent = mcp.flag_label(saved[name]);
    };

    mcp.inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.toggle_active = function(id, link) {
    $.fn.zato.gateway.mcp.toggle_flag(id, link, 'is_active');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.toggle_client_filters = function(id, link) {
    $.fn.zato.gateway.mcp.toggle_flag(id, link, 'allow_client_filters');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Size caps column - each row's caps are edited in the very popover the wizard
// edits them in, hosted here on a handful of hidden fields instead of on a wizard form.
$.fn.zato.gateway.mcp.size_caps = {

    // The kit installs the popover engine here
    forms: {},

    config: {

        // Every element the popover makes is named after this
        idPrefix: 'mcp-row',

        // Which micro-form of the ones the kit was given is the one this page opens
        form_name: 'size_caps',

        // What a saved row is told beside itself
        saved_message: 'OK, size caps saved',

        // The fields the popover reads and writes, in the shape the endpoint stores them
        field_names: ['max_response_size', 'min_size_threshold', 'characters_per_token', 'size_cap_mode'],

        // What a row's fields are kept under between opens - the dataset keys
        // the page writes the values into, one per field above
        dataset_keys: ['maxResponseSize', 'minSizeThreshold', 'charactersPerToken', 'sizeCapMode'],

        // The row being edited, held while its popover is open
        link: null
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The hidden fields the popover reads and writes, named the way it expects
$.fn.zato.gateway.mcp.size_caps.field = function(name) {
    var out = $('#id_' + $.fn.zato.gateway.mcp.size_caps.config.idPrefix + '-' + name);
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// A cap is explained in the same words wherever it is shown, the popover inputs
// carrying ids of their own for the help to find them under
$.fn.zato.gateway.mcp.size_caps.helpDescriptions = function() {
    var size_caps = $.fn.zato.gateway.mcp.size_caps;
    var out = size_caps.forms.helpDescriptions($.fn.zato.gateway.mcp.field_descriptions);
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Opens the size caps of one row, the popover hanging off the very line that was clicked
$.fn.zato.gateway.mcp.size_caps.open = function(link) {

    var size_caps = $.fn.zato.gateway.mcp.size_caps;
    var config = size_caps.config;
    var row = document.getElementById('tr_' + link.dataset.id);

    config.link = link;

    for(var field_idx = 0; field_idx < config.field_names.length; field_idx++) {
        var name = config.field_names[field_idx];
        var dataset_key = config.dataset_keys[field_idx];
        size_caps.field(name).val(row.dataset[dataset_key]);
    }

    size_caps.forms.open(config.form_name, link);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Stores what the popover answered - the whole of a gateway is not the page's to send,
// so only the caps travel and the endpoint puts them into the gateway it names
$.fn.zato.gateway.mcp.size_caps.save = function() {

    var size_caps = $.fn.zato.gateway.mcp.size_caps;
    var config = size_caps.config;
    var link = config.link;

    var data = {};

    for(var field_idx = 0; field_idx < config.field_names.length; field_idx++) {
        var name = config.field_names[field_idx];
        data[name] = size_caps.field(name).val();
    }

    var on_saved = function(saved) {

        // The row now caps at what was just sent, so it says so and opens on it next time
        var row = document.getElementById('tr_' + link.dataset.id);

        for(var field_idx = 0; field_idx < config.field_names.length; field_idx++) {
            var name = config.field_names[field_idx];
            var dataset_key = config.dataset_keys[field_idx];
            row.dataset[dataset_key] = saved[name];
        }

        link.textContent = saved.size_cap_label;
    };

    $.fn.zato.gateway.mcp.inline.save(link, link.dataset.id, data, on_saved, config.saved_message);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The popover itself, the descriptor coming from the module both this page and the
// wizard build it from - all this page adds is where a saved row goes
$.fn.zato.wizard_kit.forms.setup($.fn.zato.gateway.mcp.size_caps, {
    descriptors: {'size_caps': $.fn.zato.gateway.mcp.size_caps_descriptor},
    showCancel: true,
    doneLabel: 'Save',
    onDone: $.fn.zato.gateway.mcp.size_caps.save
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'MCP gateway `{0}` deleted',
        'Are you sure you want to delete MCP gateway `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
