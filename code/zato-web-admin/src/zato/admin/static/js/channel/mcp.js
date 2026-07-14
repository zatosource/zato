
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MCPChannel = new Class({
    toString: function() {
        var s = '<MCPChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MCPChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.mcp.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'},
        {field: 'url_path', entity_type: 'http_soap', attr_name: 'url_path'}
    ];
    $.each(unique_constraints, function(constraint_idx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });

    $.fn.zato.data_table.before_submit_hook = function(form) {
        var action = form.attr('id').replace('-form', '');

        // Inject hidden inputs for both badge pickers into the same form
        $.fn.zato.badge_picker.inject_hidden_inputs(action, $.fn.zato.channel.mcp.badge_picker_config);

        // The security picker uses 'sec-' prefixed zone IDs but must inject into the same form
        form.find('input.badge-member-input[name^="mcp_security_"]').remove();
        var sec_assigned = $('#badge-zone-assigned-sec-' + action + ' .badge-zone-body .security-badge');
        sec_assigned.each(function() {
            $.fn.zato.channel.mcp.security_badge_picker_config.inject_hidden_input(form, $(this));
        });

        return true;
    };
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MCP-specific badge picker configuration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        return (a.name || '').localeCompare(b.name || '');
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return text_match;
    },

    inject_hidden_input: function(form, badge) {
        var service_name = badge.data('name');
        form.append($('<input/>', {
            type: 'hidden',
            name: 'mcp_service_' + service_name,
            value: service_name,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Security badge picker configuration (reuses groups-style badges with sec_type)
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.security_badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-security-type': item.sec_type, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-type', 'data-security-type': item.sec_type, 'text': item.sec_type_name || item.sec_type }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        var type_order = { 'basic_auth': 0, 'apikey': 1 };
        var order_a = type_order[a.sec_type] !== undefined ? type_order[a.sec_type] : 99;
        var order_b = type_order[b.sec_type] !== undefined ? type_order[b.sec_type] : 99;
        if (order_a !== order_b) return order_a - order_b;
        return (a.name || '').localeCompare(b.name || '');
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var security_type = badge.data('security-type') || '';

        var type_match = !type_val || security_type === type_val;
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return type_match && text_match;
    },

    inject_hidden_input: function(form, badge) {
        var security_type = badge.data('security-type');
        var security_id = badge.data('id');
        var member_key = security_type + '-' + security_id;
        form.append($('<input/>', {
            type: 'hidden',
            name: 'mcp_security_' + member_key,
            value: member_key,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.badge_picker = {};
$.fn.zato.channel.mcp.security_badge_picker = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.badge_picker.load = function(action, channel_id) {
    var url = '/zato/channel/mcp/get-service-list/';
    if (channel_id) {
        url += '?channel_id=' + channel_id;
    }

    console.log('[mcp.badge_picker.load] action=' + action + ' channel_id=' + channel_id + ' url=' + url);

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            console.log('[mcp.badge_picker.load] success, total=' + (items ? items.length : 0) + ' assigned=' + (items ? items.filter(function(x){return x.is_member}).length : 0));
            if (items) {
                for (var item_idx = 0; item_idx < items.length; item_idx++) {
                    if (items[item_idx].is_member) {
                        console.log('[mcp.badge_picker.load] assigned item: ' + JSON.stringify(items[item_idx]));
                    }
                }
            }
            $.fn.zato.badge_picker.init(action, items, $.fn.zato.channel.mcp.badge_picker_config);
        },
        error: function(xhr, status, err) {
            console.log('[mcp.badge_picker.load] error: status=' + status + ' err=' + err + ' response=' + xhr.responseText);
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.security_badge_picker.load = function(action, channel_id) {
    var sec_action = 'sec-' + action;
    var url = '/zato/channel/mcp/get-security-list/';
    if (channel_id) {
        url += '?channel_id=' + channel_id;
    }

    console.log('[mcp.security_badge_picker.load] action=' + action + ' sec_action=' + sec_action + ' channel_id=' + channel_id + ' url=' + url);

    var available_body = $('#badge-zone-available-' + sec_action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            var assigned_count = 0;
            if (items) {
                for (var item_idx = 0; item_idx < items.length; item_idx++) {
                    if (items[item_idx].is_member) {
                        assigned_count++;
                        console.log('[mcp.security_badge_picker.load] assigned: ' + JSON.stringify(items[item_idx]));
                    }
                }
            }
            console.log('[mcp.security_badge_picker.load] success, total=' + (items ? items.length : 0) + ' assigned=' + assigned_count);
            $.fn.zato.badge_picker.init(sec_action, items, $.fn.zato.channel.mcp.security_badge_picker_config);
        },
        error: function(xhr, status, err) {
            console.log('[mcp.security_badge_picker.load] error: status=' + status + ' err=' + err + ' response=' + xhr.responseText);
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.tab_labels = {
    access_control:   'Access control',
    response_shaping: 'Response shaping',
    compaction:       'Compaction',
    pii_removal:      'PII removal',
    content_safety:   'Content safety'
};

$.fn.zato.channel.mcp._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'mcp-edit-tab-panel-' : 'mcp-create-tab-panel-',
        default_tab:  'access_control',
        tab_labels:   $.fn.zato.channel.mcp.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.field_descriptions = {
    'id_name': 'A unique name for this gateway.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this gateway accepts requests.<br>MCP clients cannot reach inactive gateways.',
    'id_url_path': 'URL path the MCP endpoint is exposed under,<br>e.g. /mcp/. This is the address MCP clients,<br>such as AI assistants, connect to in order<br>to discover and invoke the assigned services.',

    'id_filter_expression': 'A JSONata expression applied server-side<br>to every tool response. Only what it selects<br>reaches the client. Empty means no filtering.',

    'id_safeguards_strip_nulls': 'Removes dictionary keys whose value is null,<br>recursively. Array elements are never dropped.',
    'id_safeguards_collapse_whitespace': 'Collapses runs of whitespace inside<br>string values to a single space.',
    'id_safeguards_strip_base64': 'Replaces base64-looking strings with a short<br>marker naming the original size.',

    'id_safeguards_pii_enabled': 'Whether PII is removed from responses.<br>Detected values are replaced with tokens.',
    'id_safeguards_pii_lands': 'Comma-separated land codes whose detectors<br>are used, e.g. es, de, fr, us, intl.<br>Empty means all lands.',
    'id_safeguards_pii_detectors': 'Explicit detector names, e.g. es_dni, intl_iban.<br>When set, this takes precedence over lands.',
    'id_safeguards_pii_exclude': 'Detector names removed from whatever<br>lands and detectors selected.',
    'id_safeguards_pii_validate': 'Whether checksums are validated. A value<br>with a broken checksum is not treated as PII.',
    'id_safeguards_pii_stable_tokens': 'The same value receives the same numbered<br>token within one response.',

    'id_safeguards_normalize_unicode': 'Removes zero-width and bidi control characters<br>and applies NFC normalization to string values.',
    'id_safeguards_unicode_mode': 'Clean removes smuggled characters and continues.<br>Reject refuses the whole response because such<br>characters are a potential sign of an attack.',

    'id_safeguards_sanitize_markup': 'Strips script and style elements, event handler<br>attributes and javascript: URIs from HTML<br>and markdown found in string values.',
    'id_safeguards_markup_mode': 'Clean removes the findings and continues.<br>Reject refuses the whole response because<br>scripts are a potential sign of an attack.',

    'id_safeguards_url_policy_enabled': 'Whether URLs in responses are checked<br>against the allow list.',
    'id_safeguards_url_allow_list': 'Comma-separated host suffixes whose URLs<br>pass untouched. Empty means every URL<br>is subject to the policy.',
    'id_safeguards_url_mode': 'Remove replaces a flagged URL with a marker.<br>Defang turns https into hxxps and dots into [.].<br>Reject refuses the whole response.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Master toggles in the response safeguards tab - each key is a checkbox that
// enables or disables the inputs listed under it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.safeguard_groups = {
    'safeguards_pii_enabled': [
        'safeguards_pii_lands',
        'safeguards_pii_detectors',
        'safeguards_pii_exclude',
        'safeguards_pii_validate',
        'safeguards_pii_stable_tokens'
    ],
    'safeguards_normalize_unicode': [
        'safeguards_unicode_mode'
    ],
    'safeguards_sanitize_markup': [
        'safeguards_markup_mode'
    ],
    'safeguards_url_policy_enabled': [
        'safeguards_url_allow_list',
        'safeguards_url_mode'
    ]
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._init_safeguard_toggles = function(action) {

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var groups = $.fn.zato.channel.mcp.safeguard_groups;

    $.each(groups, function(master_name, dependent_names) {

        var master = $('#' + prefix + master_name);

        // Enable or disable every dependent input based on the master checkbox ..
        var apply_state = function() {
            var is_enabled = master.is(':checked');
            $.each(dependent_names, function(dependent_idx, dependent_name) {
                var dependent = $('#' + prefix + dependent_name);
                dependent.prop('disabled', !is_enabled);
                dependent.toggleClass('routing-disabled', !is_enabled);
            });
        };

        // .. re-apply on every change and once now for the initial state.
        master.off('change.safeguards').on('change.safeguards', apply_state);
        apply_state();
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.create = function() {
    $.fn.zato.channel.mcp._reset_tabs('create');
    $.fn.zato.channel.mcp._init_safeguard_toggles('create');
    $.fn.zato.channel.mcp.badge_picker.load('create', null);
    $.fn.zato.channel.mcp.security_badge_picker.load('create', null);
    $.fn.zato.data_table._create_edit('create', 'Create a new MCP gateway', null);
    $('#create-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.channel.mcp.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.channel.mcp._reset_tabs('edit');
    $.fn.zato.channel.mcp._init_safeguard_toggles('edit');
    $.fn.zato.channel.mcp.badge_picker.load('edit', instance.id);
    $.fn.zato.channel.mcp.security_badge_picker.load('edit', instance.id);
    $.fn.zato.data_table._create_edit('edit', 'Update the MCP gateway', id);

    $('#edit-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.channel.mcp.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var service_count = data.service_count !== undefined ? data.service_count : ($("#service_count_"+item.id).text() || 0);
    var security_count = data.security_count !== undefined ? data.security_count : ($("#security_count_"+item.id).text() || 0);
    var url_path = item.url_path;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td class="text-center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', url_path);
    row += String.format('<td class="text-center" id="service_count_{0}">{1}</td>', item.id, service_count);
    row += String.format('<td class="text-center" id="security_count_{0}">{1}</td>', item.id, security_count);

    row += String.format('<td>{0}</td>', String.format('<a href="/zato/channel/mcp/export/{0}/">Export</a>', item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.mcp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.mcp.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'MCP gateway `{0}` deleted',
        'Are you sure you want to delete MCP gateway `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
