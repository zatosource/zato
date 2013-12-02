
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HTTPSOAP = new Class({
    toString: function() {
        var s = '<HTTPSOAP id:{0} name:{1} is_active:{2} merge_url_params_req:{3}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)',
								this.merge_url_params_req ? this.merge_url_params_req : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HTTPSOAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.http_soap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path', 'service', 'security']);
})

$.fn.zato.http_soap.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new object', null);
}

$.fn.zato.http_soap.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the object', id);
}

$.fn.zato.http_soap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
	var merge_url_params_req = item.merge_url_params_req == true;
	
	var is_channel = $(document).getUrlParam('connection') == 'channel';
	var is_outgoing = $(document).getUrlParam('connection') == 'outgoing'

	var method_tr = '';
    var soap_action_tr = '';
    var soap_version_tr = '';
    var service_tr = '';
    var host_tr = '';
	var merge_url_params_req_tr = '';
	var url_params_pri_tr = '';
	var params_pri_tr = '';

    if(data.transport == 'soap') {
        soap_action_tr += String.format('<td>{0}</td>', item.soap_action);
        soap_version_tr += String.format('<td>{0}</td>', item.soap_version);
    }
    
    if(is_channel) {
        var cluster_id = $(document).getUrlParam('cluster');
        service_tr += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
		method_tr += String.format('<td>{0}</td>', item.method);
		
		merge_url_params_req_tr += String.format('<td class="ignore">{0}</td>', merge_url_params_req);
		url_params_pri_tr += String.format('<td class="ignore">{0}</td>', item.url_params_pri);
		params_pri_tr += String.format('<td class="ignore">{0}</td>', item.params_pri);
		
    }
    
    if(is_outgoing) {
        host_tr += String.format('<td>{0}</td>', item.host);
    }
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += host_tr;
    row += String.format('<td>{0}</td>', item.url_path);
    row += soap_action_tr;
    row += soap_version_tr;
    row += service_tr;
    row += String.format('<td>{0}</td>', item.security_select);
	row += method_tr;
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.delete_({0});'>Delete</a>", item.id));
	
	if(is_outgoing) {
		row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.ping({0});'>Ping</a>", item.id));
	}
	
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
	row += String.format("<td class='ignore'>{0}</td>", '');
	
	if(is_channel) {
		row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.service);
		row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.data_format);
	}
	
	if(is_outgoing) {
		row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.ping_method);
		row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.pool_size);
	}
	
	if(is_channel) {
		row += merge_url_params_req_tr;
		row += url_params_pri_tr;
		row += params_pri_tr;
	}

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.http_soap.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Object [{0}] deleted',
        'Are you sure you want to delete the object [{0}]?',
        true);
}

$.fn.zato.http_soap.ping = function(id) {

	var callback = function(data, status) {
		var success = status == 'success';
		$.fn.zato.user_message(success, data.responseText);
	}

	var url = String.format('./ping/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
	$.fn.zato.post(url, callback, '', 'text');

}
