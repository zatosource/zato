
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DiscordConnection = new Class({
    toString: function() {
        var s = '<DiscordConnection id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.DiscordConnection;
    $.fn.zato.data_table.new_row_func = $.fn.zato.chat.discord.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'ready_timeout',
        'timeout',
    ]);

    // The token is set on creation only, the edit form changes it through its own dialog.
    $.fn.zato.data_table.set_field_required('#id_token');

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'chat-discord'}
    ];
    $.each(uniqueConstraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.discord.field_descriptions = {
    'id_name': 'A unique name for this Discord connection. ' +
        'Used to identify it in services, logs and the dashboard.',
    'id_is_active': 'Whether this connection can be used. Services cannot look up an inactive connection.',
    'id_token': 'The token of a Discord bot added to the server. ' +
        'The bot\'s channel permissions decide where it can post messages.',
    'id_default_channel_id': 'The ID of the channel that messages go to when a service names no channel.',
    'id_address': 'The base address of the Discord REST API.',
    'id_ready_timeout': 'How many seconds a service waits for the connection to complete its gateway handshake.',
    'id_timeout': 'How many seconds each request to Discord can take.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.discord.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Discord connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.chat.discord.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.discord.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Discord connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.chat.discord.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.discord.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let isActive = item.is_active == true;

    let defaultChannelId = item.default_channel_id;
    if(defaultChannelId === null) {
        defaultChannelId = '';
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', defaultChannelId);

    // 2
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change token')\">Change token</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.discord.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.chat.discord.delete_('{0}');\">Delete</a>", item.id));

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.address);
    row += String.format("<td class='ignore'>{0}</td>", item.ready_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.chat.discord.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Discord connection `{0}` deleted',
        'Are you sure you want to delete Discord connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
