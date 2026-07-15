
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
    $.fn.zato.data_table.new_row_func = $.fn.zato.gateway.mcp.data_table.new_row;
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
        $.fn.zato.badge_picker.inject_hidden_inputs(action, $.fn.zato.gateway.mcp.badge_picker_config);

        // The security picker uses 'sec-' prefixed zone IDs but must inject into the same form
        form.find('input.badge-member-input[name^="mcp_security_"]').remove();
        var sec_assigned = $('#badge-zone-assigned-sec-' + action + ' .badge-zone-body .security-badge');
        sec_assigned.each(function() {
            $.fn.zato.gateway.mcp.security_badge_picker_config.inject_hidden_input(form, $(this));
        });

        return true;
    };

    // Multi-selects serialize one entry per selected option - the data table instance
    // needs all of them joined into one comma-separated value.
    $.fn.zato.data_table.add_row_hook = function(instance, name, html_elem, data) {
        if($.fn.zato.gateway.mcp.pii_select_names.indexOf(name) !== -1) {
            instance[name] = html_elem.val().join(',');
        }
    };

    $.fn.zato.gateway.mcp._init_token_combos();
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MCP-specific badge picker configuration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.badge_picker_config = {

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

$.fn.zato.gateway.mcp.security_badge_picker_config = {

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

$.fn.zato.gateway.mcp.badge_picker = {};
$.fn.zato.gateway.mcp.security_badge_picker = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.badge_picker.load = function(action, gateway_id) {
    var url = '/zato/gateway/mcp/get-service-list/';
    if (gateway_id) {
        url += '?gateway_id=' + gateway_id;
    }

    console.log('[mcp.badge_picker.load] action=' + action + ' gateway_id=' + gateway_id + ' url=' + url);

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
            $.fn.zato.badge_picker.init(action, items, $.fn.zato.gateway.mcp.badge_picker_config);
        },
        error: function(xhr, status, err) {
            console.log('[mcp.badge_picker.load] error: status=' + status + ' err=' + err + ' response=' + xhr.responseText);
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.security_badge_picker.load = function(action, gateway_id) {
    var sec_action = 'sec-' + action;
    var url = '/zato/gateway/mcp/get-security-list/';
    if (gateway_id) {
        url += '?gateway_id=' + gateway_id;
    }

    console.log('[mcp.security_badge_picker.load] action=' + action + ' sec_action=' + sec_action + ' gateway_id=' + gateway_id + ' url=' + url);

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
            $.fn.zato.badge_picker.init(sec_action, items, $.fn.zato.gateway.mcp.security_badge_picker_config);
        },
        error: function(xhr, status, err) {
            console.log('[mcp.security_badge_picker.load] error: status=' + status + ' err=' + err + ' response=' + xhr.responseText);
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.tab_labels = {
    access_control:   'Access control',
    response_shaping: 'Response shaping',
    pii_removal:      'PII removal',
    content_safety:   'Content safety'
};

$.fn.zato.gateway.mcp._reset_tabs = function(action) {
    var is_edit = action === 'edit';
    $.fn.zato.form_tabs.reset({
        div_id:       is_edit ? '#edit-div' : '#create-div',
        panel_prefix: is_edit ? 'mcp-edit-tab-panel-' : 'mcp-create-tab-panel-',
        default_tab:  'access_control',
        tab_labels:   $.fn.zato.gateway.mcp.tab_labels
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.field_descriptions = {
    'id_name': 'A unique name for this gateway.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this gateway accepts requests.<br>MCP clients cannot reach inactive gateways.',
    'id_url_path': 'URL path the MCP endpoint is exposed under,<br>e.g. /mcp/. This is the address MCP clients,<br>such as AI assistants, connect to in order<br>to discover and invoke the assigned services.',

    'id_allow_client_filters': 'Adds an optional response_filter parameter to every<br>tool, letting an AI agent pass its own JSONata<br>expression per call. The expression runs on the server<br>and the agent receives only the fields it asked for,<br>which cuts its context usage on every invocation.',
    'id_max_response_size': 'The maximum size of a tool response in tokens,<br>empty means no cap. Oversized tool responses are<br>the main way context windows get flooded - one<br>unbounded call can crowd out everything the agent<br>learned before it.',
    'id_size_cap_mode': 'Truncate degrades an over-cap JSON response<br>structurally - array tails and longest strings<br>are dropped first, the document stays valid<br>and a report states what was removed.<br>Block refuses the response with an error naming<br>the size and the cap, for endpoints where<br>a partial answer would be misleading.',
    'id_min_size_threshold': 'Responses smaller than this many tokens skip<br>all shaping and are delivered as they are, so<br>ordinary small responses pay no processing cost.',
    'id_characters_per_token': 'How many characters one token is assumed to span<br>when token counts are estimated - about 4 for<br>English text. Fractional values like 3.5 work too.',

    'id_safeguards_strip_nulls': 'Removes keys whose value is null from objects<br>at every nesting level. Array elements are kept,<br>so positions never shift. Null-heavy API responses<br>shrink substantially, which lowers the token cost<br>of every tool call.',
    'id_safeguards_collapse_whitespace': 'Collapses runs of spaces, tabs and line breaks<br>inside string values into a single space.<br>Formatting whitespace carries no meaning<br>for a model, yet it is billed as tokens<br>like any other content.',
    'id_safeguards_strip_base64': 'Replaces long base64-encoded strings, such as<br>embedded images or attachments, with a short<br>marker stating the original size. A single<br>encoded file can otherwise consume thousands<br>of tokens without giving the model anything<br>it can use.',

    'id_safeguards_pii_enabled': 'Scans string values for personally identifiable<br>information, such as national identity numbers<br>or IBANs, and replaces each match with a token<br>naming the detector. The underlying data<br>never reaches the client or its model.',
    'id_safeguards_pii_lands': 'The lands whose detectors run, e.g. Spain,<br>Germany or International. Nothing is scanned<br>until at least one land or detector is picked.',
    'id_safeguards_pii_detectors': 'Explicit detectors to run, picked by name.<br>When set, this selection takes precedence<br>over the lands.',
    'id_safeguards_pii_exclude': 'Detectors excluded from the selection made<br>by lands and detectors. Use it to keep one<br>detector out of an otherwise broad selection.',
    'id_safeguards_pii_validate': 'Verifies each match with its checksum algorithm<br>before it is replaced. A number that merely looks<br>like an identifier but fails its checksum is left<br>untouched, which prevents false positives.',
    'id_safeguards_pii_stable_tokens': 'The same value receives the same numbered token<br>throughout one response, so the model can still<br>correlate occurrences of one person or account<br>without ever seeing the underlying value.',

    'id_safeguards_normalize_unicode': 'Removes zero-width and bidirectional control<br>characters and applies NFC normalization<br>to string values. Such characters can smuggle<br>hidden instructions into text and can split<br>patterns that later detection stages<br>need to match.',
    'id_safeguards_unicode_mode': 'Clean removes the characters and delivers<br>the response. Reject refuses the whole response<br>with an error, because zero-width and bidirectional<br>control characters are a known prompt-injection<br>vector - they can hide instructions inside<br>otherwise normal text.',

    'id_safeguards_sanitize_markup': 'Removes script and style elements with their<br>content, event handler attributes and javascript:<br>URIs from HTML and Markdown in string values.<br>These are the primary carriers of instructions<br>a model could be tricked into following.',
    'id_safeguards_markup_mode': 'Clean removes the findings and delivers<br>the response. Reject refuses the whole response<br>with an error, treating active content<br>in a tool response as a potential attack.',

    'id_safeguards_url_policy_enabled': 'Checks every URL found in string values against<br>the allow list. Unexpected URLs in tool responses<br>can be used to exfiltrate data or to lure<br>the model into fetching hostile content.',
    'id_safeguards_url_allow_list': 'Comma-separated host suffixes whose URLs pass<br>untouched, e.g. example.com also covers<br>api.example.com. When empty, every URL<br>is subject to the policy.',
    'id_safeguards_url_mode': 'Remove replaces the URL with a marker.<br>Defang rewrites it so it cannot be followed,<br>https becomes hxxps and dots become [.],<br>which keeps the URL visible for analysis.<br>Reject refuses the whole response.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Response shaping fields kept in the data table's hidden columns - the order matches
// get_columns in the page and each value is what a field defaults to when an instance lacks it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.shaping_field_defaults = {
    'allow_client_filters': false,
    'max_response_size': '',
    'size_cap_mode': 'truncate',
    'min_size_threshold': '',
    'characters_per_token': '4.0',
    'safeguards_strip_nulls': false,
    'safeguards_collapse_whitespace': false,
    'safeguards_strip_base64': false,
    'safeguards_pii_enabled': false,
    'safeguards_pii_lands': '',
    'safeguards_pii_detectors': '',
    'safeguards_pii_exclude': '',
    'safeguards_pii_validate': false,
    'safeguards_pii_stable_tokens': false,
    'safeguards_normalize_unicode': false,
    'safeguards_unicode_mode': 'clean',
    'safeguards_sanitize_markup': false,
    'safeguards_markup_mode': 'clean',
    'safeguards_url_policy_enabled': false,
    'safeguards_url_allow_list': '',
    'safeguards_url_mode': 'remove'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Size caps - the two token fields are editable jQuery UI comboboxes with preset values.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.token_presets = {
    'max_response_size': ['5000', '10000', '25000', '50000', '100000'],
    'min_size_threshold': ['100', '250', '500', '1000']
};

$.fn.zato.gateway.mcp._init_token_combos = function() {

    $.each($.fn.zato.gateway.mcp.token_presets, function(field_name, presets) {

        var inputs = $('#id_' + field_name + ', #id_edit-' + field_name);

        inputs.autocomplete({
            source: presets,
            minLength: 0
        });

        // Clicking the input opens the full preset list right away - typing still filters it.
        inputs.on('click', function() {
            $(this).autocomplete('search', '');
        });
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PII removal - the lands, detectors and exclude fields are Chosen multi-selects.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.pii_select_config = {
    width: '100%',
    include_group_label_in_selected: true,
    search_contains: true
};

$.fn.zato.gateway.mcp.pii_select_names = [
    'safeguards_pii_lands',
    'safeguards_pii_detectors',
    'safeguards_pii_exclude'
];

// Chips of this group carry no land prefix - its detector names are global already.
$.fn.zato.gateway.mcp.pii_prefixless_group = 'International';

$.fn.zato.gateway.mcp._format_chip_prefixes = function(select) {

    // The chips live in the Chosen container that follows the underlying select ..
    var chosen = select.data('chosen');
    var container = select.next('.chosen-container');

    container.find('li.search-choice').each(function() {
        var chip = $(this);
        var group_label = chip.find('.group-name');

        if (!group_label.length) {
            return;
        }

        // .. chips of the prefixless group lose their land label entirely ..
        if (group_label.text() === $.fn.zato.gateway.mcp.pii_prefixless_group) {
            group_label.hide();
            return;
        }

        // .. and other chips show the short land code taken from the detector name.
        var option_index = chip.find('.search-choice-close').data('option-array-index');
        var detector_name = chosen.results_data[option_index].value;
        var land_code = detector_name.split('_')[0].toUpperCase();
        group_label.text(land_code);
    });
};

$.fn.zato.gateway.mcp._init_pii_selects = function(action) {

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var select_names = $.fn.zato.gateway.mcp.pii_select_names;

    for (var select_idx = 0; select_idx < select_names.length; select_idx++) {

        // Initialize Chosen on the select - a repeated call is a no-op ..
        var select = $('#' + prefix + select_names[select_idx]);
        select.chosen($.fn.zato.gateway.mcp.pii_select_config);

        // .. refresh the badges so a reopened dialog reflects the underlying options ..
        select.trigger('chosen:updated');

        // .. and keep the chip prefixes formatted, now and after every selection.
        select.off('change.pii_prefix').on('change.pii_prefix', function() {
            $.fn.zato.gateway.mcp._format_chip_prefixes($(this));
        });
        $.fn.zato.gateway.mcp._format_chip_prefixes(select);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp._populate_pii_selects = function(instance) {

    var select_names = $.fn.zato.gateway.mcp.pii_select_names;

    for(var select_idx = 0; select_idx < select_names.length; select_idx++) {

        // The instance keeps each multi-select's value as a comma-separated string ..
        var name = select_names[select_idx];
        var value = instance[name];
        var selected = [];

        if(value) {
            selected = value.split(',');
        }

        // .. apply it to the underlying select and let Chosen redraw its chips.
        var select = $('#id_edit-' + name);
        select.val(selected);
        select.trigger('chosen:updated');
        $.fn.zato.gateway.mcp._format_chip_prefixes(select);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Master toggles in the response safeguards tab - each key is a checkbox that
// enables or disables the inputs listed under it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.safeguard_groups = {
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

$.fn.zato.gateway.mcp._init_safeguard_toggles = function(action) {

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var groups = $.fn.zato.gateway.mcp.safeguard_groups;

    $.each(groups, function(master_name, dependent_names) {

        var master = $('#' + prefix + master_name);

        // Enable or disable every dependent input based on the master checkbox ..
        var apply_state = function() {
            var is_enabled = master.is(':checked');
            $.each(dependent_names, function(dependent_idx, dependent_name) {
                var dependent = $('#' + prefix + dependent_name);
                dependent.prop('disabled', !is_enabled);
                dependent.toggleClass('routing-disabled', !is_enabled);

                // Chosen mirrors the disabled state only when told the select changed
                if (dependent.hasClass('chosen-multi')) {
                    dependent.trigger('chosen:updated');
                }
            });
        };

        // .. re-apply on every change and once now for the initial state.
        master.off('change.safeguards').on('change.safeguards', apply_state);
        apply_state();
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.create = function() {
    $.fn.zato.gateway.mcp._reset_tabs('create');
    $.fn.zato.gateway.mcp._init_pii_selects('create');
    $.fn.zato.gateway.mcp._init_safeguard_toggles('create');
    $.fn.zato.gateway.mcp.badge_picker.load('create', null);
    $.fn.zato.gateway.mcp.security_badge_picker.load('create', null);
    $.fn.zato.data_table._create_edit('create', 'Create a new MCP gateway', null);
    $('#create-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.gateway.mcp.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.gateway.mcp._reset_tabs('edit');
    $.fn.zato.gateway.mcp._init_pii_selects('edit');
    $.fn.zato.gateway.mcp.badge_picker.load('edit', instance.id);
    $.fn.zato.gateway.mcp.security_badge_picker.load('edit', instance.id);
    $.fn.zato.data_table._create_edit('edit', 'Update the MCP gateway', id);

    // The generic populate above cannot handle multi-selects, so their values
    // are applied here, and only then can the master toggles reflect the populated state.
    $.fn.zato.gateway.mcp._populate_pii_selects(instance);
    $.fn.zato.gateway.mcp._init_safeguard_toggles('edit');

    $('#edit-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.gateway.mcp.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.data_table.new_row = function(item, data, include_tr) {
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

    row += String.format('<td>{0}</td>', String.format('<a href="/zato/gateway/mcp/export/{0}/">Export</a>', item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.gateway.mcp.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.gateway.mcp.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    // The response shaping fields live in hidden columns so a later edit sees fresh values -
    // fields the instance lacks, e.g. unchecked checkboxes absent from form serialization,
    // render as their defaults.
    $.each($.fn.zato.gateway.mcp.shaping_field_defaults, function(field_name, default_value) {
        var field_value = item[field_name];
        if(field_value === undefined) {
            field_value = default_value;
        }
        row += String.format("<td class='ignore'>{0}</td>", field_value);
    });

    if(include_tr) {
        row += '</tr>';
    }

    return row;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'MCP gateway `{0}` deleted',
        'Are you sure you want to delete MCP gateway `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
