
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HTTPSOAP = new Class({
    toString: function() {
        var s = '<HTTPSOAP id:{0} name:{1} is_active:{2} merge_url_params_req:{3} data_format:{4} serialization_type:{5}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)',
                                this.merge_url_params_req ? this.merge_url_params_req : '(none)',
                                this.data_format ? this.data_format : '(none)',
                                this.serialization_type ? this.serialization_type : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HTTPSOAP;
    $.fn.zato.data_table.new_row_func = $.fn.zato.http_soap.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path', 'service', 'security', 'sec_tls_ca_cert_id']);
    $.fn.zato.data_table.before_submit_hook = $.fn.zato.http_soap.data_table.before_submit_hook;

    $.each(['', 'edit-'], function(ignored, suffix) {

        var elem = $(String.format('#id_{0}serialization_type', suffix));
        elem.ready(function() {
            console.log(elem);
            console.log(elem.val());
            $.fn.zato.http_soap.data_table.toggle_sec_tls_ca_cert_id(suffix, elem.val() == 'suds');
            elem.change($.fn.zato.http_soap.data_table.on_serialization_change);
        });
    });
})

$.fn.zato.data_table.after_populate = function() {
    $.each(['', 'edit-'], function(ignored, suffix) {
        var elem = $(String.format('#id_{0}serialization_type', suffix));
        $.fn.zato.http_soap.data_table.toggle_sec_tls_ca_cert_id(suffix, elem.val() == 'suds');
    });
}

$.fn.zato.data_table.on_before_element_validation = function(elem) {
    if(elem.attr('id').endsWith('sec_tls_ca_cert_id')) {
        var form = elem.closest('form');
        var host = $(form.find("input[id$='host']")[0]);
        var is_https = host.val().startsWith('https');
        if(!is_https) {
            return false;
        }
    }
}

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

    var cluster_id = $(document).getUrlParam('cluster');
    var connection = $(document).getUrlParam('connection');
    var is_channel = connection == 'channel';
    var is_outgoing = connection == 'outgoing';
    var is_soap = data.transport == 'soap';

    var method_tr = '';
    var soap_action_tr = '';
    var soap_version_tr = '';
    var service_tr = '';
    var host_tr = '';
    var merge_url_params_req_tr = '';
    var url_params_pri_tr = '';
    var params_pri_tr = '';
    var serialization_type = item.serialization_type ? item.serialization_type : 'string';

    if(is_soap) {
        soap_action_tr += String.format('<td>{0}</td>', item.soap_action);
        soap_version_tr += String.format('<td>{0}</td>', item.soap_version);
    }

    if(is_channel) {
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

    if(is_channel) {
        row += String.format('<td>{0}</td>',
            String.format("<a href='/zato/http-soap/details/{3}/{4}/{1}/{0}/{2}/'>{0}</a>", 
            item.name, item.id, cluster_id, connection, data.transport));
    }
    else {
        row += String.format('<td>{0}</td>', item.name);
    }

    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    if(is_outgoing) {
        row += host_tr;
    }

    row += String.format('<td>{0}</td>', item.url_path);

    if(is_channel) {
        row += service_tr;
    }

    row += String.format('<td>{0}</td>', item.security_select);

    if(is_soap) {
        row += soap_action_tr;
        row += soap_version_tr;
    }

    if(is_channel) {
        row += method_tr;
        row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.service);
    }

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", '');
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.data_format);
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", 333);

    if(is_outgoing) {
        row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.ping_method);
        row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.pool_size);
        row += String.format("<td class='ignore item_id_{0}'>{0}</td>", serialization_type);
    }

    if(is_channel) {
        row += merge_url_params_req_tr;
        row += url_params_pri_tr;
        row += params_pri_tr;
    }

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.delete_({0});'>Delete</a>", item.id));

    if(is_outgoing) {
        row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
        if(item.serialization_type == 'suds') {
            row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.reload_wsdl({0});'>Reload WSDL</a>", item.id));
        }
        else {
        row += '<td></td>';
        }
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

$.fn.zato.http_soap.reload_wsdl = function(id) {

    var callback = function(data, status) {
        var success = status == 'success';
        $.fn.zato.user_message(success, data.responseText);
    }

    var url = String.format('./reload-wsdl/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
    $.fn.zato.post(url, callback, '', 'text');

}

$.fn.zato.http_soap.data_table.toggle_sec_tls_ca_cert_id = function(suffix, is_suds) {
    $(String.format('#id_{0}sec_tls_ca_cert_id', suffix)).prop('disabled', is_suds);
}

$.fn.zato.http_soap.data_table.on_serialization_change = function() {

    var is_edit = this.id.indexOf('edit') > 1;
    var suffix = is_edit ? 'edit-' : '';
    $.fn.zato.http_soap.data_table.toggle_sec_tls_ca_cert_id(suffix, this.value == 'suds');
}
