
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Group = new Class({
    toString: function() {
        var s = '<Group id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Group;
    $.fn.zato.data_table.new_row_func = $.fn.zato.groups.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
    ]);
    var unique_constraints = [
        {field: 'name', entity_type: 'groups', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(constraint_idx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
    });

    $.fn.zato.data_table.before_submit_hook = function(form) {
        var action = form.attr('id').replace('-form', '');
        $.fn.zato.badge_picker.inject_hidden_inputs(action, $.fn.zato.groups.badge_picker_config);
        return true;
    };
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Groups-specific badge picker configuration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-security-type': item.sec_type, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-type', 'data-security-type': item.sec_type, 'text': item.sec_type_name || item.sec_type }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        var type_order = { 'basic_auth': 0, 'apikey': 1, 'ntlm': 2, 'bearer_token': 3 };
        var order_a = type_order[a.sec_type] !== undefined ? type_order[a.sec_type] : 99;
        var order_b = type_order[b.sec_type] !== undefined ? type_order[b.sec_type] : 99;
        if (order_a !== order_b) return order_a - order_b;
        return (a.name || '').localeCompare(b.name || '');
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var security_type = badge.data('security-type') || '';

        var type_match = !type_val || security_type === type_val;
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return type_match && text_match;
    },

    inject_hidden_input: function(form, badge) {
        var security_type = badge.data('security-type');
        var security_id = badge.data('id');
        var member_key = security_type + '-' + security_id;
        form.append($('<input/>', {
            type: 'hidden',
            name: 'security_group_member_' + member_key,
            value: member_key,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.load = function(action, group_id) {
    var url = '/zato/groups/get-security-list/?group_type=zato-api-creds';
    if (group_id) {
        url += '&group_id=' + group_id;
    }

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    console.log('[badge_picker] load: loading security list for action=' + action);

    $.fn.zato.post(url, function(data, status) {
        if (status === 'success') {
            var items = $.parseJSON(data.responseText);
            console.log('[badge_picker] load: loaded ' + (items ? items.length : 0) + ' items for action=' + action);
            $.fn.zato.badge_picker.init(action, items || [], $.fn.zato.groups.badge_picker_config);

            console.log('[badge_picker] load: re-starting SSE after badge load for action=' + action);
            $.fn.zato.live_form_updates.start(action);
        } else {
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    }, '', '', true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Create / Edit actions
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.create = function() {
    $.fn.zato.groups.badge_picker.load('create', null);
    $.fn.zato.data_table._create_edit('create', 'Create a security group', null);
    $('#create-div').dialog('option', 'width', '45em');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.groups.badge_picker.load('edit', instance.id);
    $.fn.zato.data_table._create_edit('edit', 'Edit the security group', id);
    $('#edit-div').dialog('option', 'width', '45em');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    var member_count = data.member_count !== undefined ? data.member_count : ($("#group_member_count_"+item.id).text() || 0);
    row += String.format('<td id="group_member_count_{0}" class="text-center">{1}</td>', item.id, member_count);

    // 2
    if(false) {
        row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.groups.clone('{0}')\">Clone</a>", item.id));
    }
    else {
        row += String.format('<td></td>');
    }
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.groups.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.groups.delete_('{0}');\">Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 3
    row += String.format("<td class='ignore'>{0}</td>", item.group_type);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Deleted group `{0}`',
        'Are you sure you want to delete group `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {
        object_type: 'security_basic',
        handler: 'badge_picker'
    }
]);

$.fn.zato.live_form_updates.register('edit', [
    {
        object_type: 'security_basic',
        handler: 'badge_picker'
    }
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
