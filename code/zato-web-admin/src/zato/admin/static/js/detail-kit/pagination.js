
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.pagination = {};

    kit.pagination.init = function(config) {
        var poll_url = config.poll_url;
        var object_type = config.object_type;
        var object_id = config.object_id;
        var page_size = config.page_size || 50;
        var $body = $(config.table_body);
        var csrf_token = config.csrf_token || $.cookie('csrftoken');
        var render_page = config.render_page;
        var render_new = config.render_new;
        var on_page_change = config.on_page_change;
        var ts_field = config.ts_field || 'actual_fire_time_iso';

        var current_page = 1;
        var total_count = 0;
        var last_ts = '';

        function total_pages() {
            return Math.ceil(total_count / page_size) || 1;
        }

        function render_controls(selector) {
            var $c = $(selector);
            if (!$c.length) return;
            var tp = total_pages();
            if (tp <= 1) {
                $c.empty();
                return;
            }
            var html = '';
            if (current_page > 1) {
                html += '<a href="#" class="detail-page-prev">Previous</a> ';
            }
            html += '<span class="detail-pagination-info">Page ' +
                kit.format_number_full(current_page) + ' of ' +
                kit.format_number_full(tp) +
                ' \u00b7 ' + kit.format_number_full(total_count) + ' total</span>';
            if (current_page < tp) {
                html += ' <a href="#" class="detail-page-next">Next</a>';
            }
            $c.html(html);
            $c.find('.detail-page-prev').on('click', function(e) {
                e.preventDefault();
                fetch_page(current_page - 1);
            });
            $c.find('.detail-page-next').on('click', function(e) {
                e.preventDefault();
                fetch_page(current_page + 1);
            });
        }

        function update_controls() {
            render_controls(config.container_top);
            render_controls(config.container_bottom);
        }

        function update_last_ts(rows) {
            for (var i = 0; i < rows.length; i++) {
                var ts = rows[i][ts_field] || '';
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
                data: {
                    object_type: object_type,
                    id: object_id,
                    page: page,
                    page_size: page_size
                },
                headers: {'X-CSRFToken': csrf_token},
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    var rows = data.rows || [];
                    total_count = data.total || 0;
                    current_page = data.page || page;

                    render_page($body, rows);

                    update_last_ts(rows);
                    update_controls();

                    if (typeof on_page_change === 'function') {
                        on_page_change(current_page, total_pages());
                    }
                }
            });
        }

        function poll_new() {
            if (!last_ts) return;
            if (current_page !== 1) return;

            $.ajax({
                url: poll_url,
                type: 'POST',
                data: {
                    object_type: object_type,
                    id: object_id,
                    since_ts: last_ts
                },
                headers: {'X-CSRFToken': csrf_token},
                success: function(data) {
                    if (typeof data === 'string') {
                        data = JSON.parse(data);
                    }
                    var rows = data.rows || [];
                    if (rows.length === 0) return;

                    update_last_ts(rows);
                    total_count += rows.length;

                    render_new($body, rows, page_size);

                    update_controls();
                }
            });
        }

        fetch_page(1);

        return {
            fetch_page: fetch_page,
            poll_new: poll_new,
            current_page: function() { return current_page; },
            total_pages: total_pages,
            get_last_ts: function() { return last_ts; },
            destroy: function() {}
        };
    };
})();
