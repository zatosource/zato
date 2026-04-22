
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.pagination = {};

    kit.pagination.init = function(config) {
        var current_page = 1;
        var page_size = config.page_size || 50;
        var data = config.data || [];

        function total_pages() {
            return Math.ceil(data.length / page_size) || 1;
        }

        function render() {
            var start = (current_page - 1) * page_size;
            var page_data = data.slice(start, start + page_size);
            var $body = $(config.table_body);
            $body.empty();
            for (var i = 0; i < page_data.length; i++) {
                $body.append(config.render_row(page_data[i], start + i));
            }
            render_controls(config.container_top);
            render_controls(config.container_bottom);
            if (typeof config.on_page_change === 'function') {
                config.on_page_change(current_page, total_pages());
            }
        }

        function render_controls(selector) {
            if (!selector) return;
            var $c = $(selector);
            if ($c.length === 0) return;
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
                ' \u00b7 ' + kit.format_number_full(data.length) + ' total</span>';
            if (current_page < tp) {
                html += ' <a href="#" class="detail-page-next">Next</a>';
            }
            $c.html(html);
            $c.find('.detail-page-prev').on('click', function(e) {
                e.preventDefault();
                go(current_page - 1);
            });
            $c.find('.detail-page-next').on('click', function(e) {
                e.preventDefault();
                go(current_page + 1);
            });
        }

        function go(page) {
            if (page < 1) page = 1;
            if (page > total_pages()) page = total_pages();
            current_page = page;
            render();
        }

        render();

        return {
            go: go,
            refresh: function(new_data) {
                data = new_data;
                current_page = 1;
                render();
            },
            current_page: function() { return current_page; },
            total_pages: total_pages
        };
    };
})();
