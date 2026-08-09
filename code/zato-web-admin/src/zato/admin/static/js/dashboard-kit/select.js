
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

    /* What to tell whoever opened the current menu once it goes away - optional,
       registered by show_menu and fired exactly once by hide_menu, so a page that
       reloads on its filters can apply several toggles in one visit to the menu */
    var active_on_close = null;

    /* How many items a select holds before its menu grows a filter box */
    var filter_threshold = 8;

    /* The class a trigger wears while its menu is up, and the one the keyboard's
       active row carries */
    var open_class = 'dashboard-select-trigger-open';
    var active_row_class = 'zato-dropdown-item-active';

    /* What the All row of a multi-select carries as its value - no real item
       has an empty one */
    var all_value = '';

    // ////////////////////////////////////////////////////////////////////////

    ns.select.hide_menu = function() {
        var existing = document.getElementById(menu_id);

        if (existing) {
            existing.parentNode.removeChild(existing);
        }

        // Whatever the menu hung off stops saying it is open
        if (active_anchor !== null) {
            active_anchor.classList.remove(open_class);
        }

        active_anchor = null;

        // Whoever asked to hear about the closing hears it once, after the cleanup,
        // so the callback sees the menu already gone
        var on_close = active_on_close;
        active_on_close = null;

        if (on_close) {
            on_close();
        }
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

            // A tri-state row wears its state - the included look is the picked one,
            // the excluded look is its own - and a two-state row only knows picked
            if (config.get_state) {
                var state = config.get_state(item.value);

                if (state === 'included') {
                    row.className = 'zato-dropdown-item zato-dropdown-item-selected';
                }
                else if (state === 'excluded') {
                    row.className = 'zato-dropdown-item zato-dropdown-item-excluded';
                }
            }
            else if (config.is_picked(item.value)) {
                row.className = 'zato-dropdown-item zato-dropdown-item-selected';
            }

            var text_span = document.createElement('span');
            text_span.className = 'zato-dropdown-item-text';
            text_span.textContent = item.label;
            row.appendChild(text_span);

            // A toggling row holds room for a checkmark after its text - the mark
            // itself appears only while the row is picked
            if (config.toggle_pick) {
                var check_span = document.createElement('span');
                check_span.className = 'zato-dropdown-item-check';
                row.appendChild(check_span);
            }
        }

        row.onclick = function() {
            config.on_select(item.value);

            // A toggling pick leaves the menu up, so several can be picked in one
            // visit, and the rows are redrawn so every mark stays truthful - the
            // pick's own, and the All row's, which stands for no picks at all ..
            if (config.toggle_pick) {
                config.rerender();
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
         get_state:   optional function(value) answering 'included', 'excluded' or 'unset' -
                      the tri-state flavour, taking precedence over is_picked for the rows
         with_filter: put a filter box at the top of the menu
         on_close:    optional callback(), fired once when the menu goes away */
    ns.select.show_menu = function(config) {

        ns.select.hide_menu();

        var rows = ns.select.build_rows(config);

        if (rows === null && !config.with_filter) {
            return;
        }

        var menu = document.createElement('div');
        menu.className = 'zato-dropdown-menu';
        menu.id = menu_id;

        /* The rows live in a host of their own so they can be redrawn in place -
           after a keystroke of the filter box and after every toggling pick -
           while the menu itself stays up */
        var rows_host = document.createElement('div');

        config.rerender = function() {
            var new_rows = ns.select.build_rows(config);
            rows_host.textContent = '';

            if (new_rows !== null) {
                rows_host.appendChild(new_rows);
            }
        };

        if (config.with_filter) {
            var filter_input = document.createElement('input');
            filter_input.type = 'text';
            filter_input.className = 'dashboard-select-filter';
            filter_input.placeholder = 'Filter ..';

            filter_input.oninput = function() {
                config.filter = filter_input.value;
                config.rerender();
            };

            menu.appendChild(filter_input);
        }

        menu.appendChild(rows_host);

        if (rows !== null) {
            rows_host.appendChild(rows);
        }

        // Position below the anchor element, never narrower than the anchor itself
        var rect = config.anchor.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = (rect.bottom + 2) + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.minWidth = rect.width + 'px';

        document.body.appendChild(menu);

        // The menu sizes itself to its widest row, but a vertical scrollbar then eats
        // into that width from the inside - the widest row overflows into the padding
        // and its checkmark drifts off the common edge - so the menu grows by the
        // scrollbar's own width and every row keeps the full width it asked for
        var scrollbar_width = menu.offsetWidth - menu.clientWidth;

        if (scrollbar_width > 0) {
            menu.style.width = (menu.offsetWidth + scrollbar_width) + 'px';
        }

        active_anchor = config.anchor;

        // Whoever opened the menu may ask to hear about it closing
        if (config.on_close) {
            active_on_close = config.on_close;
        }
        else {
            active_on_close = null;
        }

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
       the word after the count when more than one is. The menu opens with an All row
       at the top, named by `empty_label` - picking it lets every other pick go.
       An optional `on_close` is fired once when the menu goes away, which is where
       a page that reloads on its filters applies what was toggled in one visit.
       With tri_state: true on top of multi, every item carries one of three states and
       a click cycles it - unset to included to excluded and back to unset. The excluded
       picks start out as `excluded_values`, on_change receives (included, excluded),
       and a trigger whose picks amount to everything-but reads `except_label` and the
       count or the one excluded item's own label.
       Returns {set_groups} plus {get_value, set_value} or {get_values, set_values},
       and a tri-state select adds {get_excluded, set_excluded}. */
    ns.select.create = function(config) {
        var host = $(config.host)[0];
        var groups = config.groups;
        var multi = config.multi === true;
        var tri_state = config.tri_state === true;

        var current_value = config.value;
        var current_values = config.values;

        // Only a tri-state select holds excluded picks of its own
        var current_excluded = [];

        if (tri_state) {
            current_excluded = config.excluded_values;
        }

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

        // The chevron is drawn by the stylesheet, not a glyph, so it can turn over
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

        var is_picked = function(value) {
            if (multi) {

                // The All row stands for no picks at all, so it is the one
                // marked while the list is empty
                if (value === all_value) {
                    return current_values.length === 0 && current_excluded.length === 0;
                }

                return current_values.indexOf(value) !== -1;
            }

            return value === current_value;
        };

        /* Which of the three states one row is in - the All row reads as included
           while there are no picks of either kind, standing for everything */
        var get_state = function(value) {
            if (value === all_value) {
                if (current_values.length === 0 && current_excluded.length === 0) {
                    return 'included';
                }

                return 'unset';
            }

            if (current_values.indexOf(value) !== -1) {
                return 'included';
            }

            if (current_excluded.indexOf(value) !== -1) {
                return 'excluded';
            }

            return 'unset';
        };

        var apply = function() {
            if (!multi) {
                value_span.textContent = label_of(current_value);
                return;
            }

            // A trigger whose picks amount to everything-but wears the excluding face
            var is_excluding = tri_state && current_values.length === 0 && current_excluded.length > 0;

            value_span.classList.toggle('dashboard-select-value-excluding', is_excluding);

            // Everything-but names the one value cut out or counts several of them ..
            if (is_excluding) {
                if (current_excluded.length === 1) {
                    value_span.textContent = config.except_label + ' ' + label_of(current_excluded[0]);
                }
                else {
                    value_span.textContent = config.except_label + ' ' + current_excluded.length;
                }

                return;
            }

            // .. nothing picked is everything on offer, one pick is named, more are counted.
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

                // Picking All is picking nothing - every other pick of either kind is let go
                if (value === all_value) {
                    current_values = [];
                    current_excluded = [];
                }
                else if (tri_state) {

                    // The cycle - an unset pick is included, an included one turns
                    // excluded and an excluded one is let go back to unset
                    var included_idx = current_values.indexOf(value);
                    var excluded_idx = current_excluded.indexOf(value);

                    if (included_idx !== -1) {
                        current_values.splice(included_idx, 1);
                        current_excluded.push(value);
                    }
                    else if (excluded_idx !== -1) {
                        current_excluded.splice(excluded_idx, 1);
                    }
                    else {
                        current_values.push(value);
                    }
                }
                else {
                    var value_idx = current_values.indexOf(value);

                    if (value_idx === -1) {
                        current_values.push(value);
                    }
                    else {
                        current_values.splice(value_idx, 1);
                    }
                }

                apply();

                // The caller gets copies - what it does with the lists is its own affair
                if (tri_state) {
                    config.on_change(current_values.slice(), current_excluded.slice());
                }
                else {
                    config.on_change(current_values.slice());
                }

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

            // A multi-select's menu opens with an All row of its own at the top,
            // the one pick that stands for no picks at all
            var menu_groups = groups;

            if (multi) {
                var all_group = {group: '', items: [{value: all_value, label: config.empty_label}]};
                menu_groups = [all_group].concat(groups);
            }

            ns.select.show_menu({
                anchor: trigger,
                groups: menu_groups,
                filter: '',
                on_select: pick,
                excluded: null,
                keep_open: false,
                toggle_pick: multi,
                item_style: 'text',
                is_picked: is_picked,
                get_state: tri_state ? get_state : null,
                with_filter: item_count() > filter_threshold,
                on_close: config.on_close
            });

            // The trigger wears its open look until hide_menu takes it back
            trigger.classList.add(open_class);
        };

        apply();

        var out = {
            set_groups: function(new_groups) {
                groups = new_groups;
                apply();
            },

            /* A disabled select stands aside - its menu, if up, goes away with it and
               its value says why there is nothing to pick, coming back on re-enabling */
            set_enabled: function(flag) {
                trigger.classList.toggle('dashboard-select-trigger-disabled', !flag);

                if (flag) {
                    apply();
                    return;
                }

                if (config.disabled_label !== undefined) {
                    value_span.textContent = config.disabled_label;
                }

                if (active_anchor === trigger) {
                    ns.select.hide_menu();
                }
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

        // Only a tri-state select has excluded picks to hand out and take in
        if (tri_state) {
            out.get_excluded = function() {
                return current_excluded.slice();
            };
            out.set_excluded = function(values) {
                current_excluded = values.slice();
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

    /* The row the arrow keys stand on moves one step, wrapping at either end,
       and is kept in sight when the menu scrolls */
    var move_active = function(menu, step) {
        var rows = menu.querySelectorAll('.zato-dropdown-item');

        if (rows.length === 0) {
            return;
        }

        var current = -1;

        for (var row_idx = 0; row_idx < rows.length; row_idx++) {
            if (rows[row_idx].classList.contains(active_row_class)) {
                current = row_idx;
            }
        }

        var next = current + step;

        if (next < 0) {
            next = rows.length - 1;
        }

        if (next >= rows.length) {
            next = 0;
        }

        if (current !== -1) {
            rows[current].classList.remove(active_row_class);
        }

        rows[next].classList.add(active_row_class);
        rows[next].scrollIntoView({block: 'nearest'});
    };

    /* The keyboard drives an open menu - arrows walk the rows, Enter picks the one
       stood on, Escape first empties the filter and only then puts the menu away */
    $(document).on('keydown', function(event) {
        var menu = document.getElementById(menu_id);

        if (!menu) {
            return;
        }

        if (event.key === 'ArrowDown') {
            // The page must not scroll under the menu
            event.preventDefault();
            move_active(menu, 1);
            return;
        }

        if (event.key === 'ArrowUp') {
            event.preventDefault();
            move_active(menu, -1);
            return;
        }

        if (event.key === 'Enter') {
            // The trigger stands inside a form - Enter must not submit it
            event.preventDefault();
            var active = menu.querySelector('.' + active_row_class);

            if (active) {
                active.click();
            }

            return;
        }

        if (event.key === 'Escape') {
            var filter_input = menu.querySelector('.dashboard-select-filter');

            // A filter with text in it is what Escape clears first ..
            if (filter_input && filter_input.value !== '') {
                filter_input.value = '';

                // .. and the rows are rebuilt the same way typing rebuilds them
                filter_input.dispatchEvent(new Event('input'));
                return;
            }

            ns.select.hide_menu();
        }
    });
})();
