
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
