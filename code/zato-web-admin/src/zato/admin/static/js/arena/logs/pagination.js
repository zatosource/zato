
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.arena === 'undefined') { $.fn.zato.arena = {}; }
if (typeof $.fn.zato.arena.logs === 'undefined') { $.fn.zato.arena.logs = {}; }

$.fn.zato.arena.logs.pagination = {

    update: function(total, offset, limit) {
        var $container = $('#arena-pagination');
        $container.empty();

        if (total === 0) {
            return;
        }

        var current_page = Math.floor(offset / limit) + 1;
        var total_pages = Math.ceil(total / limit);

        var $info = $('<span class="arena-page-info">Page ' + current_page + ' of ' + total_pages + ' (' + total + ' results)</span>');
        $container.append($info);

        if (offset > 0) {
            var $prev = $('<button class="arena-page-prev">Previous</button>');
            $prev.on('click', function() {
                $.fn.zato.arena.logs.search.prev_page();
            });
            $container.append($prev);
        }

        if (offset + limit < total) {
            var $next = $('<button class="arena-page-next">Next</button>');
            $next.on('click', function() {
                $.fn.zato.arena.logs.search.next_page();
            });
            $container.append($next);
        }

        // Page size selector
        var page_sizes = $.fn.zato.arena.logs.config.pagination.page_sizes;
        var $select = $('<select class="arena-page-size"></select>');
        for (var idx = 0; idx < page_sizes.length; idx++) {
            var size = page_sizes[idx];
            var selected = (size === limit) ? ' selected' : '';
            $select.append('<option value="' + size + '"' + selected + '>' + size + ' per page</option>');
        }
        $select.on('change', function() {
            $.fn.zato.arena.logs.search.set_page_size(parseInt($(this).val()));
        });
        $container.append($select);
    }
};
