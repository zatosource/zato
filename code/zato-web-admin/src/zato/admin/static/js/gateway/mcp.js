
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
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'gateway-mcp'},
        {field: 'url_path', entity_type: 'http_soap', attr_name: 'url_path'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
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
// The badge picker configurations, their loaders, the PII multi-selects and
// the safeguard master toggles live in mcp-controls.js, and the help texts
// in mcp-descriptions.js - both files are shared with the wizard page.
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
// Response shaping fields kept in the data table's hidden columns - the order matches
// get_columns in the page and each value is what a field defaults to when an instance lacks it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.config = {
    'cluster_id': '1'
};

$.fn.zato.gateway.mcp.shaping_field_defaults = {
    'validate_input': false,
    'is_audit_log_active': false,
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

    row += String.format('<td><a href="/zato/audit-log/?source=mcp&object_name={0}&cluster={1}">Audit log</a></td>',
        encodeURIComponent(item.name), $.fn.zato.gateway.mcp.config.cluster_id);

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
