
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DeliveryItem = new Class({
    toString: function() {
        var s = '<DeliveryItem id:{0}, name:{1}, check_after:{2}, retry_repeats:{3}, retry_seconds:{4}>';
        return String.format(s, this.id ? this.id : '(none)',
                                 this.name ? this.name : '(none)',
                                 this.check_after ? this.check_after : '(none)',
                                 this.retry_repeats ? this.retry_repeats : '(none)',
                                 this.retry_seconds ? this.retry_seconds : '(none)'
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
            'in_progress_count', 'in_doubt_count', 'confirmed_count', 'failed_count',
            'last_updated', 'last_used', 'check_after', 'retry_repeats', 'retry_seconds', 'expire_after',
            'expire_arch_succ_after', 'expire_arch_fail_after']);

    $("#look-up-task").click($.fn.zato.pattern.look_up_task);
    $("#look-up-form").submit($.fn.zato.pattern.look_up_task);

})


$.fn.zato.pattern.delivery.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new guaranteed delivery definition', null);
}

$.fn.zato.pattern.delivery.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $('#item_name').text(instance.name);
    $('#id_edit-name').text(instance.name);
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
    row += String.format('<td>{0}</td>', data.name);
    row += String.format('<td>{0}</td>', item.target);
    row += String.format('<td>{0}</td>', data.short_def);
    row += String.format('<td>{0}</td>', '0');
    row += String.format('<td>n/a <a href="../{0}/{1}/{2}/{3}/{4}/">(list)</a></td>', item.name, item.target_type, item.target, 'in-progress-any', item.id);
    row += String.format('<td>n/a <a href="../{0}/{1}/{2}/{3}/{4}/">(list)</a></td>', item.name, item.target_type, item.target, 'in-doubt', item.id);
    row += String.format('<td>n/a <a href="../{0}/{1}/{2}/{3}/{4}/">(list)</a></td>', item.name, item.target_type, item.target, 'confirmed', item.id);
    row += String.format('<td>n/a <a href="../{0}/{1}/{2}/{3}/{4}/">(list)</a></td>', item.name, item.target_type, item.target, 'failed', item.id);
    row += String.format('<td><span class="form_hint">{0}</span></td>', 'n/a');
    row += String.format('<td><span class="form_hint">{0}</span></td>', 'n/a');
    row += String.format('<td><a href="javascript:$.fn.zato.pattern.delivery.edit(\'{0}\')">Edit</a></td>', item.id);
    row += String.format('<td><a href="javascript:$.fn.zato.pattern.delivery.delete_(\'{0}\')">Delete</a></td>', item.id);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

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
