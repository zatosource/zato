
/* Dashboard kit - the select and the dropdown menu behind it.
   One home for the grouped, filterable menu that used to live in rate-limiting.js
   and for a select built on top of it - a trigger showing what is picked, opening
   the menu underneath. The menu look is shared/dropdown-menu.css, the trigger wears
   whatever classes its page hands it - it has no face of its own. */



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
       flavour, marked when config.is_picked says the value is a picked one. */
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
            if (config.is_picked(item.value)) {
                row.className = 'zato-dropdown-item zato-dropdown-item-selected';
            }

            // A toggling row carries a checkbox of its own, filled in when picked
            if (config.toggle_pick) {
                var check_span = document.createElement('span');
                check_span.className = 'zato-dropdown-item-check';
                row.appendChild(check_span);
            }

            var text_span = document.createElement('span');
            text_span.className = 'zato-dropdown-item-text';
            text_span.textContent = item.label;
            row.appendChild(text_span);
        }

        row.onclick = function() {
            config.on_select(item.value);

            // A toggling pick flips its own mark and leaves the menu up, so several
            // can be picked in one visit ..
            if (config.toggle_pick) {
                row.classList.toggle('zato-dropdown-item-selected');
            }

            // .. a kept-open pick takes its row along, the suggestion flavour ..
            else if (config.keep_open) {
                row.parentNode.removeChild(row);
            }

            // .. and a plain pick is the menu's last word.
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
         anchor:      the element the menu hangs off
         groups:      [{group, items: [{value, label}]}]
         filter:      text the items are narrowed by before the menu opens
         on_select:   callback(value)
         excluded:    map of values left out, e.g. ones already picked as pills
         keep_open:   a pick removes its row rather than the menu
         toggle_pick: a pick flips its own mark and leaves the menu up
         item_style:  'value_label' or 'text'
         is_picked:   function(value) saying which rows are marked (item_style 'text')
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
         host:        selector or element the trigger is rendered into
         trigger_cls: the classes the trigger wears - the page's own look, not the kit's
         label:       what the select is called, standing before the value
         groups:      [{group, items: [{value, label}]}]
         value:       the value picked at the start
         on_change:   callback(value), called on picks that change the value
       With multi: true, several values can be picked at once - picks toggle and the menu
       stays up. Then `values` replaces `value`, on_change receives the picked list,
       `empty_label` is what the trigger says when nothing is picked and `many_label`
       the word after the count when more than one is.
       Returns {set_groups} plus {get_value, set_value} or {get_values, set_values}. */
    ns.select.create = function(config) {
        var host = $(config.host)[0];
        var groups = config.groups;
        var multi = config.multi === true;

        var current_value = config.value;
        var current_values = config.values;

        // The trigger has no look of the kit's own - dashboard-select-trigger is
        // layout alone and everything visible about it comes from the caller
        var trigger = document.createElement('span');
        trigger.className = 'dashboard-select-trigger ' + config.trigger_cls;

        var label_span = document.createElement('span');
        label_span.className = 'dashboard-select-label';
        label_span.textContent = config.label;
        trigger.appendChild(label_span);

        var value_span = document.createElement('span');
        value_span.className = 'dashboard-select-value';
        trigger.appendChild(value_span);

        var chevron = document.createElement('span');
        chevron.className = 'dashboard-select-chevron';
        chevron.textContent = '\u25be';
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

        var is_picked = function(value) {
            if (multi) {
                return current_values.indexOf(value) !== -1;
            }

            return value === current_value;
        };

        var apply = function() {
            if (!multi) {
                value_span.textContent = label_of(current_value);
                return;
            }

            // Nothing picked is everything on offer, one pick is named, more are counted
            if (current_values.length === 0) {
                value_span.textContent = config.empty_label;
            }
            else if (current_values.length === 1) {
                value_span.textContent = label_of(current_values[0]);
            }
            else {
                value_span.textContent = current_values.length + ' ' + config.many_label;
            }
        };

        var pick = function(value) {
            if (multi) {
                var value_idx = current_values.indexOf(value);

                if (value_idx === -1) {
                    current_values.push(value);
                }
                else {
                    current_values.splice(value_idx, 1);
                }

                apply();

                // The caller gets a copy - what it does with the list is its own affair
                config.on_change(current_values.slice());
                return;
            }

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
                toggle_pick: multi,
                item_style: 'text',
                is_picked: is_picked,
                with_filter: item_count() > filter_threshold
            });
        };

        apply();

        var out = {
            set_groups: function(new_groups) {
                groups = new_groups;
                apply();
            }
        };

        if (multi) {
            out.get_values = function() {
                return current_values.slice();
            };
            out.set_values = function(values) {
                current_values = values.slice();
                apply();
            };
        }
        else {
            out.get_value = function() {
                return current_value;
            };
            out.set_value = function(value) {
                current_value = value;
                apply();
            };
        }

        return out;
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
