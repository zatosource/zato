
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.OpenAPIChannel = new Class({
    toString: function() {
        var s = '<OpenAPIChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.OpenAPIChannel;
    $.fn.zato.data_table.new_row_func = $.fn.zato.channel.openapi.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
    ]);

    $('#create-div').dialog('option', 'open', function() {
        $.fn.zato.channel.openapi.loadRestChannels('rest-channels-div');
    });

    $('#edit-div').dialog('option', 'open', function() {
        $.fn.zato.channel.openapi.loadRestChannels('id_edit-rest-channels-div');
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new OpenAPI channel', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the OpenAPI channel', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.channel.openapi.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.channel.openapi.delete_({0});'>Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'OpenAPI channel `{0}` deleted',
        'Are you sure you want to delete OpenAPI channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.loadRestChannels = function(containerId) {
    var cluster_id = $('#cluster_id').val();

    $.ajax({
        url: '/zato/pubsub/subscription/get-rest-channels/',
        type: 'GET',
        data: {
            cluster_id: cluster_id
        },
        success: function(response) {
            if (response.rest_channels && response.rest_channels.length > 0) {
                var items = [];
                for (var i = 0; i < response.rest_channels.length; i++) {
                    var channel = response.rest_channels[i];
                    items.push({
                        id: channel.id,
                        state: $.fn.zato.multi_checkbox.State.Off,
                        link: '/zato/http-soap/?cluster=' + cluster_id + '&connection=channel&transport=plain_http&query=' + encodeURIComponent(channel.name),
                        linkText: channel.name,
                        description: channel.url_path
                    });
                }

                $.fn.zato.multi_checkbox.render({
                    containerId: containerId,
                    items: items,
                    inputName: 'rest_channel_id',
                    emptyMessage: 'No REST channels available'
                });
            } else {
                $('#' + containerId).html(
                    '<table class="multi-select-table"><tr><td colspan="2">' +
                    '<span class="multi-select-message">No REST channels available</span>' +
                    '</td></tr></table>'
                );
            }
        },
        error: function(xhr, status, error) {
            console.log('loadRestChannels error:', status, error);
            $('#' + containerId).html(
                '<table class="multi-select-table"><tr><td colspan="2">' +
                '<span class="multi-select-message">Error loading REST channels</span>' +
                '</td></tr></table>'
            );
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
