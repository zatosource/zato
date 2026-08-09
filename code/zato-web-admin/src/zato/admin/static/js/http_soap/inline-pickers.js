
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Service and Security columns of the HTTP/SOAP listings - each cell opens a popup
// menu, the menus open the single-pick panels, and the groups cell opens the badge picker,
// all of them saving through the inline machinery in http_soap/inline.js.

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.build_menu_button = function(label) {

    var out = document.createElement('input');

    out.type = 'button';
    out.value = label;

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The filter and the single-pick list every choice panel holds. Each visible row stands
// for one option, the picked one wearing the dot, and clicking any of them answers the panel.
$.fn.zato.http_soap.inline._build_pick_body = function(content, options, current, filter_placeholder, on_pick) {

    var inline = $.fn.zato.http_soap.inline;
    var lines = $.fn.zato.wizard_kit.lines;

    var list = document.createElement('div');
    list.className = 'wizard-panel-list';

    // The row of one option knows what it stands for and answers the panel when clicked
    var build_row = function(option) {
        var out = lines.buildPickRow(option.label, option.value === current, function() {
            on_pick(option);
        });
        return out;
    };

    var fill = function(filter_text) {

        var picked = null;
        list.textContent = '';

        for(var option_idx = 0; option_idx < options.length; option_idx++) {

            var option = options[option_idx];

            if(option.label.toLowerCase().indexOf(filter_text) === -1) {
                continue;
            }

            var row = build_row(option);
            list.appendChild(row);

            if(option.value === current) {
                picked = row;
            }
        }

        // A filter that leaves nothing behind says so rather than showing an empty list
        if(!list.childNodes.length) {
            var note = document.createElement('div');
            note.textContent = inline.config.no_matches_label;
            note.style.padding = '4px 8px';
            list.appendChild(note);
        }

        return picked;
    };

    // The same filter row the groups picker wears - the input and its Clear button.
    // The input keeps the wizard's own class and id, so an opening panel still
    // puts the typing here from the start.
    var filter_row = document.createElement('div');
    filter_row.className = 'badge-picker-filter';

    var filter_input = document.createElement('input');
    filter_input.type = 'text';
    filter_input.className = 'wizard-panel-filter';
    filter_input.id = 'wizard-panel-filter';
    filter_input.autocomplete = 'off';
    filter_input.placeholder = filter_placeholder;

    var clear_button = document.createElement('button');
    clear_button.type = 'button';
    clear_button.className = 'badge-filter-clear';
    clear_button.textContent = inline.config.clear_filter_label;

    filter_input.addEventListener('input', function() {
        fill(filter_input.value.trim().toLowerCase());
    });

    clear_button.addEventListener('click', function() {
        filter_input.value = '';
        fill('');
        filter_input.focus();
    });

    filter_row.appendChild(filter_input);
    filter_row.appendChild(clear_button);
    content.appendChild(filter_row);

    var picked = fill('');
    content.appendChild(list);

    // The list opens on what the row already uses, halfway down the view, so the options
    // around it are read as its neighbours. The panel takes its place and its remembered
    // size right after this build, hence the wait for the frame that has the list at its
    // final height.
    if(picked) {
        window.requestAnimationFrame(function() {
            list.scrollTop = picked.offsetTop - (list.clientHeight - picked.offsetHeight) / 2;
        });
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Opens one single-pick panel under the cell that was clicked
$.fn.zato.http_soap.inline._open_pick_panel = function(link, spec) {

    var inline = $.fn.zato.http_soap.inline;
    var lines = $.fn.zato.wizard_kit.lines;

    // Only one panel is on screen at a time
    lines.closePanel();

    lines.openPanel(link, {
        title: spec.title,
        width: inline.config.panel_width,
        minWidth: inline.config.panel_min_width,
        geometryKey: spec.geometry_key,

        build: function(content) {
            inline._build_pick_body(content, spec.options, spec.current, spec.filter_placeholder, spec.on_pick);
            return null;
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Service column - the panel's list comes from the very select the edit form uses
$.fn.zato.http_soap.inline.open_service_panel = function(link) {

    var inline = $.fn.zato.http_soap.inline;
    var id = link.getAttribute('data-id');
    var instance = $.fn.zato.data_table.data[id];

    var options = [];

    $('#id_edit-service option').each(function() {
        if(this.value) {
            options.push({value: this.value, label: this.value});
        }
    });

    var on_pick = function(option) {

        $.fn.zato.wizard_kit.lines.closePanel();

        // A channel always runs a service, so picking the one it already runs changes nothing
        if(option.value === instance.service) {
            return;
        }

        var data = {
            'service': option.value
        };

        var on_saved = function(saved) {

            // The row stands at what came back
            instance.service = saved.service_name;
            link.textContent = saved.service_name;

            // A save anchors its spinner on the very same link, and action_runner destroys
            // whatever tippy it finds there, so a saved cell is given a new popup
            inline.init_service_menu(link);
        };

        inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
    };

    inline._open_pick_panel(link, {
        title: inline.config.service_panel_title,
        filter_placeholder: inline.config.service_filter_placeholder,
        geometry_key: inline.config.service_panel_key,
        options: options,
        current: instance.service,
        on_pick: on_pick
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The two things a service can be done with, one to a button
$.fn.zato.http_soap.inline.build_service_menu = function(menu, name) {

    var inline = $.fn.zato.http_soap.inline;
    var config = inline.config;

    var out = document.createElement('div');
    out.className = 'zato-tippy-buttons';

    // The IDE is reached with a plain page load, so the browser's own Back button comes
    // back to this list rather than to wherever the list was opened from
    var ide_url = config.service_ide_url.replace('{name}', encodeURIComponent(name));
    var open_ide = inline.build_menu_button(config.open_ide_label);

    open_ide.addEventListener('click', function() {
        window.location.href = ide_url;
    });

    var change_service = inline.build_menu_button(config.change_service_label);

    change_service.addEventListener('click', function() {
        menu.hide();
        inline.open_service_panel(menu.reference);
    });

    out.appendChild(open_ide);
    out.appendChild(change_service);

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The popup of one service cell
$.fn.zato.http_soap.inline.init_service_menu = function(link) {

    var inline = $.fn.zato.http_soap.inline;
    var config = inline.config;

    // One popup to a link, whatever the cell was left with standing down
    if(link._tippy) {
        link._tippy.destroy();
    }

    tippy(link, {
        content: '',
        allowHTML: true,
        theme: config.menu_theme,
        trigger: 'click',
        placement: config.menu_placement,
        arrow: true,
        interactive: true,
        appendTo: document.body,

        onShow: function(menu) {

            var id = menu.reference.getAttribute('data-id');
            var instance = $.fn.zato.data_table.data[id];

            menu.setContent(inline.build_service_menu(menu, instance.service));
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.init_service_menus = function() {

    var inline = $.fn.zato.http_soap.inline;
    var links = document.querySelectorAll('#data-table a.http-soap-service-cell');

    for(var link_idx = 0; link_idx < links.length; link_idx++) {
        inline.init_service_menu(links[link_idx]);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The security definition part of the Security column - the panel's list comes from
// the very select the edit form uses, "No security definition" included
$.fn.zato.http_soap.inline.open_security_panel = function(link) {

    var inline = $.fn.zato.http_soap.inline;
    var id = link.getAttribute('data-id');
    var instance = $.fn.zato.data_table.data[id];

    // Each page keeps the composite value under its own name
    var security_attr = inline.config.security_attr;

    var options = [];

    $(inline.config.security_select + ' option').each(function() {
        if(this.value) {
            options.push({value: this.value, label: this.text});
        }
    });

    var on_pick = function(option) {

        $.fn.zato.wizard_kit.lines.closePanel();

        // Picking the definition the row already uses changes nothing
        if(option.value === instance[security_attr]) {
            return;
        }

        var data = {
            'security': option.value
        };

        var on_saved = function(saved) {

            // The row stands at what came back - the composite id feeds the edit form,
            // the label feeds the rebuilt rows
            instance[security_attr] = saved.security_id;
            instance[security_attr + '_select'] = option.label;

            inline.write_security_cell(link, saved);
            inline.init_security_menu(link);
        };

        inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
    };

    inline._open_pick_panel(link, {
        title: inline.config.security_panel_title,
        filter_placeholder: inline.config.security_filter_placeholder,
        geometry_key: inline.config.security_panel_key,
        options: options,
        current: instance[security_attr],
        on_pick: on_pick
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the definition part of the cell now says of itself
$.fn.zato.http_soap.inline.write_security_cell = function(link, saved) {

    var inline = $.fn.zato.http_soap.inline;

    if(saved.security_name) {
        link.textContent = '';

        // The outgoing SOAP listing names the definition's type above its name
        if(inline.config.show_sec_type_in_cell) {
            link.appendChild(document.createTextNode(saved.sec_type_name));
            link.appendChild(document.createElement('br'));
        }

        link.appendChild(document.createTextNode(saved.security_name));
    }
    else {
        link.textContent = inline.config.empty_security_label;
    }

    link.setAttribute('data-href', saved.security_href);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The two things a definition can be done with, one to a button
$.fn.zato.http_soap.inline.build_security_menu = function(menu) {

    var inline = $.fn.zato.http_soap.inline;
    var config = inline.config;
    var link = menu.reference;

    var out = document.createElement('div');
    out.className = 'zato-tippy-buttons';

    // The definition's page is reached with a plain page load, so the browser's own
    // Back button comes back to this list
    var href = link.getAttribute('data-href');
    var go_to_definition = inline.build_menu_button(config.go_to_definition_label);

    go_to_definition.addEventListener('click', function() {
        window.location.href = href;
    });

    var change_definition = inline.build_menu_button(config.change_definition_label);

    change_definition.addEventListener('click', function() {
        menu.hide();
        inline.open_security_panel(link);
    });

    out.appendChild(go_to_definition);
    out.appendChild(change_definition);

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The popup of one security definition cell
$.fn.zato.http_soap.inline.init_security_menu = function(link) {

    var inline = $.fn.zato.http_soap.inline;
    var config = inline.config;

    // One popup to a link, whatever the cell was left with standing down
    if(link._tippy) {
        link._tippy.destroy();
    }

    tippy(link, {
        content: '',
        allowHTML: true,
        theme: config.menu_theme,
        trigger: 'click',
        placement: config.menu_placement,
        arrow: true,
        interactive: true,
        appendTo: document.body,

        onShow: function(menu) {

            // A row with no definition has nothing to go to, so the picker comes up at once
            if(!menu.reference.getAttribute('data-href')) {
                inline.open_security_panel(menu.reference);
                return false;
            }

            menu.setContent(inline.build_security_menu(menu));
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline.init_security_menus = function() {

    var inline = $.fn.zato.http_soap.inline;
    var links = document.querySelectorAll('#data-table a.http-soap-security-cell');

    for(var link_idx = 0; link_idx < links.length; link_idx++) {
        inline.init_security_menu(links[link_idx]);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The filter and the two zones the groups panel holds, the same markup the channel's
// own edit form renders - the badge picker wires itself up to the ids derived from
// the action, so the panel only has to put them on the page.
$.fn.zato.http_soap.inline._build_groups_body = function(content) {

    var inline = $.fn.zato.http_soap.inline;
    var action = inline.config.groups_element_action;

    content.innerHTML = '' +
        '<div class="badge-picker-filter" id="badge-filter-' + action + '">' +
            '<input type="text" id="badge-filter-text-' + action + '" placeholder="' + inline.config.groups_filter_placeholder + '" />' +
            '<button type="button" class="badge-filter-clear" id="badge-filter-clear-' + action + '">Clear</button>' +
        '</div>' +
        '<div class="badge-picker" id="badge-picker-' + action + '">' +
            '<div class="badge-zone" id="badge-zone-available-' + action + '">' +
                '<div class="badge-zone-header">Available (<span class="badge-zone-count">0</span>)</div>' +
                '<div class="badge-zone-body"></div>' +
            '</div>' +
            '<div class="badge-picker-resizer"></div>' +
            '<div class="badge-zone" id="badge-zone-assigned-' + action + '">' +
                '<div class="badge-zone-header">Assigned (<span class="badge-zone-count">0</span>)</div>' +
                '<div class="badge-zone-body"></div>' +
            '</div>' +
        '</div>';
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The ids of the groups the assigned zone holds, sorted so two reads compare as one
$.fn.zato.http_soap.inline._read_groups = function() {

    var inline = $.fn.zato.http_soap.inline;

    var out = $.fn.zato.badge_picker.get_assigned_ids(inline.config.groups_element_action);
    out.sort();

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the whole security cell of a channel now says of itself - the definition's
// name, the groups beneath it, or the invitation when the row holds neither
$.fn.zato.http_soap.inline.write_channel_security_cell = function(link, saved) {

    var inline = $.fn.zato.http_soap.inline;

    var has_name = Boolean(saved.security_name);
    var has_groups = Boolean(saved.security_groups_info) && saved.security_groups_info.charAt(0) != '0';

    link.textContent = '';

    if(has_name) {
        link.appendChild(document.createTextNode(saved.security_name));
    }

    if(has_groups) {
        if(has_name) {
            link.appendChild(document.createElement('br'));
        }
        link.appendChild(document.createTextNode(saved.security_groups_info));
    }

    if(!has_name && !has_groups) {
        link.textContent = inline.config.empty_security_label;
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The one popup a channel's security cell opens - the IDE's own action-menu layout,
// the list on the left and the live pane on the right, hovering over an entry being
// what switches the pane. Both panes are built before the popup shows, so switching
// is immediate. The groups list is brought over first and the popup comes on screen
// already populated, in one paint.
$.fn.zato.http_soap.inline.open_security_menu = function(link) {

    var inline = $.fn.zato.http_soap.inline;
    var lines = $.fn.zato.wizard_kit.lines;
    var url = inline.config.groups_url + link.getAttribute('data-id');

    var on_response = function(data, status) {

        if(status != 'success') {
            inline.flash(link, inline.config.load_error_label);
            return;
        }

        var items = JSON.parse(data.responseText);

        // Only one panel is on screen at a time - a click elsewhere while
        // the list was in flight may have opened another one by now
        lines.closePanel();

        inline._open_security_menu(link, items);
    };

    $.fn.zato.post(url, on_response, '', '', true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.http_soap.inline._open_security_menu = function(link, items) {

    var inline = $.fn.zato.http_soap.inline;
    var lines = $.fn.zato.wizard_kit.lines;
    var id = link.getAttribute('data-id');
    var instance = $.fn.zato.data_table.data[id];
    var security_attr = inline.config.security_attr;

    // What the groups stood at when the popup opened, compared against when it closes
    var groups_baseline = [];

    for(var item_idx = 0; item_idx < items.length; item_idx++) {
        if(items[item_idx].is_assigned) {
            groups_baseline.push(items[item_idx].id);
        }
    }
    groups_baseline.sort();

    // What the definition stood at - a pick is only remembered here, both panes
    // save together in one go when the popup closes
    var security_baseline = instance[security_attr];
    var picked_security = security_baseline;
    var picked_security_label = '';

    // A pane with nothing to pick from says so instead of showing its empty chrome
    var build_empty_note = function(message) {
        var note = document.createElement('div');
        note.className = 'form_hint';
        note.textContent = message;
        return note;
    };

    var build_definition_pane = function(holder) {

        var options = [];

        $(inline.config.security_select + ' option').each(function() {
            if(this.value) {
                options.push({value: this.value, label: this.text});
            }
        });

        if(!options.length) {
            holder.appendChild(build_empty_note(inline.config.definitions_empty_message));
            return;
        }

        // The filter keeps its height inside the pane, so the list under it is
        // the only thing that grows with the popup
        var pin_filter = function() {
            holder.querySelector('.badge-picker-filter').style.flex = '0 0 auto';
        };

        var on_pick = function(option) {

            // The pick is only remembered - the popup stays open so the groups
            // can be changed in the same visit, everything saves on close
            picked_security = option.value;
            picked_security_label = option.label;

            // The dot moves to the picked row
            holder.textContent = '';
            inline._build_pick_body(
                holder, options, picked_security, inline.config.security_filter_placeholder, on_pick);
            pin_filter();
        };

        inline._build_pick_body(
            holder, options, picked_security, inline.config.security_filter_placeholder, on_pick);
        pin_filter();
    };

    var build_groups_pane = function(holder) {

        if(!items.length) {
            holder.appendChild(build_empty_note(inline.config.groups_empty_message));
            return;
        }

        inline._build_groups_body(holder);

        // The list already says which of the groups the channel holds
        $.fn.zato.badge_picker.init(inline.config.groups_element_action, items, {
            is_assigned: function(item) {
                return item.is_assigned;
            }
        });

        // A filter that leaves nothing on the available side says so - the picker
        // itself only hides the badges, one by one
        var action = inline.config.groups_element_action;
        var available_body = holder.querySelector('#badge-zone-available-' + action + ' .badge-zone-body');
        var filter_input = holder.querySelector('#badge-filter-text-' + action);

        var no_matches_note = document.createElement('div');
        no_matches_note.textContent = inline.config.no_matches_label;
        no_matches_note.style.padding = '6px 8px';
        no_matches_note.style.display = 'none';
        available_body.appendChild(no_matches_note);

        var update_no_matches = function() {

            var badges = available_body.querySelectorAll('.security-badge');
            var visible_count = 0;

            for(var badge_idx = 0; badge_idx < badges.length; badge_idx++) {
                if(badges[badge_idx].style.display !== 'none') {
                    visible_count += 1;
                }
            }

            // An empty zone with no filter is just an empty zone - only a filter
            // that hid everything has something to say
            var is_filtered_out = Boolean(filter_input.value.trim()) && !visible_count;
            no_matches_note.style.display = is_filtered_out ? '' : 'none';
        };

        // The picker's own filter is debounced, so the check waits a touch longer
        var note_timer = null;

        filter_input.addEventListener('input', function() {
            clearTimeout(note_timer);
            note_timer = setTimeout(update_no_matches, 200);
        });

        holder.querySelector('#badge-filter-clear-' + action).addEventListener('click', update_no_matches);

        // The filter keeps its height while the zones fill the rest of the pane -
        // their own stylesheet caps them at a fixed height for the edit form,
        // here the popup's height is what they follow. Their minimum stays, it is
        // what gives the popup its opening height.
        holder.querySelector('.badge-picker-filter').style.flex = '0 0 auto';

        var picker = holder.querySelector('.badge-picker');
        picker.style.flex = '1';
        picker.style.minHeight = '0';

        var zone_bodies = holder.querySelectorAll('.badge-zone-body');

        for(var zone_idx = 0; zone_idx < zone_bodies.length; zone_idx++) {
            zone_bodies[zone_idx].style.maxHeight = 'none';
        }
    };

    lines.openPanel(link, {
        title: inline.config.security_menu_title,
        width: inline.config.groups_panel_width,
        minWidth: inline.config.groups_panel_min_width,
        geometryKey: inline.config.security_menu_key,

        build: function(content) {

            // The flex chain of the wizard panel runs on through these divs, so the
            // lists inside fill the popup's height and follow it when it is resized
            var body = document.createElement('div');
            body.className = 'grid-panel-body';
            body.style.flex = '1';
            body.style.minHeight = '0';

            var list = document.createElement('div');
            list.className = 'grid-panel-list';

            // The panes take the room the list leaves - the pickers are wider than the
            // IDE's own information pane. Both panes share the one grid cell, so the
            // popup is naturally as tall as the taller of the two and switching between
            // them can never change its size.
            var panes = document.createElement('div');
            panes.style.display = 'grid';
            panes.style.flex = '1';
            panes.style.minWidth = '0';
            panes.style.minHeight = '0';

            var entries = [];
            var pane_elems = [];

            // The hovered entry wears the highlight, its pane alone is in view - the
            // other stays in the layout, invisible, which is what keeps the size steady
            var show_pane = function(pane_idx) {
                for(var idx = 0; idx < entries.length; idx++) {
                    entries[idx].classList.toggle('current', idx === pane_idx);
                    pane_elems[idx].style.visibility = idx === pane_idx ? '' : 'hidden';
                }
            };

            // On the page before anything is filled in - the badge picker finds
            // its zones by their ids, so a pane built while detached stays empty
            body.appendChild(list);
            body.appendChild(panes);
            content.appendChild(body);

            var add_pane = function(label, build) {

                var entry = document.createElement('div');
                entry.className = 'grid-panel-item';

                var entry_label = document.createElement('span');
                entry_label.className = 'grid-panel-item-label';
                entry_label.textContent = label;
                entry.appendChild(entry_label);

                var pane_idx = entries.length;
                entry.addEventListener('mouseenter', function() {
                    show_pane(pane_idx);
                });

                entries.push(entry);
                list.appendChild(entry);

                var pane = document.createElement('div');
                pane.style.display = 'flex';
                pane.style.flexDirection = 'column';
                pane.style.gridArea = '1 / 1';
                pane.style.minHeight = '0';
                pane.style.minWidth = '0';

                pane_elems.push(pane);
                panes.appendChild(pane);

                build(pane);
            };

            add_pane(inline.config.definition_pane_label, build_definition_pane);
            add_pane(inline.config.groups_pane_label, build_groups_pane);

            show_pane(0);

            // What runs when the popup closes, however it was closed - only what
            // changed travels, a popup closed on what it opened with saves nothing
            return function() {

                var data = {};

                var picked_groups = inline._read_groups();

                if(JSON.stringify(picked_groups) !== JSON.stringify(groups_baseline)) {
                    data['security_groups'] = JSON.stringify(picked_groups);
                }

                if(picked_security !== security_baseline) {
                    data['security'] = picked_security;
                }

                if(!Object.keys(data).length) {
                    return;
                }

                var on_saved = function(saved) {

                    // The row stands at what came back - the composite id feeds the edit form,
                    // the label feeds the rebuilt rows
                    instance[security_attr] = saved.security_id;

                    if(picked_security_label) {
                        instance[security_attr + '_select'] = picked_security_label;
                    }

                    inline.write_channel_security_cell(link, saved);
                };

                inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
            };
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The menus hang off the cells once the page's own scripts have parsed the table
$(document).ready(function() {
    $.fn.zato.http_soap.inline.init_service_menus();
    $.fn.zato.http_soap.inline.init_security_menus();
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
