
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
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // Inject assigned badge IDs as hidden inputs before form submit
    $.fn.zato.data_table.before_submit_hook = function(form) {
        var action = form.attr('id').replace('-form', '');
        $.fn.zato.groups.badge_picker.inject_hidden_inputs(action);
        return true;
    };
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Badge Picker
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker = {};

$.fn.zato.groups.badge_picker.init = function(action, data) {
    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    var assigned_body = $('#badge-zone-assigned-' + action + ' .badge-zone-body');

    available_body.empty();
    assigned_body.empty();

    // Sort order for security types
    var type_order = { 'basic_auth': 0, 'apikey': 1, 'ntlm': 2, 'oauth': 3 };
    var sort_fn = function(a, b) {
        var oa = type_order[a.sec_type] !== undefined ? type_order[a.sec_type] : 99;
        var ob = type_order[b.sec_type] !== undefined ? type_order[b.sec_type] : 99;
        if (oa !== ob) return oa - ob;
        return (a.name || '').localeCompare(b.name || '');
    };

    // Global numbering counter
    var num = 1;

    // Separate into assigned and available
    var assigned_items = [];
    var available_items = [];

    for (var i = 0; i < data.length; i++) {
        if (data[i].is_member) {
            assigned_items.push(data[i]);
        } else {
            available_items.push(data[i]);
        }
    }

    assigned_items.sort(sort_fn);
    available_items.sort(sort_fn);

    // Render assigned first (they get lower numbers)
    for (var i = 0; i < assigned_items.length; i++) {
        assigned_body.append($.fn.zato.groups.badge_picker._make_badge(assigned_items[i], num++));
    }
    for (var i = 0; i < available_items.length; i++) {
        available_body.append($.fn.zato.groups.badge_picker._make_badge(available_items[i], num++));
    }

    $.fn.zato.groups.badge_picker.update_counts(action);
    $.fn.zato.groups.badge_picker.attach_events(action);
    $.fn.zato.groups.badge_picker.attach_resizer(action);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker._make_badge = function(item, num) {
    var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-security-type': item.sec_type, 'data-name': (item.name || '').toLowerCase() });
    badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
    badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
    badge.append($('<span/>', { 'class': 'security-badge-type', 'data-security-type': item.sec_type, 'text': item.sec_type_name || item.sec_type }));
    badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
    return badge;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.renumber = function(action) {
    var num;

    num = 1;
    $('#badge-zone-available-' + action + ' .badge-zone-body .security-badge:visible').each(function() {
        $(this).find('.security-badge-number').text(num + '.');
        num++;
    });

    num = 1;
    $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge:visible').each(function() {
        $(this).find('.security-badge-number').text(num + '.');
        num++;
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.update_counts = function(action) {
    var available_count = $('#badge-zone-available-' + action + ' .badge-zone-body .security-badge:visible').length;
    var assigned_count = $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge').length;
    $('#badge-zone-available-' + action + ' .badge-zone-count').text(available_count);
    $('#badge-zone-assigned-' + action + ' .badge-zone-count').text(assigned_count);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.attach_events = function(action) {
    var picker = $('#badge-picker-' + action);
    var available_body = picker.find('#badge-zone-available-' + action + ' .badge-zone-body');
    var assigned_body = picker.find('#badge-zone-assigned-' + action + ' .badge-zone-body');

    // Click to move (single badge) or Ctrl+click to select
    picker.off('click.badge', '.security-badge').on('click.badge', '.security-badge', function(e) {
        if (e.ctrlKey || e.metaKey) {
            $(this).toggleClass('selected');
            return;
        }

        var badge = $(this);
        var parent_zone = badge.closest('.badge-zone');
        var target_zone;

        if (parent_zone.attr('id').indexOf('available') !== -1) {
            target_zone = assigned_body;
        } else {
            target_zone = available_body;
        }

        // If multi-selection exists in same zone, move all selected
        var selected = parent_zone.find('.security-badge.selected');
        if (selected.length > 0 && badge.hasClass('selected')) {
            selected.removeClass('selected').appendTo(target_zone);
        } else {
            picker.find('.security-badge.selected').removeClass('selected');
            badge.appendTo(target_zone);
        }

        $.fn.zato.groups.badge_picker.update_counts(action);
        $.fn.zato.groups.badge_picker.renumber(action);
    });

    // Marquee (rectangle select) and Drag share a unified mousedown
    var marquee_state = {};
    var drag_state = {};

    picker.find('.badge-zone-body').off('mousedown.unified').on('mousedown.unified', function(e) {
        if (e.ctrlKey || e.metaKey) {
            if ($(e.target).closest('.security-badge').length) {
                return; // Ctrl+click handled by click handler
            }
        }

        var zone_body = $(this);
        var badge = $(e.target).closest('.security-badge');
        var offset = zone_body.offset();
        var scroll_top = zone_body.scrollTop();
        var scroll_left = zone_body.scrollLeft();

        marquee_state.pending = true;
        marquee_state.active = false;
        marquee_state.zone_body = zone_body;
        marquee_state.start_x = e.pageX - offset.left + scroll_left;
        marquee_state.start_y = e.pageY - offset.top + scroll_top;
        marquee_state.page_x = e.pageX;
        marquee_state.page_y = e.pageY;
        marquee_state.badge = badge.length ? badge : null;

        drag_state.active = false;
        drag_state.dragging = false;

        if (badge.length) {
            drag_state.badge = badge;
            drag_state.source_zone = badge.closest('.badge-zone');
            drag_state.start_x = e.pageX;
            drag_state.start_y = e.pageY;
        }

        e.preventDefault();
    });

    $(document).off('mousemove.unified_' + action).on('mousemove.unified_' + action, function(e) {
        // Pending state: decide whether this is a marquee or a drag
        if (marquee_state.pending && !marquee_state.active && !drag_state.active) {
            var dx = Math.abs(e.pageX - marquee_state.page_x);
            var dy = Math.abs(e.pageY - marquee_state.page_y);

            if (dx > 5 || dy > 5) {
                // If started on a badge and moving mostly horizontal, it's a drag
                if (marquee_state.badge && dx > dy * 1.5) {
                    drag_state.active = true;
                    marquee_state.pending = false;
                } else {
                    // It's a marquee
                    marquee_state.active = true;
                    marquee_state.pending = false;

                    var zone_body = marquee_state.zone_body;
                    var marquee = $('<div class="badge-marquee"></div>');
                    zone_body.append(marquee);
                    marquee_state.marquee = marquee;

                    if (!e.ctrlKey && !e.metaKey) {
                        zone_body.find('.security-badge.selected').removeClass('selected');
                    }
                }
            }
        }

        // Marquee movement
        if (marquee_state.active) {
            var zone_body = marquee_state.zone_body;
            var offset = zone_body.offset();
            var scroll_top = zone_body.scrollTop();
            var scroll_left = zone_body.scrollLeft();

            var cur_x = e.pageX - offset.left + scroll_left;
            var cur_y = e.pageY - offset.top + scroll_top;

            var x = Math.min(marquee_state.start_x, cur_x);
            var y = Math.min(marquee_state.start_y, cur_y);
            var w = Math.abs(cur_x - marquee_state.start_x);
            var h = Math.abs(cur_y - marquee_state.start_y);

            marquee_state.marquee.css({ left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px' });

            var marquee_rect = { left: x, top: y, right: x + w, bottom: y + h };

            zone_body.find('.security-badge:visible').each(function() {
                var badge = $(this);
                var pos = badge.position();
                var badge_rect = { left: pos.left, top: pos.top, right: pos.left + badge.outerWidth(), bottom: pos.top + badge.outerHeight() };

                var intersects = !(badge_rect.right < marquee_rect.left || badge_rect.left > marquee_rect.right ||
                                 badge_rect.bottom < marquee_rect.top || badge_rect.top > marquee_rect.bottom);

                if (intersects) {
                    badge.addClass('selected');
                } else if (!e.ctrlKey && !e.metaKey) {
                    badge.removeClass('selected');
                }
            });
        }

        // Drag movement
        if (drag_state.active) {
            var dx = e.pageX - drag_state.start_x;
            var dy = e.pageY - drag_state.start_y;
            if (!drag_state.dragging && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) {
                drag_state.dragging = true;

                if (!drag_state.badge.hasClass('selected')) {
                    drag_state.source_zone.find('.security-badge.selected').removeClass('selected');
                    drag_state.badge.addClass('selected');
                }

                drag_state.badges = drag_state.source_zone.find('.security-badge.selected');
                drag_state.badges.addClass('dragging');

                var ghost = $('<div class="badge-drag-ghost"></div>');
                var header = $('<div class="badge-drag-ghost-header"></div>');
                header.text(drag_state.badges.length + ' item' + (drag_state.badges.length > 1 ? 's' : ''));
                ghost.append(header);
                drag_state.badges.each(function() {
                    var clone = $(this).clone();
                    clone.removeClass('selected dragging');
                    clone.addClass('badge-drag-ghost-row');
                    ghost.append(clone);
                });
                $('body').append(ghost);
                drag_state.ghost = ghost;
            }

            if (drag_state.dragging && drag_state.ghost) {
                drag_state.ghost.css({ left: e.pageX + 12, top: e.pageY + 12 });

                var target = $.fn.zato.groups.badge_picker._get_drop_target(e, picker, drag_state.source_zone);
                picker.find('.badge-zone').removeClass('drop-target');
                if (target) {
                    target.addClass('drop-target');
                }
            }
        }
    });

    $(document).off('mouseup.unified_' + action).on('mouseup.unified_' + action, function(e) {
        // Handle marquee end
        if (marquee_state.active) {
            marquee_state.active = false;
            if (marquee_state.marquee) {
                marquee_state.marquee.remove();
                marquee_state.marquee = null;
            }
        }

        // Handle drag end
        if (drag_state.active && drag_state.dragging) {
            var target = $.fn.zato.groups.badge_picker._get_drop_target(e, picker, drag_state.source_zone);
            if (target) {
                var target_body = target.find('.badge-zone-body');
                drag_state.badges.removeClass('selected dragging').appendTo(target_body);
                $.fn.zato.groups.badge_picker.update_counts(action);
                $.fn.zato.groups.badge_picker.renumber(action);
            } else {
                drag_state.badges.removeClass('dragging');
            }

            picker.find('.badge-zone').removeClass('drop-target');
            if (drag_state.ghost) {
                drag_state.ghost.remove();
            }
        }

        marquee_state.pending = false;
        marquee_state.active = false;
        drag_state.active = false;
        drag_state.dragging = false;
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.attach_resizer = function(action) {
    var picker = $('#badge-picker-' + action);
    var resizer = picker.find('.badge-picker-resizer');
    var left_zone = picker.find('.badge-zone').first();
    var right_zone = picker.find('.badge-zone').last();

    var state = {};

    resizer.on('mousedown', function(e) {
        state.active = true;
        state.start_x = e.pageX;
        state.left_width = left_zone.outerWidth();
        state.right_width = right_zone.outerWidth();
        resizer.addClass('active');
        e.preventDefault();
    });

    $(document).on('mousemove.resizer_' + action, function(e) {
        if (!state.active) return;
        var dx = e.pageX - state.start_x;
        var new_left = state.left_width + dx;
        var new_right = state.right_width - dx;
        var min_w = 100;

        if (new_left >= min_w && new_right >= min_w) {
            var total = new_left + new_right;
            left_zone.css('flex', '0 0 ' + (new_left / total * 100) + '%');
            right_zone.css('flex', '0 0 ' + (new_right / total * 100) + '%');
        }
    });

    $(document).on('mouseup.resizer_' + action, function() {
        if (!state.active) return;
        state.active = false;
        resizer.removeClass('active');
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker._get_drop_target = function(e, picker, source_zone) {
    var zones = picker.find('.badge-zone');
    var target = null;

    zones.each(function() {
        if ($(this).attr('id') === source_zone.attr('id')) return;
        var offset = $(this).offset();
        var w = $(this).outerWidth();
        var h = $(this).outerHeight();

        if (e.pageX >= offset.left && e.pageX <= offset.left + w &&
            e.pageY >= offset.top && e.pageY <= offset.top + h) {
            target = $(this);
            return false;
        }
    });

    return target;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.get_assigned_ids = function(action) {
    var ids = [];
    $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge').each(function() {
        ids.push($(this).data('id'));
    });
    return ids;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.inject_hidden_inputs = function(action) {
    var form = $('#' + action + '-form');
    form.find('input.badge-member-input').remove();

    var assigned = $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge');
    assigned.each(function() {
        var badge = $(this);
        var security_type = badge.data('security-type');
        var security_id = badge.data('id');
        var member_key = security_type + '-' + security_id;
        form.append($('<input/>', {
            type: 'hidden',
            name: 'security_group_member_' + member_key,
            value: member_key,
            'class': 'badge-member-input'
        }));
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.groups.badge_picker.load = function(action, group_id) {
    var url = '/zato/groups/get-security-list/?group_type=zato-api-creds';
    if (group_id) {
        url += '&group_id=' + group_id;
    }

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    console.log('[live_form_updates] badge_picker.load: loading security list for action=' + action);

    $.fn.zato.post(url, function(data, status) {
        if (status === 'success') {
            var items = $.parseJSON(data.responseText);
            console.log('[live_form_updates] badge_picker.load: loaded ' + (items ? items.length : 0) + ' items for action=' + action);
            $.fn.zato.groups.badge_picker.init(action, items || []);

            // Re-start the SSE connection now that badges are populated
            console.log('[live_form_updates] badge_picker.load: re-starting SSE after badge load for action=' + action);
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
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', $("#group_member_count_"+item.id).text() || 0);

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
    row += String.format("<td class='ignore'>{0}</td>", item.generic_object_id);

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
