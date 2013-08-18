
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DeliveryItem = new Class({
    toString: function() {
        var s = '<DeliveryItem id:{0}, name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                 this.name ? this.name : '(none)'
                             );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.DeliveryItem;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pattern.delivery.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'target', 'target_type', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count',
            'last_updated', 'check_after', 'retry_repeats', 'retry_seconds', 'expire_after',
            'expire_arch_succ_after', 'expire_arch_fail_after']);
})


$.fn.zato.pattern.delivery.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new guaranteed delivery definition', null);
}

$.fn.zato.pattern.delivery.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the guaranteed delivery definition', id);
}

$.fn.zato.pattern.delivery.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.pattern.delivery.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Guaranteed delivery definition [{0}] deleted',
        'Are you sure you want to delete the guaranteed delivery definition [{0}]<br/>along with any in-progress tasks?',
        true);
}
