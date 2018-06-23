// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.CacheBuiltin = new Class({
    toString: function() {
        var s = '<CacheBuiltin id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.CacheBuiltin;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cache.builtin.data_table.new_row;
    $.fn.zato.data_table.add_row_hook = $.fn.zato.cache.builtin.add_row_hook;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'max_size', 'max_item_size', 'sync_method', 'persistent_storage']);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


$.fn.zato.cache.builtin.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new cache definition', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.builtin.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update cache definition', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.builtin.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_default = item.is_default == true
    var extend_expiry_on_get = item.extend_expiry_on_get == true
    var extend_expiry_on_set = item.extend_expiry_on_set == true

    if(is_default) {
        var delete_link = String.format("<span class='form_hint'>(Delete)</span>");
    }
    else {
        var delete_link = String.format("<a href=\"javascript:$.fn.zato.cache.builtin.delete_('{0}')\">Delete</a>", data.cache_id);
    }

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

    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/cache/builtin/details/entry/create/cache-id/{0}/cluster/{1}/\">Add a new entry</a>",
            data.cache_id, item.cluster_id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.cache.builtin.clear('{0}')\">Clear</a>", data.cache_id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.cache.builtin.edit('{0}')\">Edit</a>", data.cache_id));
    row += String.format('<td>{0}</td>', delete_link);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.cache_id);

    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_default);
    row += String.format("<td class='ignore'>{0}</td>", item.extend_expiry_on_get);
    row += String.format("<td class='ignore'>{0}</td>", item.extend_expiry_on_set);
    row += String.format("<td class='ignore'>{0}</td>", data.cache_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.builtin.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cache definition `{0}` deleted',
        'Are you sure you want to delete cache definition `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.builtin.clear = function(id) {

    var post_data = {};
    post_data['cluster_id'] = $('#cluster_id').val();
    post_data['cache_id'] = id;

    var _callback = function() {
        $('#cache_current_size_' + id).html('0');
    }

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cache `{0}` cleared',
        'Are you sure you want to remove all entries from cache <b>{0}</b>?',
        false, false, './clear/', post_data, false, _callback);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.builtin.add_row_hook = function(instance, elem_name, html_elem, data) {
    if(elem_name == 'cache_id') {
        instance.cache_id = data.cache_id;
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

