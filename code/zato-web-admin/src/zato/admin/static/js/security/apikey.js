
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.APIKey = new Class({
    toString: function() {
        var s = '<APIKey id:{0} name:{1} username:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.username ? this.username : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.APIKey;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.apikey.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'username']);
})


$.fn.zato.security.apikey.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new API key', null);
}

$.fn.zato.security.apikey.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the API key', id);
}

$.fn.zato.security.apikey.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_rate_limit_active = $.fn.zato.like_bool(data.is_rate_limit_active) == true;
    var rate_limit_check_parent_def = $.fn.zato.like_bool(data.rate_limit_check_parent_def) == true;

    var item_header_id = "item_header_" + item.id;
    var item_header_value = $("#"+ item_header_id).text() || "X-API-Key";

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td id="{0}">{1}</td>', item_header_id, item_header_value);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change API key</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.apikey.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.apikey.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    row += String.format("<td class='ignore'>{0}</td>", is_rate_limit_active);
    row += String.format("<td class='ignore'>{0}</td>", data.rate_limit_type);
    row += String.format("<td class='ignore'>{0}</td>", data.rate_limit_def);
    row += String.format("<td class='ignore'>{0}</td>", rate_limit_check_parent_def);

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
