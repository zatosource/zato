
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.XPathSecurity = new Class({
    toString: function() {
        var s = '<XPathSecurity id:{0} name:{1} username:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.XPathSecurity;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.xpath.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username', 'username_expr']);
})


$.fn.zato.security.xpath.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new XPath security definition', null);
}

$.fn.zato.security.xpath.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the XPath security definition', id);
}

$.fn.zato.security.xpath.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    var password_expr = item.password_expr ? item.password_expr : '';
    var password_expr_html = password_expr ? password_expr : "<span class='form_hint'>(None)</span>";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.username_expr);
    row += String.format('<td>{0}</td>', password_expr_html);
    row += String.format('<td>{0}</td>', item.username);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.xpath.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.xpath.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", password_expr);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.xpath.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'XPath security definition `{0}` deleted',
        'Are you sure you want to delete XPath security definition `{0}`?',
        true);
}
