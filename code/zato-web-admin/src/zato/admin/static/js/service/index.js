
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Service = new Class({
    toString: function() {
        var s = '<Service id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Service;
    $.fn.zato.data_table.new_row_func = $.fn.zato.service.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['slow_threshold']);

})

$.fn.zato.service.get_sparklines_options = function() {
    return {'width':'90px', 'height':'12px', 'lineColor':'#555', 'spotColor':false, 'disableHiddenCheck':true, 'fillColor':false}
}

$.fn.zato.service.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new service', null);
}

$.fn.zato.service.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the service', id, $.fn.zato.service.add_stats);
}

$.fn.zato.service.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Service `{0}` deleted',
        'Are you sure you want to delete service `{0}`?',
        true);
}

$.fn.zato.service.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var instance = $.fn.zato.data_table.data[item.id];
    instance.name = data.name;

    var is_internal = $.fn.zato.to_bool(data.is_internal);

    var cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += '<td class="impexp"><input type="checkbox" /></td>';
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(data.name, cluster_id));
    row += String.format('<td>{0}</td>', data.impl_name);
    row += String.format('<td>{0}</td>', is_internal ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.service.edit('{0}')\">Edit</a>", data.id));
    if(data.may_be_deleted) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.service.delete_('{0}')\">Delete</a>", data.id));
    }
    else {
        row += '<td></td>';
    }

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);

    row += String.format("<td class='ignore'>{0}</td>", is_internal);
    row += String.format("<td class='ignore'>{0}</td>", data.slow_threshold);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}
