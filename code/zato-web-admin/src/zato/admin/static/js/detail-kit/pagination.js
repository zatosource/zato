
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.pagination = {};

    kit.pagination.init = function(config) {
        var poll_url = config.poll_url;
        var action = config.action;
        var object_id = config.object_id;
        var page_size = config.page_size;
        var filters = config.filters;
        var $body = $(config.table_body);
        function csrf_token() { return $.cookie('csrftoken'); }
        var render_page = config.render_page;
        var render_new = config.render_new;
        var on_page_change = config.on_page_change;
        var ts_field = config.ts_field;
        var on_new_rows = config.on_new_rows;
        var get_active_items = config.get_active_items;
        var active_items_field = config.active_items_field;

        var current_page = 1;
        var total_count = 0;
        var last_ts = '';
        var show_all = false;

        function build_request(extra) {
            var data = {action: action, id: object_id};
            for (var fk in filters) {
                data[fk] = filters[fk];
            }
            for (var ek in extra) {
                data[ek] = extra[ek];
            }
            return data;
        }

        function total_pages() {
            return Math.ceil(total_count / page_size) || 1;
        }

        function render_controls(selector) {
            var $c = $(selector);
            if (!$c.length) return;

            if (show_all) {
                var html = '<span class="detail-pagination-row">';
                html += '<span class="detail-pagination-info">' +
                    kit.format_number_full(total_count) + ' total</span>';
                html += '<span class="detail-page-sep">|</span><a href="#" class="detail-page-paginate">Paginate</a>';
                html += '</span>';
                $c.html(html);
                $c.find('a.detail-page-paginate').on('click', function(e) {
                    e.preventDefault();
                    show_all = false;
                    fetch_page(1);
                });
                return;
            }

            var tp = total_pages();
            var has_prev = current_page > 1;
            var has_next = current_page < tp;
            var is_empty = total_count === 0;

            var html = '<span class="detail-pagination-row">';
            if (has_prev) {
                html += '<a href="#" class="detail-page-prev">Previous</a>';
            } else {
                html += '<span class="detail-page-prev detail-page-disabled">Previous</span>';
            }
            if (is_empty) {
                html += '<span class="detail-pagination-info"><span class="detail-page-disabled">Page ' +
                    kit.format_number_full(current_page) + ' of ' +
                    kit.format_number_full(tp) + '</span>' +
                    ' \u00b7 ' + kit.format_number_full(total_count) + ' total</span>';
            } else {
                html += '<span class="detail-pagination-info">Page ' +
                    kit.format_number_full(current_page) + ' of ' +
                    kit.format_number_full(tp) +
                    ' \u00b7 ' + kit.format_number_full(total_count) + ' total</span>';
            }
            if (has_next) {
                html += '<a href="#" class="detail-page-next">Next</a>';
            } else {
                html += '<span class="detail-page-next detail-page-disabled">Next</span>';
            }
            if (is_empty) {
                html += '<span class="detail-page-sep">|</span><span class="detail-page-disabled">Show all</span>';
            } else {
                html += '<span class="detail-page-sep">|</span><a href="#" class="detail-page-show-all">Show all</a>';
            }
            html += '</span>';

            $c.html(html);
            $c.find('a.detail-page-prev').on('click', function(e) {
                e.preventDefault();
                fetch_page(current_page - 1);
            });
            $c.find('a.detail-page-next').on('click', function(e) {
                e.preventDefault();
                fetch_page(current_page + 1);
            });
            $c.find('a.detail-page-show-all').on('click', function(e) {
                e.preventDefault();
                show_all = true;
                fetch_all();
            });
        }

        function update_controls() {
            render_controls(config.container_top);
            render_controls(config.container_bottom);
        }

        function update_last_ts(rows) {
            for (var i = 0; i < rows.length; i++) {
                var ts = rows[i][ts_field];
                if (ts > last_ts) {
                    last_ts = ts;
                }
            }
        }

        function fetch_page(page) {
            if (page < 1) page = 1;
            if (total_count > 0 && page > total_pages()) page = total_pages();
            current_page = page;

            $.ajax({
                url: poll_url,
                type: 'POST',
                data: JSON.stringify(build_request({page: page, page_size: page_size})),
                contentType: 'application/json',
                headers: {'X-CSRFToken': csrf_token()},
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    var rows = data.rows;
                    total_count = data.total;
                    current_page = data.page;

                    render_page($body, rows, total_count);

                    update_last_ts(rows);
                    update_controls();

                    // .. keep the URL in sync with the current page ..
                    var urlParams = new URLSearchParams(window.location.search);
                    urlParams.set('page', current_page);
                    history.replaceState(null, '', '?' + urlParams.toString());

                    if (typeof on_page_change === 'function') {
                        on_page_change(current_page, total_pages());
                    }
                }
            });
        }

        function fetch_all() {
            $.ajax({
                url: poll_url,
                type: 'POST',
                data: JSON.stringify(build_request({page: 1, page_size: 100000})),
                contentType: 'application/json',
                headers: {'X-CSRFToken': csrf_token()},
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    var rows = data.rows;
                    total_count = data.total;
                    render_page($body, rows);
                    update_last_ts(rows);
                    update_controls();
                }
            });
        }

        function poll_new() {
            if (!last_ts) {
                fetch_page(1);
                return;
            }
            if (!show_all && current_page !== 1) return;

            var poll_extra = {since_ts: last_ts};
            if (get_active_items) {
                var active = get_active_items();
                if (active.length > 0) {
                    poll_extra[active_items_field] = active;
                }
            }
            $.ajax({
                url: poll_url,
                type: 'POST',
                data: JSON.stringify(build_request(poll_extra)),
                contentType: 'application/json',
                headers: {'X-CSRFToken': csrf_token()},
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    var rows = data.rows;
                    if (rows.length === 0) return;

                    update_last_ts(rows);
                    total_count = data.total;

                    render_new($body, rows, show_all ? Infinity : page_size);

                    update_controls();

                    if (on_new_rows) {
                        on_new_rows(rows, total_count);
                    }
                }
            });
        }

        function set_filters(new_filters) {
            for (var key in new_filters) {
                filters[key] = new_filters[key];
            }
        }

        if (config.initial_data) {
            var initialRows = config.initial_data.rows;
            total_count = config.initial_data.total;
            current_page = config.initial_data.page;
            render_page($body, initialRows, total_count);
            update_last_ts(initialRows);
            update_controls();
        } else {
            fetch_page(1);
        }

        // Bind filter tabs if configured ..
        // .. config.filter_tabs = {selector: '.dashboard-tab[data-state]', filter_key: 'state', url_key: 'state'}
        if (config.filter_tabs) {
            var filterTabConfig = config.filter_tabs;
            $(filterTabConfig.selector).on('click', function() {
                var newValue = $(this).data(filterTabConfig.filter_key);
                var updatePayload = {};
                updatePayload[filterTabConfig.filter_key] = newValue;

                // .. update active tab styling ..
                $(filterTabConfig.selector).removeClass('dashboard-tab-active').attr('aria-selected', 'false');
                $(this).addClass('dashboard-tab-active').attr('aria-selected', 'true');

                // .. update filters and re-fetch page 1 ..
                set_filters(updatePayload);
                fetch_page(1);

                // .. and update the URL without reload.
                var urlParams = new URLSearchParams(window.location.search);
                urlParams.set(filterTabConfig.url_key, newValue);
                history.replaceState(null, '', '?' + urlParams.toString());
            });
        }

        return {
            fetch_page: fetch_page,
            poll_new: poll_new,
            set_filters: set_filters,
            current_page: function() { return current_page; },
            total_pages: total_pages,
            get_last_ts: function() { return last_ts; },
            destroy: function() {}
        };
    };
})();
