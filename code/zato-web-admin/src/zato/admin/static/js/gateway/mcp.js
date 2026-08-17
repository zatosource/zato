
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

    // The connection type the name and URL path have to be unique within -
    // generic connection attributes are unique per type rather than across all of them
    connection_type: 'gateway-mcp',

    // Where a row goes when it is edited where it stands, its id following it
    inline_edit_url: '/zato/gateway/mcp/inline-edit/',

    // What the two flags read as, in the order a boolean puts them
    flag_labels: ['No', 'Yes'],

    // How long a confirmation takes to fade once it has been read
    confirmation_fade_ms: 200,

    // What a picker cell says when its list could not be brought over
    load_error_label: 'Could not load the list'
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

$.fn.zato.gateway.mcp.toggle_agent_filters = function(id, link) {
    $.fn.zato.gateway.mcp.toggle_flag(id, link, 'allow_agent_filters');
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

// The Name and URL path columns - each is edited in the small form the scheduler
// and the wizard's own name badge use, opened right above the value it changes.
$.fn.zato.gateway.mcp.edit_text = function(id, link, name, label) {

    var mcp = $.fn.zato.gateway.mcp;
    var instance = $.fn.zato.data_table.data[id];

    $.fn.zato.inline_edit.form_tippy({
        link_elem: link,
        title: label,
        input_width: '18em',
        rows: [
            // The uniqueness check is scoped to MCP gateways because generic
            // connection attributes are unique per connection type
            {name: name, label: label, value: instance[name],
                unique: {entity_type: 'generic_connection', attr_name: name,
                    filter: {filter_name: 'type_', filter_value: mcp.config.connection_type}}}
        ],
        validate: function(values) {
            if(!values[name]) {
                return 'This field is required: ' + label;
            }
            return '';
        },
        on_submit: function(values) {

            var data = {};
            data[name] = values[name];

            var on_saved = function(saved) {

                // The row stands at what came back
                instance[name] = saved[name];
                link.textContent = saved[name];
            };

            mcp.inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.edit_name = function(id, link) {
    $.fn.zato.gateway.mcp.edit_text(id, link, 'name', 'Name');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.edit_url_path = function(id, link) {
    $.fn.zato.gateway.mcp.edit_text(id, link, 'url_path', 'URL path');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Services and Security columns - each count opens a panel with the very badge
// picker the wizard uses, and a panel closed with its picks changed saves the row.
$.fn.zato.gateway.mcp.pickers = {

    services: {

        // What the picker's elements are named after - the loaders below fill
        // the zones in under ids derived from it
        element_action: 'row',

        title: 'Services',
        placeholder: 'Filter services...',

        // Where the panel opens once it has been moved or resized
        geometry_key: 'mcp-row-services-panel',

        width: 640,
        min_width: 420,

        saved_message: 'OK, services saved',

        // What the save travels under and what the count cell is named after
        post_name: 'services',
        cell_id_prefix: 'mcp-services-cell-',

        // What the panel opened on - a panel closed with the same picks saves nothing
        baseline: null,

        fetch: function(gateway_id, on_items, on_error) {
            $.fn.zato.gateway.mcp.badge_picker.fetch(gateway_id, on_items, on_error);
        },

        init: function(items) {
            $.fn.zato.badge_picker.init('row', items, $.fn.zato.gateway.mcp.badge_picker_config);
        },

        read: function() {
            var out = $.fn.zato.badge_picker.get_assigned_names('row');
            out.sort();
            return out;
        }
    },

    security: {

        // The loader adds the sec- prefix of its own accord, so it is called
        // with the plain action while the elements carry the prefixed one
        element_action: 'sec-row',

        title: 'Security',
        placeholder: 'Filter security...',

        geometry_key: 'mcp-row-security-panel',

        width: 640,
        min_width: 420,

        saved_message: 'OK, security saved',

        post_name: 'security',
        cell_id_prefix: 'mcp-security-cell-',

        baseline: null,

        fetch: function(gateway_id, on_items, on_error) {
            $.fn.zato.gateway.mcp.security_badge_picker.fetch(gateway_id, on_items, on_error);
        },

        init: function(items) {
            $.fn.zato.badge_picker.init('sec-row', items, $.fn.zato.gateway.mcp.security_badge_picker_config);
        },

        // The group members are keyed the way the groups page keys them,
        // the definition's type in front of its id
        read: function() {
            var out = [];
            $('#badge-zone-assigned-sec-row .badge-zone-body .security-badge').each(function() {
                var badge = $(this);
                out.push(badge.data('security-type') + '-' + badge.data('id'));
            });
            out.sort();
            return out;
        }
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The filter and the two zones one panel holds, the same markup the wizard's
// step 1 renders - the badge picker wires itself up to the ids derived from
// the action, so the panel only has to put them on the page.
$.fn.zato.gateway.mcp.pickers.build_body = function(content, spec) {

    var action = spec.element_action;

    content.innerHTML = '' +
        '<div class="badge-picker-filter" id="badge-filter-' + action + '">' +
            '<input type="text" id="badge-filter-text-' + action + '" placeholder="' + spec.placeholder + '" />' +
            '<button type="button" class="badge-filter-clear" id="badge-filter-clear-' + action + '">Clear</button>' +
        '</div>' +
        '<div class="badge-picker" id="badge-picker-' + action + '">' +
            '<div class="badge-zone" id="badge-zone-available-' + action + '">' +
                '<div class="badge-zone-header">Available (<span class="badge-zone-count">0</span>)</div>' +
                '<div class="badge-zone-body"></div>' +
            '</div>' +
            '<div class="badge-picker-resizer"></div>' +
            '<div class="badge-zone" id="badge-zone-assigned-' + action + '">' +
                '<div class="badge-zone-header">Assigned (<span class="badge-zone-count">0</span>)</div>' +
                '<div class="badge-zone-body"></div>' +
            '</div>' +
        '</div>';
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Opens one of the two panels on the row the cell belongs to. The list is brought
// over first and the panel comes on screen already populated, in one paint -
// a panel filled in after it opened would flicker as its zones got replaced.
$.fn.zato.gateway.mcp.pickers.open = function(link, spec) {

    var pickers = $.fn.zato.gateway.mcp.pickers;

    spec.fetch(link.dataset.id, function(items) {

        // Only one panel is on screen at a time - a click elsewhere while
        // the list was in flight may have opened another one by now
        $.fn.zato.wizard_kit.lines.closePanel();

        var panel_spec = {
            title: spec.title,
            width: spec.width,
            minWidth: spec.min_width,
            geometryKey: spec.geometry_key,

            build: function(content) {

                pickers.build_body(content, spec);
                spec.init(items);

                // What the panel opened on, compared against when it closes
                spec.baseline = spec.read();

                // What runs when the panel closes, however it was closed
                return function() {
                    pickers.on_close(link, spec);
                };
            }
        };

        $.fn.zato.wizard_kit.lines.openPanel(link, panel_spec);

    }, function() {
        $.fn.zato.gateway.mcp.inline.flash(link, $.fn.zato.gateway.mcp.config.load_error_label);
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.pickers.open_services = function(link) {
    $.fn.zato.gateway.mcp.pickers.open(link, $.fn.zato.gateway.mcp.pickers.services);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.pickers.open_security = function(link) {
    $.fn.zato.gateway.mcp.pickers.open(link, $.fn.zato.gateway.mcp.pickers.security);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Saves the row whose panel has just closed, a panel closed on what it opened with saving nothing
$.fn.zato.gateway.mcp.pickers.on_close = function(link, spec) {

    var picked = spec.read();

    if(JSON.stringify(picked) === JSON.stringify(spec.baseline)) {
        return;
    }

    var data = {};
    data[spec.post_name] = JSON.stringify(picked);

    var on_saved = function() {

        // The cell now counts what was just sent
        link.textContent = picked.length;
    };

    $.fn.zato.gateway.mcp.inline.save(link, link.dataset.id, data, on_saved, spec.saved_message);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'MCP gateway `{0}` deleted',
        'Are you sure you want to delete MCP gateway `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
