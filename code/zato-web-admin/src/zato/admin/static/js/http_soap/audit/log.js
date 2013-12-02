
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.AuditLogEntry = new Class({
    toString: function() {
        var s = '<AuditLogEntry name:{1}>';
        return String.format(s, this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.AuditLogEntry;
    $.fn.zato.data_table.new_row_func = null;
            
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
	
	$("#look-up-item").click($.fn.zato.http_soap.audit.look_up_item);
	$("#look-up-form").submit($.fn.zato.http_soap.audit.look_up_item);
})

$.fn.zato.http_soap.audit.look_up_item = function(e) {
    if(e) {
		e.preventDefault();
	}

	// connection, transport, conn_id, conn_name, cluster_id, q
	var pattern = '/zato/http-soap/audit/log/{0}/{1}/{2}/{3}/{4}/?query={5}';
	var href = String.format(pattern,
		$("#connection").val(),
		$("#transport").val(),
		$("#conn_id").val(),
		$("#conn_name").val(),
		$("#cluster_id").val(),
		$("#query").val()
	);
	window.location.href = href;
}
