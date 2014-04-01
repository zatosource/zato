
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OpenstackSwiftNotification = new Class({
    toString: function() {
        var s = '<OpenstackSwiftNotification id:{0} name:{1} is_active:{2} is_snet:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)'
                                );
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OpenstackSwiftNotification;
    $.fn.zato.data_table.new_row_func = $.fn.zato.notif.cloud.openstack.swift.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'interval', 'containers', 'def_id', 'service_name']);
})

$.fn.zato.notif.cloud.openstack.swift.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new OpenStack Swift notification definition', null);
}

$.fn.zato.notif.cloud.openstack.swift.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the OpenStack Swift notification definition', id);
}

$.fn.zato.notif.cloud.openstack.swift.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var suppr_cons_slashes = item.suppr_cons_slashes == true;
    var name_pattern_neg = item.name_pattern_neg == true;

    var get_data_patt = item.get_data_patt ? item.get_data_patt : "";
    var get_data = item.get_data ? item.get_data : false;

    var name_pattern_neg = item.name_pattern_neg ? item.name_pattern_neg : false;
    var get_data_patt_neg = item.get_data_patt_neg ? item.get_data_patt_neg : false;

    var name_pattern = "<span class='form_hint'>(None)</span>";
    if(item.name_pattern) {
        name_pattern = item.name_pattern;
    }

    var containers_html = "";
    var containers = "";
    if(item.containers) {
        containers_html = item.containers;
        containers = item.containers;
    }

    console.log(item);

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', data.def_name);
    row += String.format('<td>{0}</td>', item.interval);
    row += String.format('<td>{0}</td>', name_pattern);
    row += String.format('<td>{0}</td>', name_pattern_neg ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', containers_html);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.notif.cloud.openstack.swift.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.notif.cloud.openstack.swift.delete_({0});'>Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.def_id);

    row += String.format("<td class='ignore'>{0}</td>", name_pattern_neg);
    row += String.format("<td class='ignore'>{0}</td>", item.containers);

    row += String.format("<td class='ignore'>{0}</td>", get_data);
    row += String.format("<td class='ignore'>{0}</td>", get_data_patt);
    row += String.format("<td class='ignore'>{0}</td>", get_data_patt_neg);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.notif.cloud.openstack.swift.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'OpenStack Swift notification definition [{0}] deleted',
        'Are you sure you want to delete the OpenStack Swift notification definition [{0}]?',
        true);
}
