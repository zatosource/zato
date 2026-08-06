
/* Dashboard kit - the select and the dropdown menu behind it.
   One home for the grouped, filterable menu that used to live in rate-limiting.js
   and for a select built on top of it - a trigger showing the current value, opening
   the menu underneath. The menu look is shared/dropdown-menu.css, the trigger look
   is dashboard-kit/select.css. */



(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.select = {};

    /* The one menu open at a time, whoever opened it, and what it hangs off -
       a click into the anchor is part of using the menu, not a click away from it */
    var menu_id = 'dashboard-select-menu-active';
    var active_anchor = null;

    /* How many items a select holds before its menu grows a filter box */
    var filter_threshold = 8;

    // ////////////////////////////////////////////////////////////////////////

    ns.select.hide_menu = function() {
        var existing = document.getElementById(menu_id);

        if (existing) {
            existing.parentNode.removeChild(existing);
        }

        active_anchor = null;
    };

    // ////////////////////////////////////////////////////////////////////////

    /* One row of the menu. item_style 'value_label' draws the value and its label as
       two spans - the suggestion flavour - and 'text' draws one plain span, the select
       flavour, marked when it is the value currently picked. */
    ns.select.make_item = function(item, config) {
        var row = document.createElement('div');
        row.className = 'zato-dropdown-item';

        if (config.item_style === 'value_label') {
            var value_span = document.createElement('span');
            value_span.className = 'zato-dropdown-item-value';
            value_span.textContent = item.value;
            row.appendChild(value_span);

            var label_span = document.createElement('span');
            label_span.className = 'zato-dropdown-item-label';
            label_span.textContent = item.label;
            row.appendChild(label_span);
        }
        else {
            if (item.value === config.selected) {
                row.className = 'zato-dropdown-item zato-dropdown-item-selected';
            }

            var text_span = document.createElement('span');
            text_span.className = 'zato-dropdown-item-text';
            text_span.textContent = item.label;
            row.appendChild(text_span);
        }

        row.onclick = function() {
            config.on_select(item.value);

            if (config.keep_open) {
                row.parentNode.removeChild(row);
            }
            else {
                ns.select.hide_menu();
            }
        };

        return row;
    };

    // ////////////////////////////////////////////////////////////////////////

    /* The rows of the menu - group headers, separators and items - as one fragment,
       so a filter box can swap the rows out without taking the menu itself down.
       Returns null when nothing matches, which is the caller's cue to show nothing. */
    ns.select.build_rows = function(config) {
        var fragment = document.createDocumentFragment();

        var filter = (config.filter || '').trim().toLowerCase();
        var total_items = 0;

        for (var group_idx = 0; group_idx < config.groups.length; group_idx++) {
            var group = config.groups[group_idx];
            var matching_items = [];

            for (var item_idx = 0; item_idx < group.items.length; item_idx++) {
                var item = group.items[item_idx];

                // Skip already-selected values
                if (config.excluded && config.excluded[item.value]) {
                    continue;
                }

                // Apply text filter
                if (filter && item.value.toLowerCase().indexOf(filter) === -1 &&
                        item.label.toLowerCase().indexOf(filter) === -1) {
                    continue;
                }

                matching_items.push(item);
            }

            if (matching_items.length === 0) {
                continue;
            }

            // Add separator between groups
            if (total_items > 0) {
                var separator = document.createElement('div');
                separator.className = 'zato-dropdown-separator';
                fragment.appendChild(separator);
            }

            // A group of one unnamed group carries no header at all
            if (group.group) {
                var header = document.createElement('div');
                header.className = 'zato-dropdown-header';
                header.textContent = group.group;
                fragment.appendChild(header);
            }

            for (var match_idx = 0; match_idx < matching_items.length; match_idx++) {
                fragment.appendChild(ns.select.make_item(matching_items[match_idx], config));
                total_items++;
            }
        }

        if (total_items === 0) {
            return null;
        }

        return fragment;
    };

    // ////////////////////////////////////////////////////////////////////////

    /* Opens the menu under its anchor. config:
         anchor:     the element the menu hangs off
         groups:     [{group, items: [{value, label}]}]
         filter:     text the items are narrowed by before the menu opens
         on_select:  callback(value)
         excluded:   map of values left out, e.g. ones already picked as pills
         keep_open:  a pick removes its row rather than the menu
         item_style: 'value_label' or 'text'
         selected:   the value marked as the current one (item_style 'text')
         with_filter: put a filter box at the top of the menu */
    ns.select.show_menu = function(config) {

        ns.select.hide_menu();

        var rows = ns.select.build_rows(config);

        if (rows === null && !config.with_filter) {
            return;
        }

        var menu = document.createElement('div');
        menu.className = 'zato-dropdown-menu';
        menu.id = menu_id;

        /* The filter box narrows the rows in place - the menu itself stays up,
           so what is typed is not lost to a rebuild. */
        if (config.with_filter) {
            var filter_input = document.createElement('input');
            filter_input.type = 'text';
            filter_input.className = 'dashboard-select-filter';
            filter_input.placeholder = 'Filter ..';

            var rows_host = document.createElement('div');

            filter_input.oninput = function() {
                config.filter = filter_input.value;

                var new_rows = ns.select.build_rows(config);
                rows_host.textContent = '';

                if (new_rows !== null) {
                    rows_host.appendChild(new_rows);
                }
            };

            menu.appendChild(filter_input);
            menu.appendChild(rows_host);

            if (rows !== null) {
                rows_host.appendChild(rows);
            }
        }
        else {
            menu.appendChild(rows);
        }

        // Position below the anchor element, never narrower than the anchor itself
        var rect = config.anchor.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = (rect.bottom + 2) + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.minWidth = rect.width + 'px';

        document.body.appendChild(menu);
        active_anchor = config.anchor;

        if (config.with_filter) {
            menu.querySelector('.dashboard-select-filter').focus();
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    /* A select - a trigger showing what is picked, the menu underneath picking it. config:
         host:      selector or element the trigger is rendered into
         label:     what the select is called, standing before the value
         groups:    [{group, items: [{value, label}]}]
         value:     the value picked at the start
         on_change: callback(value), called on picks that change the value
       Returns {get_value, set_value, set_groups}. */
    ns.select.create = function(config) {
        var host = $(config.host)[0];
        var current_value = config.value;
        var groups = config.groups;

        var trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'dashboard-select';

        var label_span = document.createElement('span');
        label_span.className = 'dashboard-select-label';
        label_span.textContent = config.label;
        trigger.appendChild(label_span);

        var value_span = document.createElement('span');
        value_span.className = 'dashboard-select-value';
        trigger.appendChild(value_span);

        var chevron = document.createElement('span');
        chevron.className = 'dashboard-select-chevron';
        trigger.appendChild(chevron);

        host.appendChild(trigger);

        /* What the trigger shows is the picked item's own label, found by its value */
        var label_of = function(value) {
            for (var group_idx = 0; group_idx < groups.length; group_idx++) {
                var items = groups[group_idx].items;

                for (var item_idx = 0; item_idx < items.length; item_idx++) {
                    if (items[item_idx].value === value) {
                        return items[item_idx].label;
                    }
                }
            }

            return value;
        };

        var item_count = function() {
            var count = 0;

            for (var group_idx = 0; group_idx < groups.length; group_idx++) {
                count += groups[group_idx].items.length;
            }

            return count;
        };

        var apply = function() {
            value_span.textContent = label_of(current_value);
        };

        var pick = function(value) {
            // Picking what is already picked is not a change
            if (value === current_value) {
                return;
            }

            current_value = value;
            apply();

            config.on_change(value);
        };

        trigger.onclick = function() {
            // The trigger is also how an open menu is put away
            if (document.getElementById(menu_id)) {
                ns.select.hide_menu();
                return;
            }

            ns.select.show_menu({
                anchor: trigger,
                groups: groups,
                filter: '',
                on_select: pick,
                excluded: null,
                keep_open: false,
                item_style: 'text',
                selected: current_value,
                with_filter: item_count() > filter_threshold
            });
        };

        apply();

        return {
            get_value: function() {
                return current_value;
            },
            set_value: function(value) {
                current_value = value;
                apply();
            },
            set_groups: function(new_groups) {
                groups = new_groups;
                apply();
            }
        };
    };

    // ////////////////////////////////////////////////////////////////////////

    /* A click landing outside both the menu and the anchor it hangs off puts the menu
       away, and so does Escape. Registered once, serving every menu on the page. */
    $(document).on('mousedown', function(event) {
        var menu = document.getElementById(menu_id);

        if (!menu) {
            return;
        }

        if (menu.contains(event.target)) {
            return;
        }

        if (active_anchor !== null && active_anchor.contains(event.target)) {
            return;
        }

        ns.select.hide_menu();
    });

    $(document).on('keydown', function(event) {
        if (event.key === 'Escape') {
            ns.select.hide_menu();
        }
    });
})();
