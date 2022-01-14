
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.RBACRolePermission = new Class({
    toString: function() {
        var s = '<RBACRolePermission id:{0} name:{1} client_def:{2} service_name:{3} role_id:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
                this.name ? this.name : '(none)',
                this.client_def ? this.client_def : '(none)',
                this.service_name ? this.service_name : '(none)',
                this.role_id ? this.role_id : '(none)');
    }

});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.RBACRolePermission;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.rbac.role_permission.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'client_def', 'service_id', 'role_id']);
})


$.fn.zato.security.rbac.role_permission.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new role permission', null);
}

$.fn.zato.security.rbac.role_permission.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the role permission', id);
}

$.fn.zato.security.rbac.role_permission.data_table.new_row = function(item, data, include_tr) {

    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    item.name = String.format("{0}:::{1}:::{2}", data.role_name, data.service_name, data.perm_name);

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.role_name);
    row += String.format('<td>{0}</td>', data.service_name);
    row += String.format('<td>{0}</td>', data.perm_name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.rbac.role_permission.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.role_id);
    row += String.format("<td class='ignore'>{0}</td>", item.service_id);
    row += String.format("<td class='ignore'>{0}</td>", item.perm_id);
    row += String.format("<td class='ignore'>{0}</td>", item.name);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.rbac.role_permission.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Role permission [{0}] deleted',
        'Are you sure you want to delete the role permission [{0}]?',
        true);
}
