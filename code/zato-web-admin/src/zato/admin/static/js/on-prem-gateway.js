
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OnPremGateway = new Class({
    toString: function() {
        var s = '<OnPremGateway id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.status = {
    notEnrolled: 'Not enrolled'
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OnPremGateway;
    $.fn.zato.data_table.new_row_func = $.fn.zato.on_prem_gateway.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name']);

    $('#enrollment_token-div').dialog({
        autoOpen: false,
        width: '40em'
    });

    $('#enrollment-token-close').on('click', function() {
        $('#enrollment_token-div').dialog('close');
    });

    var uniqueConstraints = [
        {field: 'name', entity_type: 'on_prem_gateway', attr_name: 'name'}
    ];

    $.each(uniqueConstraints, function(constraintIndex, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new on-premises gateway', null);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the on-premises gateway', id);
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var isActive = item.is_active == true;

    // Only the hub knows how many of the addresses are in use and what the gateway is doing,
    // so a row rebuilt here shows what the configuration alone says.
    var hostCount = item.hosts ? item.hosts.split('\n').length : 0;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', $.fn.zato.on_prem_gateway.status.notEnrolled);
    row += String.format('<td>{0}</td>', hostCount);
    row += '<td></td>';
    row += '<td></td>';
    row += '<td></td>';

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.enrollment_token('{0}')\">Enrollment token</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.reset_key('{0}')\">Reset key</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.on_prem_gateway.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.hosts);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.enrollment_token = function(id) {

    var url = String.format('./enrollment-token/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));

    var callback = function(data, status) {

        if(status != 'success') {
            $.fn.zato.user_message(false, data.responseText);
            return;
        }

        // The token is minted once and never stored, so the popup is the only place it is shown ..
        var response = $.parseJSON(data.responseText);

        $('#enrollment-token-name').text(response.name);
        $('#enrollment-token-value').val(response.token);

        // .. and the popup's own title says which gateway it belongs to.
        var div = $('#enrollment_token-div');
        var title = 'Enrollment token, valid until ' + response.expires_at;

        div.prev().html('<span class="ui-dialog-title-text">' + title + '</span>');
        div.dialog('open');
    }

    $.fn.zato.post(url, callback, {});
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.reset_key = function(id) {

    var instance = $.fn.zato.data_table.data[id];
    var question = String.format('Are you sure you want to reset the key of the on-premises gateway `{0}`?', instance.name);

    var callback = function(data, status) {

        if(status != 'success') {
            $.fn.zato.user_message(false, data.responseText);
            return;
        }

        // The gateway has to enroll again, which is what its Status column now says.
        var response = $.parseJSON(data.responseText);
        var statusCell = $.fn.zato.data_table.get_cell(id, '_status');

        statusCell.text($.fn.zato.on_prem_gateway.status.notEnrolled);

        $.fn.zato.data_table.row_updated(id);
        $.fn.zato.user_message(true, response.message);
    }

    jConfirm(question, 'Please confirm', function(isConfirmed) {

        if(!isConfirmed) {
            return;
        }

        var url = String.format('./reset-key/{0}/cluster/{1}/', id, $(document).getUrlParam('cluster'));
        $.fn.zato.post(url, callback, {});
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.on_prem_gateway.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'On-premises gateway `{0}` deleted',
        'Are you sure you want to delete the on-premises gateway `{0}`?',
        true);
}
