
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
        $.fn.zato.channel.openapi.updateSlug('id_name', 'id_url_path', 'id_url_path_display');
    });

    $('#edit-div').dialog('option', 'open', function() {
        var id = $('#id_edit-id').val();
        $.fn.zato.channel.openapi.loadRestChannelsForEdit('id_edit-rest-channels-div', id);
        $.fn.zato.channel.openapi.updateSlug('id_edit-name', 'id_edit-url_path', 'id_edit-url_path_display');
    });

    $('#id_name').on('input', function() {
        $.fn.zato.channel.openapi.updateSlug('id_name', 'id_url_path', 'id_url_path_display');
    });

    $('#id_edit-name').on('input', function() {
        $.fn.zato.channel.openapi.updateSlug('id_edit-name', 'id_edit-url_path', 'id_edit-url_path_display');
    });

    var originalOnSubmit = $.fn.zato.data_table.on_submit;
    $.fn.zato.data_table.on_submit = function(action) {
        var containerId = action === 'create' ? '#rest-channels-div' : '#id_edit-rest-channels-div';
        var $form = $(containerId).closest('form');

        $form.find('input[name="rest_channel_list"]').remove();

        $(containerId + ' input[name="rest_channel_id"]:checked:not(.disabled)').each(function() {
            var $checkbox = $(this);
            var channelId = $checkbox.val();
            var dataObj = {id: channelId, state: 'on'};
            var dataStr = JSON.stringify(dataObj).replace(/"/g, '&quot;');
            $form.append('<input type="hidden" name="rest_channel_list" value="' + dataStr + '">');
        });

        $(containerId + ' input[name="rest_channel_id"].disabled').each(function() {
            var $checkbox = $(this);
            var channelId = $checkbox.val();
            var dataObj = {id: channelId, state: 'disabled'};
            var dataStr = JSON.stringify(dataObj).replace(/"/g, '&quot;');
            $form.append('<input type="hidden" name="rest_channel_list" value="' + dataStr + '">');
        });

        return originalOnSubmit.call(this, action);
    };
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
    row += String.format("<td class='ignore'>{0}</td>", item.rest_channel_list || '[]');

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

$.fn.zato.channel.openapi.slugify = function(text) {
    var result = '';
    for (var i = 0; i < text.length; i++) {
        var char = text[i];
        if (char === '/') {
            result += '/';
        } else if (/[0-9]/.test(char)) {
            result += char;
        } else if (/[a-zA-Z]/.test(char)) {
            result += char.toLowerCase();
        } else if (char === ' ' || char === '-' || char === '_') {
            if (result.length > 0 && result[result.length - 1] !== '-' && result[result.length - 1] !== '/') {
                result += '-';
            }
        }
    }
    if (result.length > 0 && result[result.length - 1] === '-') {
        result = result.slice(0, -1);
    }
    return result;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.updateSlug = function(nameInputId, hiddenInputId, displayId) {
    var name = $('#' + nameInputId).val() || '';
    var slug = $.fn.zato.channel.openapi.slugify(name);
    var prefix = $('#' + displayId).data('prefix') || $('#' + displayId).text().split('/').filter(Boolean).map(function(p) { return '/' + p; }).join('') + '/';
    if (!$('#' + displayId).data('prefix')) {
        $('#' + displayId).data('prefix', prefix);
    }
    var urlPath = prefix + slug;
    $('#' + hiddenInputId).val(urlPath);
    $('#' + displayId).text(urlPath);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.openapi.loadRestChannels = function(containerId, channelStates) {
    var cluster_id = $('#cluster_id').val();
    channelStates = channelStates || {};
    console.log('[openapi.js] loadRestChannels called with containerId:', containerId, 'channelStates:', JSON.stringify(channelStates));

    $.ajax({
        url: '/zato/channel/openapi/get-rest-channels/',
        type: 'GET',
        data: {
            cluster_id: cluster_id
        },
        success: function(response) {
            console.log('[openapi.js] loadRestChannels got response:', JSON.stringify(response));
            if (response.rest_channels && response.rest_channels.length > 0) {
                var items = [];
                for (var i = 0; i < response.rest_channels.length; i++) {
                    var channel = response.rest_channels[i];
                    var savedState = channelStates[String(channel.id)];
                    var state = $.fn.zato.multi_checkbox.State.Off;
                    if (savedState === 'on') {
                        state = $.fn.zato.multi_checkbox.State.On;
                    } else if (savedState === 'disabled') {
                        state = $.fn.zato.multi_checkbox.State.Disabled;
                    }
                    console.log('[openapi.js] channel.id:', channel.id, 'savedState:', savedState, 'state:', state);
                    items.push({
                        id: channel.id,
                        state: state,
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

$.fn.zato.channel.openapi.loadRestChannelsForEdit = function(containerId, channelId) {
    console.log('[openapi.js] loadRestChannelsForEdit called with containerId:', containerId, 'channelId:', channelId);
    var instance = $.fn.zato.data_table.data[channelId];
    console.log('[openapi.js] instance from data_table:', JSON.stringify(instance));
    var channelStates = {};

    if (instance && instance.rest_channel_list) {
        var raw = instance.rest_channel_list;
        console.log('[openapi.js] raw rest_channel_list:', raw);
        var channelList = [];
        if (typeof raw === 'string' && raw.length > 0) {
            var parsed = JSON.parse(raw);
            channelList = Array.isArray(parsed) ? parsed : [parsed];
        } else if (Array.isArray(raw)) {
            channelList = raw;
        } else if (typeof raw === 'object') {
            channelList = [raw];
        }
        for (var i = 0; i < channelList.length; i++) {
            var item = channelList[i];
            channelStates[String(item.id)] = item.state;
        }
        console.log('[openapi.js] parsed channelStates:', JSON.stringify(channelStates));
    }
    $.fn.zato.channel.openapi.loadRestChannels(containerId, channelStates);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
