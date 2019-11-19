
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OpenStackSwift = new Class({
    toString: function() {
        var s = '<OpenStackSwift id:{0} name:{1} is_active:{2} is_snet:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)',
                                this.is_snet ? this.is_snet : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OpenStackSwift;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.openstack.swift.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(
        ['name', 'auth_url', 'auth_version', 'key', 'retries', 'starting_backoff', 'max_backoff', 'pool_size']);
})

$.fn.zato.cloud.openstack.swift.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new OpenStack Swift connection', null);
}

$.fn.zato.cloud.openstack.swift.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the OpenStack Swift connection', id);
}

$.fn.zato.cloud.openstack.swift.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var is_snet = item.is_snet == true;
    var should_validate_cert = item.should_validate_cert == true;
    var should_retr_ratelimit = item.should_retr_ratelimit == true;
    var needs_tls_compr = item.needs_tls_compr == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.auth_version);
    row += String.format('<td>{0}</td>', item.auth_url);
    row += String.format('<td>{0}</td>', item.user);
    row += String.format('<td>{0}</td>', item.tenant_name);
    row += String.format('<td>{0}</td>', item.pool_size);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.openstack.swift.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cloud.openstack.swift.delete_({0});'>Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.key);
    row += String.format("<td class='ignore'>{0}</td>", item.retries);
    row += String.format("<td class='ignore'>{0}</td>", is_snet);
    row += String.format("<td class='ignore'>{0}</td>", item.starting_backoff);
    row += String.format("<td class='ignore'>{0}</td>", item.max_backoff);
    row += String.format("<td class='ignore'>{0}</td>", should_validate_cert);
    row += String.format("<td class='ignore'>{0}</td>", item.cacert);
    row += String.format("<td class='ignore'>{0}</td>", should_retr_ratelimit);
    row += String.format("<td class='ignore'>{0}</td>", needs_tls_compr);
    row += String.format("<td class='ignore'>{0}</td>", item.custom_options);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.cloud.openstack.swift.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'OpenStack Swift connection [{0}] deleted',
        'Are you sure you want to delete the OpenStack Swift connection [{0}]?',
        true);
}
