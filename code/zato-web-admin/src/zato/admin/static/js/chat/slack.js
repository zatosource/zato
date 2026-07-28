
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SlackConnection = new Class({
    toString: function() {
        var s = '<SlackConnection id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SlackConnection;
    $.fn.zato.data_table.new_row_func = $.fn.zato.chat.slack.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
    ]);

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'chat-slack'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.field_descriptions = {
    'id_name': 'A unique name for this Slack connection.<br>Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_token': 'A bot token of a Slack app installed in the workspace,<br>starting with xoxb-. The app\'s scopes decide<br>what channels and people it can message.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Slack connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.chat.slack.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Slack connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.chat.slack.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.data_table.new_row = function(item, data, include_tr) {
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

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change token')\">Change token</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.slack.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.slack.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.slack.send_message('{0}')\">Send message</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Slack connection `{0}` deleted',
        'Are you sure you want to delete Slack connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.get_send_message_url = function() {
    var out = '/zato/chat/slack/send-message/';
    return out;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.send_message = function(id) {
    var item = $.fn.zato.data_table.data[id];

    var historyKey = 'zato.chat.slack.send-message.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        title_prefix: 'Send a message',
        action_label: 'Send',
        show_more_options: false,
        history_key: historyKey,
        highlight_lexer: 'markdown',
        extra_fields_html: '<div class="invoker-more-options-row invoker-more-options-row-compact">'
            + '<label>Send to</label>'
            + '<input type="text" id="invoker-modal-target" placeholder="#general, @user or C0123456789" />'
            + '</div>',
        get_invoke_url_func: $.fn.zato.chat.slack.get_send_message_url,
        collect_form_data_func: $.fn.zato.chat.slack.collect_form_data(item)
    });

    // Slack messages are written in mrkdwn, which Markdown highlighting renders closely enough ..
    $.fn.zato.invoker._request_ace_mode = 'ace/mode/markdown';

    // .. and the pane that was just mounted needs to be switched over to it.
    var editor = $.fn.zato.invoker._request_pane.getEditor();
    editor.session.setMode('ace/mode/markdown');
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.slack.collect_form_data = function(item) {
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
