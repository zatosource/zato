
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7FHIROutconn = new Class({
    toString: function() {
        var s = '<HL7FHIROutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $.fn.zato.alerts_tab.init({config_id: 'out-fhir-alerts-tab-config'});
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7FHIROutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.hl7.fhir.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'pool_size',
        'security_id',
    ]);
    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'outconn-hl7-fhir'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.field_descriptions = {
    'id_name': 'A unique name for this connection. Services obtain a client with self.fhir[name].',
    'id_address': 'Base URL of the FHIR server, e.g. https://fhir.example.com. ' +
        'Resource paths are appended to it.',
    'id_username': 'Security definition the connection authenticates with, e.g. Basic Auth or OAuth. ' +
        'Pick no security for open servers.',
    'id_extra': 'Additional client options, one key=value per line. Passed as-is to the underlying FHIR client.',
    'id_is_active': 'Whether this connection can be used. Services cannot look up an inactive connection.',
    'id_is_audit_log_active': 'Whether this connection\'s requests and responses are recorded in the audit log. On by default.',
    'id_pool_size': 'How many connections to the FHIR server the pool keeps open. ' +
        'Each service using the client concurrently needs one. The default is 10.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The two tabs of a create or edit dialog - the connection's own fields and the Alerts tab
$.fn.zato.outgoing.hl7.fhir.tab_labels = function() {
    let out = {
        config: 'Config',
        alerts: $.fn.zato.alerts_tab.tab_label()
    };
    return out;
}

$.fn.zato.outgoing.hl7.fhir._reset_tabs = function(action) {
    $.fn.zato.form_tabs.reset({
        div_id:       '#' + action + '-div',
        panel_prefix: 'out-fhir-' + action + '-tab-panel-',
        default_tab:  'config',
        tab_labels:   $.fn.zato.outgoing.hl7.fhir.tab_labels()
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.create = function() {
    $.fn.zato.outgoing.hl7.fhir._reset_tabs('create');
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 FHIR connection', null);
    $.fn.zato.alerts_tab.bind({
        panel_id: 'out-fhir-create-tab-panel-alerts',
        field_prefix: ''
    });
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        fieldSelector: 'table.form-data tr, .decision-line',
        descriptions: $.extend({}, $.fn.zato.outgoing.hl7.fhir.field_descriptions, $.fn.zato.alerts_tab.descriptions())
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.edit = function(id) {
    $.fn.zato.outgoing.hl7.fhir._reset_tabs('edit');
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 FHIR connection', id);
    $.fn.zato.alerts_tab.bind({
        panel_id: 'out-fhir-edit-tab-panel-alerts',
        field_prefix: 'edit-'
    });
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        fieldSelector: 'table.form-data tr, .decision-line',
        descriptions: $.extend({}, $.fn.zato.outgoing.hl7.fhir.field_descriptions, $.fn.zato.alerts_tab.descriptions())
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let is_audit_log_active = item.is_audit_log_active == true;
    var security_name = item.security_id ? item.security_select : '<span class="form_hint">---</span>';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td><a href="{0}">{0}</a></td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", security_name || $.fn.zato.empty_value);

    // 3
    // The audit log of this connection's requests is filed under the connection's name
    row += String.format('<td><a href="/zato/audit-log/?source=fhir&object_name={0}&cluster=1">Audit log</a>{1}</td>',
        encodeURIComponent(item.name), is_audit_log_active ? '' : ' <span class="form_hint">(off)</span>');
    row += String.format('<td><a href="/zato/channel-usage/?sources=fhir&objects={0}&cluster=1">Usage</a></td>', encodeURIComponent(item.name));

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.hl7.fhir.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.hl7.fhir.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.extra);

    row += String.format("<td class='ignore'>{0}</td>", item.security_id);
    row += String.format("<td class='ignore'>{0}</td>", is_audit_log_active);

    // 7 - the health check
    row += String.format("<td class='ignore'>{0}</td>", item.health_check_run_every);
    row += String.format("<td class='ignore'>{0}</td>", item.health_check_run_unit);
    row += String.format("<td class='ignore'>{0}</td>", item.health_check_job_id);

    // 8 - the Alerts tab
    row += $.fn.zato.alerts_tab.hidden_cells(item);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 FHIR connection `{0}` deleted',
        'Are you sure you want to delete HL7 FHIR connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security', target_select: '#id_security_id'}
].concat($.fn.zato.alerts_tab.live_configs('')));

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id'}
].concat($.fn.zato.alerts_tab.live_configs('edit-')));

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
