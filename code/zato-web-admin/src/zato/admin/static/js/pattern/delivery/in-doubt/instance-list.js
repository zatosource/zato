
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DeliveryItem = new Class({
    toString: function() {
        var s = '<DeliveryItem name:{1}>';
        return String.format(s, this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.DeliveryItem;
    $.fn.zato.data_table.new_row_func = $.fn.zato.pattern.delivery.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'target_type', 'tx_id', 'created', 'in_doubt_created_at', 
            'source_count', 'target_count', 'check_after', 'retry_repeats', 'retry_seconds']);
            
    $.each(['start', 'stop'], function(ignored, suffix) {
        var id = 'id_' + suffix;
        var jq_id = '#' + id;
        
		$(jq_id).datetimepicker(
			{
				'dateFormat':$('#js_date_format').val(),
				'timeFormat':$('#js_time_format').val(),
				'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
			}
		);

    })
})

$.fn.zato.pattern.delivery.in_doubt._update_all = function(cluster_id, url_pattern) {

	var tx_data = {};
	var tx_id;
	$("td[class^='ignore item_id_']").each(function(idx, item) {
		tx_id = $(item).text();
		tx_data[tx_id] = tx_id;
	});

    var _callback = function(data, status) {
        var success = status == 'success';
        var msg;
		if(success) {
		    msg = $.parseJSON(data.responseText)["message"];
		}
		else {
			msg = data.responseText;
		}
        $.fn.zato.user_message(success, msg);
		
		for(tx_id in tx_data) {
			$.fn.zato.data_table.row_updated(tx_id);
		}
    }
	
    $.ajax({
        type: 'POST',
        url: String.format(url_pattern, cluster_id),
        data: tx_data,
		dataType: 'json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: _callback
    });
}

$.fn.zato.pattern.delivery.in_doubt.resubmit_all = function(cluster_id) {
	$.fn.zato.pattern.delivery.in_doubt._update_all(cluster_id, '/zato/pattern/delivery/in-doubt/resubmit-many/{0}/');
}

$.fn.zato.pattern.delivery.in_doubt.delete_all = function(cluster_id) {
	$.fn.zato.pattern.delivery.in_doubt._update_all(cluster_id, '/zato/pattern/delivery/in-doubt/delete-many/{0}/');
}

$.fn.zato.pattern.delivery.in_doubt.resubmit = function(tx_id, cluster_id) {

    var _callback = function(data, status) {
        var success = status == 'success';
        var msg;
		if(success) {
		    msg = $.parseJSON(data.responseText)["message"];
		}
		else {
			msg = data.responseText;
		}
        $.fn.zato.user_message(success, msg);
		$.fn.zato.data_table.row_updated(tx_id);
    }
	
    $.ajax({
        type: 'POST',
        url: String.format('/zato/pattern/delivery/in-doubt/resubmit/{0}/{1}/', tx_id, cluster_id),
        data: '',
		dataType: 'json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: _callback
    });
}