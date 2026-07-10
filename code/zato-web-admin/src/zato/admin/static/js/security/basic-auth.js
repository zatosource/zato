
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.BasicAuth = new Class({
    toString: function() {
        var s = '<BasicAuth id:{0} name:{1} username:{2} realm:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)',
                                this.realm ? this.realm : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.BasicAuth;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.basic_auth.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username']);
    var unique_constraints = [
        {field: 'name', entity_type: 'security', attr_name: 'name'},
        {field: 'username', entity_type: 'security', attr_name: 'username',
            filter_name: 'sec_type', filter_value: 'basic_auth'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.basic_auth.field_descriptions = {
    'id_name': 'A unique name for this definition.<br>Used to identify it in channels, connections,<br>logs and the dashboard.',
    'id_username': 'The username part of the credentials.<br>Channels check it against incoming requests,<br>outgoing connections send it to the remote server.',
    'id_realm': 'The HTTP authentication realm, API by default.<br>Returned in WWW-Authenticate challenges<br>when a request carries no valid credentials.',
    'id_password': 'The password part of the credentials.<br>A random one is assigned at creation,<br>change it before the definition is used.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.security.basic_auth.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a Basic Auth definition', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.security.basic_auth.field_descriptions
    });
}

$.fn.zato.security.basic_auth.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit Basic Auth definition', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.security.basic_auth.field_descriptions
    });
}

$.fn.zato.security.basic_auth.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', item.realm);
    var cluster_id = $(document).getUrlParam('cluster');
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
    row += String.format('<td><a href="/zato/security/basic-auth/rate-limiting/{0}/?cluster={1}&name={2}">Rate limiting</a></td>', item.id, cluster_id, encodeURIComponent(item.name));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.basic_auth.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.basic_auth.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.basic_auth.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Basic Auth definition `{0}` deleted',
        'Are you sure you want to delete Basic Auth definition `{0}`?',
        true);
}
