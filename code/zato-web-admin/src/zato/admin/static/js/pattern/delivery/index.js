
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
    $.fn.zato.data_table.setup_forms(['name', 'target_type', 'tx_id', 'created', 'last_used', 
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
	
	$("#look-up-task").click($.fn.zato.pattern.look_up_task);
	$("#look-up-form").submit($.fn.zato.pattern.look_up_task);
})

$.fn.zato.pattern.delivery._update_all = function(cluster_id, url_pattern) {

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

$.fn.zato.pattern.delivery.resubmit_all = function(cluster_id) {
	$.fn.zato.pattern.delivery._update_all(cluster_id, '/zato/pattern/delivery/resubmit-many/{0}/');
}

$.fn.zato.pattern.delivery.delete_all = function(cluster_id) {
    var callback = function(ok) {
        if(ok) {
		    $.fn.zato.pattern.delivery._update_all(cluster_id, '/zato/pattern/delivery/delete-many/{0}/');
		}
	};
	jConfirm('Are you sure you want to delete all tasks from this page?', 'Please confirm', callback);	
}

$.fn.zato.pattern.delivery.resubmit = function(tx_id, cluster_id) {

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
        url: String.format('/zato/pattern/delivery/resubmit/{0}/{1}/', tx_id, cluster_id),
        data: '',
		dataType: 'json',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: _callback
    });
}