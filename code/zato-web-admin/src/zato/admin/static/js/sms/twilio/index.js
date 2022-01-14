
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SMSTwilio = new Class({
    toString: function() {
        var s = '<SMSTwilio id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SMSTwilio;
    $.fn.zato.data_table.new_row_func = $.fn.zato.sms.twilio.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'account_sid', 'auth_token']);
})


$.fn.zato.sms.twilio.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new SMS Twilio connection', null);
}

$.fn.zato.sms.twilio.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the SMS Twilio connection', id);
}

$.fn.zato.sms.twilio.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    var default_from = item.default_from ? item.default_from : '<span class="form_hint">(None)</span>';
    var default_to = item.default_to ? item.default_to : '<span class="form_hint">(None)</span>';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', default_from);
    row += String.format('<td>{0}</td>', default_to);
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"/zato/sms/twilio/send/cluster/{0}/conn/{1}\">Send a message</a>", item.cluster_id, item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.sms.twilio.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href='javascript:$.fn.zato.sms.twilio.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.sms.twilio.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'SMS Twilio connection `{0}` deleted',
        'Are you sure you want to delete the SMS Twilio connection `{0}`?',
        true);
}
