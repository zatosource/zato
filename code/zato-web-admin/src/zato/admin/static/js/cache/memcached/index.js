
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.CacheMemcached = new Class({
    toString: function() {
        var s = '<CacheMemcached id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.CacheMemcached;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cache.memcached.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'servers']);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.memcached.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new cache definition', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.memcached.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the cache definition', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.memcached.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true
    var is_default = item.is_default == true
    var is_debug = item.is_debug == true

    if(is_default) {
        var delete_link = String.format("<span class='form_hint'>(Delete)</span>");
    }
    else {
        var delete_link = String.format("<a href='javascript:$.fn.zato.cache.memcached.delete_({0});'>Delete</a>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', is_default ? "Yes":"No");
    row += String.format('<td>{0}</td>', item.servers);
    row += String.format('<td>{0}</td>', is_debug ? "Yes":"No");
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cache.memcached.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', delete_link);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_default);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cache.memcached.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Cache definition `{0}` deleted',
        'Are you sure you want to delete the cache definition `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
