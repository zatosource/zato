
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

        // Copy the filter expression from the editor pane into the hidden textarea
        var pane = $.fn.zato.channel.mcp._filter_panes[action];
        if (pane) {
            $.fn.zato.channel.mcp._filter_source(action).val(pane.getValue());
        }

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

    'id_filter_expression': 'A JSONata expression applied to every tool response<br>before it is returned. Only the fields the expression<br>selects are delivered, so a large upstream response<br>becomes a small, purpose-built one and the client<br>spends context only on data it actually needs.',

    'id_safeguards_strip_nulls': 'Removes keys whose value is null from objects<br>at every nesting level. Array elements are kept,<br>so positions never shift. Null-heavy API responses<br>shrink substantially, which lowers the token cost<br>of every tool call.',
    'id_safeguards_collapse_whitespace': 'Collapses runs of spaces, tabs and line breaks<br>inside string values into a single space.<br>Formatting whitespace carries no meaning<br>for a model, yet it is billed as tokens<br>like any other content.',
    'id_safeguards_strip_base64': 'Replaces long base64-encoded strings, such as<br>embedded images or attachments, with a short<br>marker stating the original size. A single<br>encoded file can otherwise consume thousands<br>of tokens without giving the model anything<br>it can use.',

    'id_safeguards_pii_enabled': 'Scans string values for personally identifiable<br>information, such as national identity numbers<br>or IBANs, and replaces each match with a token<br>naming the detector. The underlying data<br>never reaches the client or its model.',
    'id_safeguards_pii_lands': 'Comma-separated land codes selecting which<br>detectors run, e.g. es, de, fr, us, intl.<br>Leave empty to run detectors for all lands.',
    'id_safeguards_pii_detectors': 'Explicit detector names to run, e.g. es_dni<br>or intl_iban. When set, this list takes<br>precedence over the lands selection.',
    'id_safeguards_pii_exclude': 'Detector names excluded from the selection made<br>by lands and detectors, e.g. us_ssn. Use it to keep<br>one detector out of an otherwise broad selection.',
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
// Response shaping - the filter expression editor pane and its demos.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._filter_panes = {};

// The sample document the demo expressions run against.
$.fn.zato.channel.mcp.filter_demo_sample = {
    'customer': {'name': 'Jane Smith', 'email': 'jane.smith@example.com'},
    'orders': [
        {'id': 1, 'total': 250.0, 'status': 'shipped'},
        {'id': 2, 'total': 120.5, 'status': 'pending'}
    ]
};

// Each demo loads a ready expression into the editor.
$.fn.zato.channel.mcp.filter_demos = [
    {name: 'select-fields', label: 'Select fields', expression: '{"name": customer.name, "email": customer.email}'},
    {name: 'aggregate', label: 'Aggregate', expression: '{"order_count": $count(orders), "grand_total": $sum(orders.total)}'},
    {name: 'reshape-list', label: 'Reshape list', expression: 'orders.{"order": id, "value": total}'}
];

$.fn.zato.channel.mcp.filter_demo_config = {
    overlay_title: 'Filter expression demo',
    input_tab_label: 'Sample input',
    result_tab_label: 'Result',
    no_match_text: 'No match - the expression selected nothing.',
    run_label: 'Run'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._filter_source = function(action) {
    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    return $('#' + prefix + 'filter_expression');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._show_filter_demo_result = function(result_text) {

    var config = $.fn.zato.channel.mcp.filter_demo_config;
    var sample = $.fn.zato.channel.mcp.filter_demo_sample;
    var sample_text = JSON.stringify(sample, null, 2);

    $.fn.zato.highlight_pane.open_overlay({
        title: config.overlay_title,
        editable: false,
        tabs: [
            {label: config.input_tab_label, text: sample_text, ace_mode: 'ace/mode/json'},
            {label: config.result_tab_label, text: result_text, ace_mode: 'ace/mode/json'}
        ],
        buttons: [$.fn.zato.highlight_pane.buttons.copy()]
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._run_filter_demo = function(pane) {

    var config = $.fn.zato.channel.mcp.filter_demo_config;
    var sample = $.fn.zato.channel.mcp.filter_demo_sample;
    var expression_text = pane.getValue();

    // Compile the expression first - a syntax error is reported in the result tab ..
    var expression;
    try {
        expression = jsonata(expression_text);
    }
    catch(error) {
        $.fn.zato.channel.mcp._show_filter_demo_result(error.message);
        return;
    }

    // .. evaluate it against the sample document and show both side by side.
    expression.evaluate(sample).then(function(result) {
        var result_text;
        if (result === undefined) {
            result_text = config.no_match_text;
        }
        else {
            result_text = JSON.stringify(result, null, 2);
        }
        $.fn.zato.channel.mcp._show_filter_demo_result(result_text);
    }).catch(function(error) {
        $.fn.zato.channel.mcp._show_filter_demo_result(error.message);
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.mcp._init_filter_pane = function(action) {

    var config = $.fn.zato.channel.mcp.filter_demo_config;

    // Tear down the pane from a previous opening of this dialog ..
    var previous = $.fn.zato.channel.mcp._filter_panes[action];
    if (previous) {
        previous.destroy();
    }

    // .. one button per demo expression ..
    var buttons = [];
    $.each($.fn.zato.channel.mcp.filter_demos, function(demo_idx, demo) {
        buttons.push({
            id: 'filter-demo-' + demo.name + '-' + action,
            label: demo.label,
            on_click: function(button_element, pane) {
                pane.setValue(demo.expression);
            }
        });
    });

    // .. plus one that evaluates the current expression against the sample document ..
    buttons.push({
        id: 'filter-demo-run-' + action,
        label: config.run_label,
        on_click: function(button_element, pane) {
            $.fn.zato.channel.mcp._run_filter_demo(pane);
        }
    });

    // .. mount the editor, seeded from the hidden textarea ..
    var source = $.fn.zato.channel.mcp._filter_source(action);

    var pane = $.fn.zato.highlight_pane.init({
        container: '#filter-expression-pane-' + action,
        text: source.val(),
        editable: true,
        ace_mode: 'ace/mode/javascript',
        ace_options: {minLines: 5, maxLines: 8},
        buttons: buttons
    });

    $.fn.zato.channel.mcp._filter_panes[action] = pane;

    // .. and re-seed the pane whenever the dialog opens, after its form was populated.
    var div_id = action === 'edit' ? '#edit-div' : '#create-div';
    $(div_id).off('dialogopen.filter_pane').on('dialogopen.filter_pane', function() {
        pane.setValue(source.val());
    });
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
    $.fn.zato.channel.mcp._init_filter_pane('create');
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
    $.fn.zato.channel.mcp._init_filter_pane('edit');
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
