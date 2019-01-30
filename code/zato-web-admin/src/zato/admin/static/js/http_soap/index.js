
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

    var security_name = item.security_id ? item.security_select : '<span class="form_hint">---</span>';

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

    /* 1,2 */
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    /* 3 */
    row += String.format('<td>{0}</td>', item.name);

    /* 4 */
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    /* 5 */
    if(is_outgoing) {
        row += host_tr;
    }

    /* 6 */
    row += String.format('<td>{0}</td>', item.url_path);

    /* 7,8 */
    if(is_channel) {
        row += service_tr;

        if(item.cache_id) {
            row += String.format('<td><a href="/zato/cache/{0}/?cluster={1}&amp;highlight={2}">{3}</a></td>',
                    data.cache_type, cluster_id, item.cache_id, data.cache_name);
        }
        else {
            row += '<td><span class="form_hint">---</span></td>';
        }

    }

    /* 9 */
    row += String.format('<td>{0}</td>', security_name);

    /* 10,11 */
    if(is_soap) {
        row += soap_action_tr;
        row += soap_version_tr;
    }

    /* 12,13,13a */
    if(is_channel) {
        row += method_tr;
        row += String.format("<td class='ignore'>{0}</td>", item.service);
        row += String.format("<td class='ignore'>{0}</td>", item.content_encoding);
    }

    /* 14,15,16 */
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);

    /* 17,18,19 */
    row += String.format("<td class='ignore'>{0}</td>", item.cache_id);
    row += String.format("<td class='ignore'>{0}</td>", item.cache_type);
    row += String.format("<td class='ignore'>{0}</td>", item.cache_expiry);

    /* 20,21 */
    row += String.format("<td class='ignore'>{0}</td>", item.has_rbac);
    row += String.format("<td class='ignore'>{0}</td>", item.data_format);

    /* 22,23a,23b */
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.sec_tls_ca_cert_id);
    row += String.format("<td class='ignore'>{0}</td>", item.match_slash);

    /* 24,25,26,27 */
    if(is_outgoing) {
        row += String.format("<td class='ignore'>{0}</td>", item.ping_method);
        row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
        row += String.format("<td class='ignore'>{0}</td>", serialization_type);
        row += String.format("<td class='ignore'>{0}</td>", item.content_type);
    }

    /* 28,29,30 */
    if(is_channel) {
        row += merge_url_params_req_tr;
        row += url_params_pri_tr;
        row += params_pri_tr;
    }

    /* 31,32 */
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.delete_({0});'>Delete</a>", item.id));

    if(is_outgoing) {

        /* 33 */
        row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

        /* 34 */
        if(item.serialization_type == 'suds') {
            row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.http_soap.reload_wsdl({0});'>Reload WSDL</a>", item.id));
        }
        else {
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
