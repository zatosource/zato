
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Service = new Class({
    toString: function() {
        var s = '<Service id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)'
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
    
    $.each($.fn.zato.data_table.data, function(idx, instance) {
        $.fn.zato.service.add_stats(instance, $.fn.zato.service.get_sparklines_options());
    });
    
})

$.fn.zato.service.add_stats = function(instance, sparklines_options) {
    var _callback = function(data, status) {
        var json = $.parseJSON(data.responseText);
        $.fn.zato.service.add_stats_to_table(instance.id, json.rate, json.mean, json.mean_trend, sparklines_options);
    };
    $.fn.zato.post(String.format('./last-stats/{0}/cluster/{1}/', instance.id, $('#cluster_id').val()), _callback, {}, 'json', true);
}

$.fn.zato.service.add_stats_callback = function(args) {
    $.fn.zato.service.add_stats(args['instance'], args['sparklines_options'])
}

$.fn.zato.service.add_stats_to_table = function(id, rate, mean, mean_trend, sparklines_options) {
    $('#rate_1h_' + id).text(rate);
    $('#mean_1h_' + id).text(mean);
    if(mean_trend != '0') {
        $('#trend_mean_1h_' + id).sparkline(mean_trend, sparklines_options);
    }
    else {
        $('#trend_mean_1h_' + id).text('n/a');
    }
}

$.fn.zato.service.get_sparklines_options = function() {
    return {'width':'90px', 'height':'12px', 'lineColor':'#555', 'spotColor':false, 'disableHiddenCheck':true, 'fillColor':false}
}

$.fn.zato.service.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new service', null);
}

$.fn.zato.service.edit = function(id) {
    $.fn.zato.data_table.on_submit_complete_callback = $.fn.zato.service.add_stats_callback
    $.fn.zato.data_table.on_submit_complete_callback_args = {
        'instance': $.fn.zato.data_table.data[id], 
        'sparklines_options':$.fn.zato.service.get_sparklines_options()
    }
    $.fn.zato.data_table._create_edit('edit', 'Update the service', id, $.fn.zato.service.add_stats);
}

$.fn.zato.service.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Service [{0}] deleted',
        'Are you sure you want to delete the service [{0}]?',
        true);
}

$.fn.zato.service.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }
    
    var instance = $.fn.zato.data_table.data[item.id];
    instance.name = data.name;
    
    var is_active = $.fn.zato.like_bool(item.is_active) == true;
    var is_internal = $.fn.zato.like_bool(data.is_internal) == true;
    
    var cluster_id = $(document).getUrlParam('cluster');
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += '<td class="impexp"><input type="checkbox" /></td>';
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(data.name, cluster_id));
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.impl_name);
    row += String.format('<td>{0}</td>', is_internal ? 'Yes' : 'No');
    row += String.format('<td id="rate_1h_{0}"></td>', item.id);
    row += String.format('<td id="mean_1h_{0}"></td>', item.id);
    row += String.format('<td><span id="trend_mean_1h_{0}"></span></td>', item.id);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.service.edit('{0}')\">Edit</a>", data.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.service.delete_('{0}')\">Delete</a>", data.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", data.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_internal);

    if(include_tr) {
        row += '</tr>';
    }
    
    return row;
}
