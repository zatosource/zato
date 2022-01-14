
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ElasticSearch = new Class({
    toString: function() {
        var s = '<ElasticSearch id:{0} name:{1} value:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.value ? this.value : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ElasticSearch;
    $.fn.zato.data_table.new_row_func = $.fn.zato.search.es.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'hosts', 'timeout', 'body_as']);
})


$.fn.zato.search.es.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new ElasticSearch connection', null);
}

$.fn.zato.search.es.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the ElasticSearch connection', id);
}

$.fn.zato.search.es.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', item.hosts);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.search.es.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.search.es.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.search.es.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'ElasticSearch connection [{0}] deleted',
        'Are you sure you want to delete the ElasticSearch connection [{0}]?',
        true);
}
