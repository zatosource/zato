
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7RESTChannel = new Class({
    toString: function() {
        var s = '<HL7RESTChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7RESTChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.hl7.rest.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path', 'service', 'security_id', 'hl7_version']);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.rest.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new HL7 REST channel', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.rest.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the HL7 REST channel', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.rest.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.hl7_version);

    // 2
    row += String.format('<td>{0}</td>', item.url_path);
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(item.service, cluster_id));
    row += String.format('<td>{0}</td>', data.sec_def_link || $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.hl7.rest.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.hl7.rest.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.service);
    row += String.format("<td class='ignore'>{0}</td>", item.security);

    // 5
    row += String.format("<td class='ignore'>{0}</td>", item.json_path);
    row += String.format("<td class='ignore'>{0}</td>", item.should_parse_on_input);
    row += String.format("<td class='ignore'>{0}</td>", item.should_validate);

    // 6
    row += String.format("<td class='ignore'>{0}</td>", item.data_encoding);
    row += String.format("<td class='ignore'>{0}</td>", item.should_return_errors);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.rest.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 REST channel `{0}` deleted',
        'Are you sure you want to delete HL7 REST channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
