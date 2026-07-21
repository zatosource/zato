
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
    'id_name': 'A unique name for this connection.<br>Services obtain a client with self.fhir[name].',
    'id_address': 'Base URL of the FHIR server,<br>e.g. https://fhir.example.com.<br>Resource paths are appended to it.',
    'id_username': 'Security definition the connection<br>authenticates with, e.g. Basic Auth or OAuth.<br>Pick no security for open servers.',
    'id_extra': 'Additional client options, one key=value per line.<br>Passed as-is to the underlying FHIR client.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_pool_size': 'How many connections to the FHIR server<br>the pool keeps open. Each service using<br>the client concurrently needs one.<br>The default is 10.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 FHIR connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.hl7.fhir.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 FHIR connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.hl7.fhir.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.fhir.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
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
    row += String.format('<td><a href="/zato/audit-log/?source=fhir&object_name={0}&cluster=1">Audit log</a></td>', encodeURIComponent(item.name));

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
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
