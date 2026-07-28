
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.MicrosoftTeamsConnection = new Class({
    toString: function() {
        var s = '<MicrosoftTeamsConnection id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.MicrosoftTeamsConnection;
    $.fn.zato.data_table.new_row_func = $.fn.zato.chat.microsoft_teams.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'tenant_id',
        'client_id',
        'scopes',
    ]);

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'chat-microsoft-teams'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.field_descriptions = {
    'id_name': 'A unique name for this Microsoft Teams connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_tenant_id': 'Directory (tenant) ID of the Microsoft Entra tenant<br>the connection signs in to. Found on the overview page<br>of the app registration in the Azure portal.',
    'id_client_id': 'Application (client) ID of the Azure app registration<br>the connection authenticates as. The app\'s API permissions<br>decide what the connection can access.',
    'id_secret_value': 'Value of a client secret created for the app registration.<br>Note that secrets expire in Azure<br>and need to be rotated periodically.',
    'id_scopes': 'OAuth2 scopes the connection requests, one per line.<br>The default https://graph.microsoft.com/.default<br>grants all permissions assigned to the app in Azure.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Microsoft Teams connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.chat.microsoft_teams.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Microsoft Teams connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.chat.microsoft_teams.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.tenant_id);
    row += String.format('<td>{0}</td>', item.client_id);

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change secret')\">Change secret</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.microsoft_teams.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.microsoft_teams.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.chat.microsoft_teams.send_message('{0}')\">Send message</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore'>{0}</td>", item.scopes);

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Microsoft Teams connection `{0}` deleted',
        'Are you sure you want to delete Microsoft Teams connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.get_send_message_url = function() {
    var out = '/zato/chat/microsoft-teams/send-message/';
    return out;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.send_message = function(id) {
    var item = $.fn.zato.data_table.data[id];

    var historyKey = 'zato.chat.microsoft-teams.send-message.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        title_prefix: 'Send a message',
        action_label: 'Send',
        show_more_options: false,
        history_key: historyKey,
        highlight_lexer: 'html',
        extra_fields_html: '<div class="invoker-more-options-row invoker-more-options-row-compact">'
            + '<label>Send to</label>'
            + '<input type="text" id="invoker-modal-target" placeholder="My Team/General or a chat ID" />'
            + '</div>',
        get_invoke_url_func: $.fn.zato.chat.microsoft_teams.get_send_message_url,
        collect_form_data_func: $.fn.zato.chat.microsoft_teams.collect_form_data(item)
    });

    // Teams messages are sent as HTML, which is how rich content reaches the Graph API ..
    $.fn.zato.invoker._request_ace_mode = 'ace/mode/html';

    // .. and the pane that was just mounted needs to be switched over to it.
    var editor = $.fn.zato.invoker._request_pane.getEditor();
    editor.session.setMode('ace/mode/html');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.microsoft_teams.collect_form_data = function(item) {
    return function() {
        var message = $.fn.zato.invoker._request_pane.getValue();
        var target = $('#invoker-modal-target').val();

        var out = {
            'data-request': message,
            'conn_name': item.name,
            'target': target
        };

        return out;
    };
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
