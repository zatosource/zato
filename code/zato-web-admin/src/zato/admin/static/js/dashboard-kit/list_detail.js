

/* Dashboard kit - the list beside a detail pane.
   A scrolling list of items with one of them selected, and a pane showing that one whole.
   The arrow keys walk the list, the pane follows, and the two panes are dragged to whatever
   size the screen they are on wants - which is remembered under the key its caller passes in. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.list_detail = {};

    kit.list_detail.config = {

        // How wide the list may be pulled, and how much of the pane is kept no matter how wide
        // it is pulled. The list has no width it stops narrowing at - it gives its columns up
        // one at a time and then shuts altogether, the handle staying where it is to pull it
        // back open.
        max_list_width: 1400,
        min_pane_width: 320,

        // Narrower than this a list has room for nothing worth reading, so it is shut rather
        // than left standing as a strip of empty panel
        snap_shut_width: 110,

        // How far the pair may be dragged up and down
        min_height: 240,
        max_height: 1400,

        // What the two panes measure before anyone has dragged them
        default_list_width: 420,
        default_height: 560,

        selected_class: 'dashboard-list-detail-item-selected',
        closed_class: 'dashboard-list-detail-closed',

        list_width_property: '--dashboard-list-detail-list-width',
        height_property: '--dashboard-list-detail-height'
    };

    /* A width dragged on a wider window is not a width this one can hold, so whatever
       was stored is brought back into range rather than restored as it stands. */
    kit.list_detail._clamp_list_width = function(width, container_width) {
        var config = kit.list_detail.config;
        var max_width = config.max_list_width;

        // The pane keeps its own minimum whatever the window is worth.
        var room_left = container_width - config.min_pane_width;

        if (room_left < max_width) {
            max_width = room_left;
        }

        if (width > max_width) {
            width = max_width;
        }

        // A list too narrow to read anything in is shut all the way rather than left ajar,
        // which is also what keeps a drag past the left edge from going negative
        if (width < config.snap_shut_width) {
            width = 0;
        }

        return width;
    };

    kit.list_detail._clamp_height = function(height) {
        var config = kit.list_detail.config;

        if (height > config.max_height) {
            height = config.max_height;
        }

        if (height < config.min_height) {
            height = config.min_height;
        }

        return height;
    };

    /* The shape itself - the list, the handle that sets how wide it is, the pane,
       and under both of them the handle that sets how tall the pair is. A pair that takes
       the room the page has left gets no such handle: what it is tall enough for is the
       window, and dragging it past that is what a scrollbar comes of. */
    kit.list_detail._shape_html = function(config) {
        var html = '<div class="dashboard-list-detail">';

        html += '<div class="dashboard-list-detail-list">';
        html += config.list_html;
        html += '</div>';

        html += '<div class="dashboard-list-detail-handle-x" title="' + config.resize_hint + '"></div>';
        html += '<div class="dashboard-list-detail-pane"></div>';
        html += '</div>';

        if (!config.fit_height) {
            html += '<div class="dashboard-list-detail-handle-y" title="' + config.resize_hint + '"></div>';
        }

        return html;
    };

    /* config:
         host:          the element the two panes are built inside
         storage_key:   what the proportions of this screen are remembered under
         list_html:     the shell the items are rendered into, e.g. a table with its tbody
         items_host:    where inside that shell one item goes, the list itself when absent
         item_selector: what one item looks like to a click and to the arrow keys
         id_of:         the id of one item
         render_item:   one item as HTML, given the item and its position
         render_empty:  what stands in for the items when there are none
         render_detail: the selected item as HTML
         update_detail: brings a pane already holding one item to another, given the item
                        and the pane. Without it, every selection rebuilds the pane.
         empty_detail:  what the pane holds when there are items and none of them is selected
         no_items_detail: what it holds instead when there is nothing to select at all
         on_select:     called with the selected item once the pane holds it
         resize_hint:   the title the drag handles carry
         fit_height:    whether the pair takes the room the page has left below it, in place
                        of a height of its own that is dragged and remembered */
    kit.list_detail.create = function(config) {
        var kit_config = kit.list_detail.config;

        var $host = $(config.host);
        var items = [];
        var selected_id = null;

        // Whether the pane is already holding an item, which is what tells a pane that can
        // be brought to the next one apart from a pane that has to be built first
        var pane_is_built = false;

        if (config.resize_hint === undefined) {
            config.resize_hint = 'Drag to resize, double click to reset';
        }

        if (config.fit_height === undefined) {
            config.fit_height = false;
        }

        $host.html(kit.list_detail._shape_html(config));

        var $container = $host.find('.dashboard-list-detail');
        var $list = $container.find('.dashboard-list-detail-list');
        var $pane = $container.find('.dashboard-list-detail-pane');
        var $handle_x = $container.find('.dashboard-list-detail-handle-x');
        var $handle_y = $host.find('.dashboard-list-detail-handle-y');

        var $items_host = $list;

        if (config.items_host !== undefined) {
            $items_host = $list.find(config.items_host);
        }

        // ////////////////////////////////////////////////////////////////////
        // How wide the list is and how tall the pair is
        // ////////////////////////////////////////////////////////////////////

        // A screen whose list says more than most starts out wider than the kit's own default
        var default_list_width = kit_config.default_list_width;
        var default_height = kit_config.default_height;

        if (config.default_list_width !== undefined) {
            default_list_width = config.default_list_width;
        }

        if (config.default_height !== undefined) {
            default_height = config.default_height;
        }

        var list_width = default_list_width;
        var height = default_height;

        function apply_size() {
            $container[0].style.setProperty(kit_config.list_width_property, list_width + 'px');
            $container[0].style.setProperty(kit_config.height_property, height + 'px');

            // A list shut all the way is taken off the grid frame and all, rather than left as
            // a hairline of border between the handle and the pane
            $container.toggleClass(kit_config.closed_class, list_width === 0);
        }

        function store_size() {
            kit.storage_set_json(config.storage_key, {list_width: list_width, height: height});
        }

        function load_size() {
            var stored = kit.storage_get_json(config.storage_key);

            // A screen nobody has dragged yet takes the defaults the stylesheet would give it.
            if (stored === null) {
                return;
            }

            height = kit.list_detail._clamp_height(stored.height);

            // A list shut with the handle stays shut across a refresh like any other width
            // stays what it was dragged to - the handle is where it always is to pull it
            // back open
            list_width = kit.list_detail._clamp_list_width(stored.list_width, $container.width());
        }

        function reset_size() {
            list_width = default_list_width;
            height = default_height;

            apply_size();
            kit.storage_set_json(config.storage_key, null);
        }

        /* The pair sized to the page rather than to a number - whatever is drawn under it
           keeps its room and the pair takes everything else down to the foot of the window.
           It is all read off the layout in one pass, nothing being applied in between, so
           measuring never disturbs what is measured - which is what lets this be called
           every time anything on the page changes size. */
        function fit_to_page() {

            // A pair with a height of its own is left at whatever it was dragged to
            if (!config.fit_height) {
                return;
            }

            var pair_rect = $container[0].getBoundingClientRect();

            // The height property names the panes' content height, while on the screen each
            // pane also wears its padding and its frame - so the pair stands taller than the
            // property says by that much. How much is read off the pair as it is now, the
            // difference between what it measures and what the property last said.
            var wear = pair_rect.height - height;

            // Where the page's content really ends - the body's own edge plus the margin
            // under it, read off the layout rather than added up from stylesheets. It is the
            // body rather than the document that is asked, because the document never says
            // it is shorter than the window, and a page with room to spare is a pair to grow.
            var body_style = getComputedStyle(document.body);
            var content_bottom = document.body.getBoundingClientRect().bottom + parseFloat(body_style.marginBottom);

            var below = content_bottom - pair_rect.bottom;

            // Whole pixels only - the measurements carry fractions, and a fraction of a pixel
            // past the window is already a page that scrolls
            var new_height = Math.floor(window.innerHeight - pair_rect.top - below - wear);

            // A window too short for the pair's own minimum is one to scroll
            if (new_height < kit_config.min_height) {
                new_height = kit_config.min_height;
            }

            // A pair already the right size is left alone - which is also what stops the
            // observer below from being answered with the very change it watches for
            if (Math.abs(new_height - height) < 1) {
                return;
            }

            height = new_height;
            apply_size();
        }

        // A width dragged on this screen is kept whether the height is dragged or fitted
        load_size();
        apply_size();

        if (config.fit_height) {
            fit_to_page();

            // What stands above the pair arrives in its own time - a row of page links with
            // the first page of items, a legend with the chrome - and each arrival moves where
            // the pair begins. So the fit is not run at moments picked in advance: the body is
            // watched, and whenever anything on the page changes size the pair takes what room
            // is left again.
            new ResizeObserver(fit_to_page).observe(document.body);

            // A window pulled taller leaves the body the size it was, so that one the body's
            // observer never sees - the window says so itself
            $(window).on('resize.list_detail', fit_to_page);
        }

        // ////////////////////////////////////////////////////////////////////
        // Dragging the two panes to size
        // ////////////////////////////////////////////////////////////////////

        /* One drag - the pointer is followed until it is let go, and only then is
           the new pair written down, so a slow drag does not keep hitting storage. */
        function start_drag(event, on_move) {
            event.preventDefault();

            var start_x = event.pageX;
            var start_y = event.pageY;
            var start_width = list_width;
            var start_height = height;

            $('body').addClass('dashboard-list-detail-dragging');

            $(document).on('mousemove.list_detail', function(move_event) {
                on_move(move_event.pageX - start_x, move_event.pageY - start_y, start_width, start_height);
                apply_size();
            });

            $(document).on('mouseup.list_detail', function() {
                $(document).off('mousemove.list_detail mouseup.list_detail');
                $('body').removeClass('dashboard-list-detail-dragging');

                store_size();
            });
        }

        $handle_x.on('mousedown', function(event) {
            start_drag(event, function(delta_x, _delta_y, start_width) {
                list_width = kit.list_detail._clamp_list_width(start_width + delta_x, $container.width());
            });
        });

        $handle_y.on('mousedown', function(event) {
            start_drag(event, function(_delta_x, delta_y, _start_width, start_height) {
                height = kit.list_detail._clamp_height(start_height + delta_y);
            });
        });

        $handle_x.on('dblclick', reset_size);
        $handle_y.on('dblclick', reset_size);

        // ////////////////////////////////////////////////////////////////////
        // The selection
        // ////////////////////////////////////////////////////////////////////

        // An id read back off an element is text while an id read off an item may be a number,
        // so the two only ever meet as text.
        function id_text(item) {
            return String(config.id_of(item));
        }

        function index_of(item_id) {
            var out = -1;

            for (var item_index = 0; item_index < items.length; item_index++) {
                if (id_text(items[item_index]) === item_id) {
                    out = item_index;
                    break;
                }
            }

            return out;
        }

        function show_detail() {
            var item_index = index_of(selected_id);

            if (item_index === -1) {

                // A pane asking for a selection that cannot be made says the wrong thing
                var empty_html = config.empty_detail;

                if (items.length === 0) {
                    empty_html = config.no_items_detail;
                }

                $pane.html(empty_html);
                pane_is_built = false;
                return;
            }

            var item = items[item_index];

            // A pane already holding an item is brought to the next one where it stands,
            // so walking the list does not blank and rebuild the pane at every step.
            if (pane_is_built && config.update_detail !== undefined) {
                config.update_detail(item, $pane);
            }
            else {
                $pane.html(config.render_detail(item));
                pane_is_built = true;
            }

            config.on_select(item, $pane);
        }

        function mark_selected(scroll_into_view) {
            $items_host.find('.' + kit_config.selected_class).removeClass(kit_config.selected_class);

            var $item = $items_host.find('[data-item-id="' + selected_id + '"]');
            $item.addClass(kit_config.selected_class);

            if (scroll_into_view && $item.length) {
                $item[0].scrollIntoView({block: 'nearest'});
            }
        }

        function select(item_id, scroll_into_view) {
            selected_id = String(item_id);

            mark_selected(scroll_into_view);
            show_detail();
        }

        /* One step through the list, from wherever the selection stands now. */
        function move_by(step) {
            var item_index = index_of(selected_id) + step;

            if (item_index < 0) {
                item_index = 0;
            }

            if (item_index > items.length - 1) {
                item_index = items.length - 1;
            }

            if (items.length === 0) {
                return;
            }

            select(id_text(items[item_index]), true);
        }

        function move_to_end(is_last) {
            if (items.length === 0) {
                return;
            }

            var item_index = is_last ? items.length - 1 : 0;

            select(id_text(items[item_index]), true);
        }

        // ////////////////////////////////////////////////////////////////////
        // Drawing the list
        // ////////////////////////////////////////////////////////////////////

        function set_items(new_items) {
            items = new_items;

            var html = '';

            if (items.length === 0) {
                html = config.render_empty();
            }

            for (var item_index = 0; item_index < items.length; item_index++) {
                html += config.render_item(items[item_index], item_index);
            }

            $items_host.html(html);

            // A redraw of the same events keeps the one that was being read, and a redraw
            // that no longer has it falls back to the top of the list.
            if (index_of(selected_id) === -1) {
                selected_id = items.length ? id_text(items[0]) : null;
            }

            mark_selected(false);
            show_detail();
        }

        // ////////////////////////////////////////////////////////////////////

        $items_host.on('click', config.item_selector, function(event) {

            // A link or a button inside a row is what was clicked, not the row itself.
            if ($(event.target).closest('a, input, button').length) {
                return;
            }

            select($(this).attr('data-item-id'), false);
        });

        $(document).on('keydown.list_detail', function(event) {

            // Someone typing into the search box is not walking the list.
            if ($(event.target).is('input, textarea, select')) {
                return;
            }

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                move_by(1);
            }
            else if (event.key === 'ArrowUp') {
                event.preventDefault();
                move_by(-1);
            }
            else if (event.key === 'Home') {
                event.preventDefault();
                move_to_end(false);
            }
            else if (event.key === 'End') {
                event.preventDefault();
                move_to_end(true);
            }
        });

        return {
            set_items: set_items,
            select: function(item_id) { select(item_id, true); },
            selected: function() { return selected_id; },
            items_host: function() { return $items_host; },
            pane: function() { return $pane; }
        };
    };
})();
