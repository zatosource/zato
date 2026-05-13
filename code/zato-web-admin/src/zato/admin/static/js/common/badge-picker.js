
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Reusable badge picker component.
// Two-zone drag-and-drop UI for moving items between "Available" and "Assigned" lists.
// Used by security groups (with sec_type badges) and MCP channels (with service name badges).
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Configuration defaults. Callers override these per-instance via the config argument.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker._default_config = {

    // Build a single badge DOM element from an item. Override to change badge layout.
    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    // Sort function for items. Override for type-aware sorting.
    sort_items: function(a, b) {
        return (a.name || '').localeCompare(b.name || '');
    },

    // Determine whether an item belongs in the "assigned" zone.
    is_assigned: function(item) {
        return item.is_member;
    },

    // Filter function called on each badge in the available zone.
    // Returns true if the badge should be visible given the current filter values.
    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return text_match;
    },

    // Build hidden inputs from assigned badges when the form is submitted.
    inject_hidden_input: function(form, badge) {
        var badge_id = badge.data('id');
        form.append($('<input/>', {
            type: 'hidden',
            name: 'badge_item_' + badge_id,
            value: badge_id,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.init = function(action, data, config) {
    config = $.extend({}, $.fn.zato.badge_picker._default_config, config);

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    var assigned_body = $('#badge-zone-assigned-' + action + ' .badge-zone-body');

    available_body.empty();
    assigned_body.empty();

    var assigned_items = [];
    var available_items = [];

    for (var item_idx = 0; item_idx < data.length; item_idx++) {
        if (config.is_assigned(data[item_idx])) {
            assigned_items.push(data[item_idx]);
        } else {
            available_items.push(data[item_idx]);
        }
    }

    assigned_items.sort(config.sort_items);
    available_items.sort(config.sort_items);

    var num = 1;

    for (var assigned_idx = 0; assigned_idx < assigned_items.length; assigned_idx++) {
        assigned_body.append(config.make_badge(assigned_items[assigned_idx], num++));
    }
    for (var available_idx = 0; available_idx < available_items.length; available_idx++) {
        available_body.append(config.make_badge(available_items[available_idx], num++));
    }

    $.fn.zato.badge_picker.update_counts(action);
    $.fn.zato.badge_picker.attach_events(action, config);
    $.fn.zato.badge_picker.attach_resizer(action);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.renumber = function(action) {
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

$.fn.zato.badge_picker.update_counts = function(action) {
    var available_count = $('#badge-zone-available-' + action + ' .badge-zone-body .security-badge:visible').length;
    var assigned_count = $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge').length;
    $('#badge-zone-available-' + action + ' .badge-zone-count').text(available_count);
    $('#badge-zone-assigned-' + action + ' .badge-zone-count').text(assigned_count);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.attach_events = function(action, config) {
    var picker = $('#badge-picker-' + action);
    var available_body = picker.find('#badge-zone-available-' + action + ' .badge-zone-body');
    var assigned_body = picker.find('#badge-zone-assigned-' + action + ' .badge-zone-body');

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

        var selected = parent_zone.find('.security-badge.selected');
        if (selected.length > 0 && badge.hasClass('selected')) {
            selected.removeClass('selected').appendTo(target_zone);
        } else {
            picker.find('.security-badge.selected').removeClass('selected');
            badge.appendTo(target_zone);
        }

        $.fn.zato.badge_picker.update_counts(action);
        $.fn.zato.badge_picker.apply_filter(action, config);
        $.fn.zato.badge_picker.renumber(action);
    });

    var marquee_state = {};
    var drag_state = {};

    picker.find('.badge-zone-body').off('mousedown.unified').on('mousedown.unified', function(e) {
        if (e.ctrlKey || e.metaKey) {
            if ($(e.target).closest('.security-badge').length) {
                return;
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
        if (marquee_state.pending && !marquee_state.active && !drag_state.active) {
            var dx = Math.abs(e.pageX - marquee_state.page_x);
            var dy = Math.abs(e.pageY - marquee_state.page_y);

            if (dx > 5 || dy > 5) {
                if (marquee_state.badge) {
                    drag_state.active = true;
                    marquee_state.pending = false;
                } else {
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

        if (marquee_state.active) {
            var zone_body = marquee_state.zone_body;
            var offset = zone_body.offset();
            var scroll_top = zone_body.scrollTop();
            var scroll_left = zone_body.scrollLeft();

            var cur_x = e.pageX - offset.left + scroll_left;
            var cur_y = e.pageY - offset.top + scroll_top;

            var rect_x = Math.min(marquee_state.start_x, cur_x);
            var rect_y = Math.min(marquee_state.start_y, cur_y);
            var rect_w = Math.abs(cur_x - marquee_state.start_x);
            var rect_h = Math.abs(cur_y - marquee_state.start_y);

            marquee_state.marquee.css({ left: rect_x + 'px', top: rect_y + 'px', width: rect_w + 'px', height: rect_h + 'px' });

            var marquee_rect = { left: rect_x, top: rect_y, right: rect_x + rect_w, bottom: rect_y + rect_h };

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
                drag_state.ghost.css({ left: e.clientX + 12, top: e.clientY + 12 });

                var target = $.fn.zato.badge_picker._get_drop_target(e, picker, drag_state.source_zone);
                picker.find('.badge-zone').removeClass('drop-target');
                if (target) {
                    target.addClass('drop-target');
                }
            }
        }
    });

    $(document).off('mouseup.unified_' + action).on('mouseup.unified_' + action, function(e) {
        if (marquee_state.active) {
            marquee_state.active = false;
            if (marquee_state.marquee) {
                marquee_state.marquee.remove();
                marquee_state.marquee = null;
            }
        }

        if (drag_state.active && drag_state.dragging) {
            var target = $.fn.zato.badge_picker._get_drop_target(e, picker, drag_state.source_zone);
            if (target) {
                var target_body = target.find('.badge-zone-body');
                drag_state.badges.removeClass('selected dragging').appendTo(target_body);
                $.fn.zato.badge_picker.update_counts(action);
                $.fn.zato.badge_picker.apply_filter(action, config);
                $.fn.zato.badge_picker.renumber(action);
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

    var debounce_timer;
    $('#badge-filter-text-' + action).off('input').on('input', function() {
        clearTimeout(debounce_timer);
        debounce_timer = setTimeout(function() {
            $.fn.zato.badge_picker.apply_filter(action, config);
            $.fn.zato.badge_picker.renumber(action);
        }, 150);
    });

    $('#badge-security-type-' + action).off('change').on('change', function() {
        $.fn.zato.badge_picker.apply_filter(action, config);
        $.fn.zato.badge_picker.renumber(action);
    });

    $('#badge-filter-clear-' + action).off('click').on('click', function() {
        $('#badge-filter-text-' + action).val('');
        $('#badge-security-type-' + action).val('');
        $.fn.zato.badge_picker.apply_filter(action, config);
        $.fn.zato.badge_picker.renumber(action);
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.attach_resizer = function(action) {
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

$.fn.zato.badge_picker._get_drop_target = function(e, picker, source_zone) {
    var zones = picker.find('.badge-zone');
    var target = null;

    zones.each(function() {
        if ($(this).attr('id') === source_zone.attr('id')) return;
        var offset = $(this).offset();
        var zone_width = $(this).outerWidth();
        var zone_height = $(this).outerHeight();

        if (e.pageX >= offset.left && e.pageX <= offset.left + zone_width &&
            e.pageY >= offset.top && e.pageY <= offset.top + zone_height) {
            target = $(this);
            return false;
        }
    });

    return target;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.apply_filter = function(action, config) {
    config = config || $.fn.zato.badge_picker._default_config;

    var text_val = ($('#badge-filter-text-' + action).val() || '').toLowerCase().trim();
    var type_val = $('#badge-security-type-' + action).val() || '';
    var words = text_val ? text_val.split(/\s+/) : [];

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');

    available_body.find('.security-badge').each(function() {
        var badge = $(this);

        if (config.filter_badge(badge, words, type_val)) {
            badge.show();
        } else {
            badge.hide();
        }
    });

    $.fn.zato.badge_picker.update_counts(action);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.get_assigned_ids = function(action) {
    var ids = [];
    $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge').each(function() {
        ids.push($(this).data('id'));
    });
    return ids;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.get_assigned_names = function(action) {
    var names = [];
    $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge').each(function() {
        names.push($(this).data('name'));
    });
    return names;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.badge_picker.inject_hidden_inputs = function(action, config) {
    config = config || $.fn.zato.badge_picker._default_config;

    var form = $('#' + action + '-form');
    form.find('input.badge-member-input').remove();

    var assigned = $('#badge-zone-assigned-' + action + ' .badge-zone-body .security-badge');
    assigned.each(function() {
        config.inject_hidden_input(form, $(this));
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
