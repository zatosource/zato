
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SPNEGO = new Class({
    toString: function() {
        var s = '<SPNEGO id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SPNEGO;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.spnego.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'principal', 'keytab_path']);
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.spnego.field_descriptions = {
    'id_name': 'A unique name for this definition.<br>Used to identify it in outgoing connections,<br>logs and the dashboard.',
    'id_principal': 'The Kerberos principal that outgoing connections<br>authenticate as, e.g. zato@EXAMPLE.COM.',
    'id_keytab_path': 'Path to a keytab file on the server<br>with the keys of the principal.<br>Tickets are acquired and renewed from it automatically.',
    'id_target_spn': 'The remote service\'s principal name,<br>e.g. HTTP@api.example.com.<br>Leave empty to derive it from the target host name.',
    'id_needs_delegation': 'Whether to delegate credentials<br>to the remote service so it can act<br>on behalf of this principal.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.spnego.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a Kerberos definition', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.spnego.field_descriptions
    });
}

$.fn.zato.security.spnego.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit Kerberos definition', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.security.spnego.field_descriptions
    });
}

$.fn.zato.security.spnego.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.principal ? item.principal : '');
    row += String.format('<td>{0}</td>', item.keytab_path ? item.keytab_path : '');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.spnego.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.spnego.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.target_spn ? item.target_spn : '');
    row += String.format("<td class='ignore'>{0}</td>", $.fn.zato.to_bool(item.needs_delegation) ? 'True' : 'False');

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.spnego.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Kerberos definition `{0}` deleted',
        'Are you sure you want to delete Kerberos definition `{0}`?',
        true);
}
