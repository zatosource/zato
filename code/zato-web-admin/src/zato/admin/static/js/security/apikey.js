
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.APIKey = new Class({
    toString: function() {
        var s = '<APIKey id:{0} name:{1} header:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.header ? this.header : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.APIKey;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.apikey.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'header']);
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})


$.fn.zato.security.apikey.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create an API key', null);
}

$.fn.zato.security.apikey.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit API key', id);
}

$.fn.zato.security.apikey.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td id="item_header_{0}">{1}</td>', item.id, item.header);
    var cluster_id = $(document).getUrlParam('cluster');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change API key', 'API key', 'API key')\">Change API key</a>", item.id));
    row += String.format('<td><a href="/zato/security/apikey/rate-limiting/{0}/?cluster={1}&name={2}">Rate limiting</a></td>', item.id, cluster_id, encodeURIComponent(item.name));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.apikey.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.apikey.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.apikey.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'API key `{0}` deleted',
        'Are you sure you want to delete API key `{0}`?',
        true);
}
