// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// The row of the listing a saved channel or outgoing connection is rendered as - the cells the table shows
// and the hidden ones the edit form reads its values back from.
// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    $.fn.zato.toggle_visible_hidden(".api-client-groups-options-block", false);

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var audit_object_type_label = '';
    var is_active = item.is_active == true;
    var is_audit_log_active = item.is_audit_log_active == true;
    var merge_url_params_req = item.merge_url_params_req == true;

    var cluster_id = $(document).getUrlParam('cluster');
    var connection = $(document).getUrlParam('connection');
    var is_channel = connection == 'channel';
    var is_outgoing = connection == 'outgoing';
    var is_soap = data.transport == 'soap';

    var soap_action_tr = '';
    var soap_version_tr = '';
    var service_tr = '';
    var host_tr = '';
    var merge_url_params_req_tr = '';
    var url_params_pri_tr = '';
    var params_pri_tr = '';

    var data_encoding = '';

    // The reply carries the canonical security name and href, the same values the listing renders
    var has_security = Boolean(data.security_name);

    if(is_soap) {
        soap_action_tr += String.format('<td>{0}</td>', item.soap_action);
        soap_version_tr += String.format('<td>{0}</td>', item.soap_version);
        audit_object_type_label += 'SOAP ';
    }
    else {
        audit_object_type_label += 'REST ';
    }

    if(is_channel) {

        // Internal services stay where they are - the channels running them are not to be repointed
        if($.fn.zato.data_table.internal_services[item.service]) {
            service_tr += String.format('<td>{0}</td>', item.service);
        }
        else {
            service_tr += String.format('<td><a href="javascript:void(0)" class="http-soap-service-cell" data-id="{0}">{1}</a></td>', item.id, item.service);
        }
        merge_url_params_req_tr += String.format('<td class="ignore">{0}</td>', merge_url_params_req);
        url_params_pri_tr += String.format('<td class="ignore">{0}</td>', item.url_params_pri);
        params_pri_tr += String.format('<td class="ignore">{0}</td>', item.params_pri);
        audit_object_type_label += 'channel';
    }

    if(is_outgoing) {
        host_tr += String.format('<td>{0}</td>', item.host);
        audit_object_type_label += 'outgoing connection';
    }

    /* 1, 2 */
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    /* 3 */
    var is_gateway_channel = false;
    if(is_channel) {
        if(!is_soap) {
            is_gateway_channel = item.service === $.fn.zato.http_soap.gateway_trigger_service;
        }
    }
    // Badges precede the name - one for gateway channels, one for deprecated ones ..
    var name_badges = '';

    if(is_gateway_channel) {
        name_badges += '<span class="gateway-badge">GW</span>';
    }

    if(is_channel && !is_soap && item.is_deprecated == true) {
        name_badges += '<span class="deprecated-badge">Deprecated</span>';
    }

    // .. and the name cell combines them with the name itself.
    row += String.format(
        '<td>{0}<a href="javascript:void(0)" data-id="{1}" onclick="$.fn.zato.http_soap.inline.edit_name(\'{1}\', this)"><span class="name-value">{2}</span></a></td>',
        name_badges, item.id, item.name);

    /* 4 */
    row += String.format(
        '<td style="text-align:center"><a href="javascript:void(0)" data-id="{0}" onclick="$.fn.zato.http_soap.inline.toggle_active(\'{0}\', this)">{1}</a></td>',
        item.id, is_active ? 'Yes' : 'No');

    /* 5 */
    if(is_outgoing) {
        row += host_tr;
    }

    /* 6 */
    row += String.format(
        '<td><a href="javascript:void(0)" data-id="{0}" onclick="$.fn.zato.http_soap.inline.edit_url_path(\'{0}\', this)">{1}</a></td>',
        item.id, item.url_path);

    /* 7 */
    if(is_channel) {
        row += service_tr;
    }

    /* 9 - one link for the whole cell. A channel's opens the tabbed security panel and says
       what the row holds - the definition, the groups beneath it, or the invitation when
       it holds neither. An outgoing connection's opens the definition menu. */
    var security_cell = '';

    if(is_channel) {

        // Rows without any group say "0 groups, ..." and the cell shows nothing for them
        var has_groups = data.security_groups_info && data.security_groups_info.charAt(0) != '0';
        var cell_text = '';

        if(has_security) {
            cell_text += data.security_name;
        }
        if(has_groups) {
            cell_text += (has_security ? '<br/>' : '') + data.security_groups_info;
        }
        if(!cell_text) {
            cell_text = $.fn.zato.http_soap.inline.config.empty_security_label;
        }

        security_cell = String.format(
            '<a href="javascript:void(0)" class="http-soap-security-tabs-cell" data-id="{0}" onclick="$.fn.zato.http_soap.inline.open_security_menu(this)">{1}</a>',
            item.id, cell_text);
    }
    else {
        security_cell = String.format(
            '<a href="javascript:void(0)" class="http-soap-security-cell" data-id="{0}" data-href="{1}">{2}</a>',
            item.id, data.security_href,
            has_security ? data.security_name : $.fn.zato.http_soap.inline.config.empty_security_label);
    }

    row += String.format('<td>{0}</td>', security_cell);

    /* 10, 11, 11a */
    if(is_soap) {
        row += soap_action_tr;
        row += soap_version_tr;
        row += String.format("<td class='ignore'>{0}</td>", item.use_mtom == true ? 'True' : 'False');
    }

    /* 12, 13 */
    if(is_channel) {
        row += String.format("<td class='ignore'>{0}</td>", data.service);
    }

    /* 14, 15, 15a, 16 */
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", is_audit_log_active);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);

    if(is_channel) {
    }

    /* 20 */
    row += String.format("<td class='ignore'>{0}</td>", item.data_format);

    /* 22, 23a, 23b, 23c */
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    if(is_outgoing) {
        row += String.format("<td class='ignore'>{0}</td>", item.validate_tls);
    }
    if(is_channel) {
        row += String.format("<td class='ignore'>{0}</td>", item.match_slash);
        row += String.format("<td class='ignore'>{0}</td>", item.http_accept);
    }
    if(is_channel && !is_soap) {
        row += String.format("<td class='ignore'>{0}</td>", item.should_include_in_openapi == true);
        row += String.format("<td class='ignore'>{0}</td>", item.is_deprecated == true);
        row += String.format("<td class='ignore'>{0}</td>", item.deprecation_sunset || '');
        row += String.format("<td class='ignore'>{0}</td>", item.deprecation_successor || '');
    }

    /* 24, 25, 26, 27 */
    if(is_outgoing) {
        row += String.format("<td class='ignore'>{0}</td>", item.ping_method);
        row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
        row += String.format("<td class='ignore'>{0}</td>", item.content_type);
    }

    /* 28, 29, 30, 30a */
    if(is_channel) {
        row += merge_url_params_req_tr;
        row += url_params_pri_tr;
        row += params_pri_tr;
        row += String.format("<td class='ignore'>{0}</td>", item.method || '');
    }

    if(is_channel) {
        row += String.format('<td><a href="/zato/http-soap/rate-limiting/{0}/?cluster={1}">Rate limiting</a></td>', item.id, cluster_id);
        row += String.format('<td style="white-space:nowrap"><a href="/zato/http-soap/response-caching/{0}/?cluster={1}">Cache</a></td>', item.id, cluster_id);
    }

    /* Audit log (REST and SOAP channels, REST outgoing connections) */
    if(is_channel && !is_soap) {
        row += String.format('<td><a href="/zato/audit-log/?source=rest-channel&object_name={0}&cluster={1}">Audit log</a></td>', encodeURIComponent(item.name), cluster_id);
        row += String.format('<td><a href="/zato/channel-usage/?sources=rest-channel&objects={0}&cluster={1}">Usage</a></td>', encodeURIComponent(item.name), cluster_id);
    }

    if(is_channel && is_soap) {
        row += String.format('<td><a href="/zato/audit-log/?source=soap-channel&object_name={0}&cluster={1}">Audit log</a></td>', encodeURIComponent(item.name), cluster_id);
    }

    if(is_outgoing && !is_soap) {
        row += String.format('<td><a href="/zato/audit-log/?source=rest-outgoing&object_name={0}&cluster={1}">Audit log</a></td>', encodeURIComponent(item.name), cluster_id);
        row += String.format('<td><a href="/zato/channel-usage/?sources=rest-outgoing&objects={0}&cluster={1}">Usage</a></td>', encodeURIComponent(item.name), cluster_id);
    }

    /* 31, 32 */
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.delete_('{0}');\">Delete</a>", item.id));

    if(is_outgoing) {
        /* 33 */
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\" class=\"ping-link\">Ping</a>", item.id));
    }

    /* Invoke (REST only) */
    if(!is_soap) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.http_soap.invoke('{0}')\">Invoke</a>", item.id));
    }

    /* 38a */
    row += String.format("<td class='ignore'>{0}</td>", data.data_encoding || data_encoding);

    /* 39 - gateway_service_list for REST channels */
    if(is_channel && !is_soap) {
        row += String.format("<td class='ignore'>{0}</td>", item.gateway_service_list || '');
    }

    /* 40 - declarative invocation and health check fields for REST outgoing connections */
    if(is_outgoing && !is_soap) {

        // After a submit the instance carries the callback widgets rather than the resolved name,
        // so the name is derived from the widget matching the callback type selected.
        if(!item.callback_name && item.callback_type) {
            item.callback_name = item['callback_' + item.callback_type];
        }

        var invocation_fields = [
            'scheduler_run_every', 'scheduler_run_unit', 'scheduler_start_date', 'scheduler_job_id',
            'request_method', 'request_query_string', 'request_path_params', 'request_headers',
            'request_data', 'request_data_mode',
            'response_map', 'response_map_mode',
            'callback_type', 'callback_name',
            'health_check_run_every', 'health_check_run_unit', 'health_check_job_id'
        ];
        $.each(invocation_fields, function(ignored, name) {
            row += String.format("<td class='ignore'>{0}</td>", item[name] ? item[name] : '');
        });

        /* 41 - the Delivery tab - the retries, each count of seconds as a count and a unit, the queue switch and the DLQ config */
        var delivery_fields = [
            'max_retries', 'retry_sleep_time', 'retry_sleep_time_unit', 'retry_backoff_threshold', 'retry_backoff_threshold_unit',
            'retry_backoff_multiplier',
            'use_queue', 'use_dlq', 'dlq_action', 'dlq_retries', 'dlq_retry_interval', 'dlq_retry_interval_unit',
            'dlq_forward_to', 'dlq_keep_header'
        ];
        $.each(delivery_fields, function(ignored, name) {
            row += String.format("<td class='ignore'>{0}</td>", item[name]);
        });
    }

    // 42 - the Alerts tab of REST and SOAP channels and of REST outgoing connections
    if($.fn.zato.http_soap.has_alerts_tab()) {
        row += $.fn.zato.alerts_tab.hidden_cells(item);
    }

    if(include_tr) {
        row += '</tr>';
    }

    return row;

}


// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
