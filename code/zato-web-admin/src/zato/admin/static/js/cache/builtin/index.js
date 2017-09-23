
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.CacheBuiltin = new Class({
    toString: function() {
        var s = '<CacheBuiltin id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.CacheBuiltin;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cache.builtin.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'max_size', 'max_item_size', 'sync_method', 'persistent_storage']);
})


$.fn.zato.cache.builtin.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new cache definition', null);
}

$.fn.zato.cache.builtin.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the cache definition', id);
}

$.fn.zato.cache.builtin.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_default = item.is_default == true
    var extend_expiry_on_get = item.extend_expiry_on_get == true
    var extend_expiry_on_set = item.extend_expiry_on_set == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', is_default ? "Yes":"No");
    row += String.format('<td>{0}</td>', "<span class='form_hint'>(n/a)</span>");
    row += String.format('<td>{0}</td>', item.max_size);
    row += String.format('<td>{0}</td>', item.max_item_size);
    row += String.format('<td>{0}</td>', extend_expiry_on_get ? "Yes":"No");
    row += String.format('<td>{0}</td>', extend_expiry_on_set ? "Yes":"No");
    row += String.format('<td>{0}</td>', item.sync_method);
    row += String.format('<td>{0}</td>', item.persistent_storage);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cache.builtin.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cache.builtin.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_default);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.extend_expiry_on_get);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.extend_expiry_on_set);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.cache.builtin.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cache definition `{0}` deleted',
        'Are you sure you want to delete the cache definition `{0}`?',
        true);
}
