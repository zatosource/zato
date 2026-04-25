
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.arena === 'undefined') { $.fn.zato.arena = {}; }
if (typeof $.fn.zato.arena.logs === 'undefined') { $.fn.zato.arena.logs = {}; }

$.fn.zato.arena.logs.results = {

    render: function(data) {
        var $container = $('#arena-results');
        $container.empty();

        if (!data.entries || data.entries.length === 0) {
            $container.html('<div class="arena-no-results">No results found</div>');
            return;
        }

        var $table = $('<table class="arena-results-table"></table>');
        var $thead = $('<thead><tr><th>ID</th><th>Score</th><th>Series</th><th>Depth</th><th>Actions</th></tr></thead>');
        $table.append($thead);

        var $tbody = $('<tbody></tbody>');

        for (var idx = 0; idx < data.entries.length; idx++) {
            var entry = data.entries[idx];
            var entry_id = entry[0];
            var score = entry[1];

            var $row = $('<tr></tr>');
            $row.append('<td>' + entry_id + '</td>');
            $row.append('<td>' + score.toFixed(2) + '</td>');
            $row.append('<td><a href="#" class="arena-series-link" data-entry-id="' + entry_id + '">View series</a></td>');
            $row.append('<td></td>');
            $row.append('<td><a href="#" class="arena-detail-link" data-entry-id="' + entry_id + '">Detail</a></td>');
            $tbody.append($row);
        }

        $table.append($tbody);
        $container.append($table);

        $container.find('.arena-detail-link').on('click', function(event) {
            event.preventDefault();
            var target_entry_id = $(this).data('entry-id');
            $.fn.zato.arena.logs.results.load_detail(target_entry_id);
        });

        $container.find('.arena-series-link').on('click', function(event) {
            event.preventDefault();
            var target_entry_id = $(this).data('entry-id');
            $.fn.zato.arena.logs.series.load(target_entry_id);
        });
    },

    load_detail: function(entry_id) {
        $.ajax({
            url: $.fn.zato.arena.logs.config.urls.get,
            type: 'POST',
            data: {entry_id: entry_id},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                $.fn.zato.arena.logs.results.render_detail(data);
            }
        });
    },

    render_detail: function(entry) {
        var $detail = $('#arena-detail');
        $detail.empty();

        if (!entry) {
            $detail.html('<div class="arena-no-results">Entry not found</div>');
            return;
        }

        var $dl = $('<dl class="arena-detail-list"></dl>');
        $dl.append('<dt>Entry ID</dt><dd>' + entry.entry_id + '</dd>');
        $dl.append('<dt>Parent ID</dt><dd>' + entry.parent_id + '</dd>');
        $dl.append('<dt>Series ID</dt><dd>' + entry.series_id + '</dd>');
        $dl.append('<dt>Depth</dt><dd>' + entry.depth + '</dd>');

        if (entry.attrs) {
            var attr_keys = Object.keys(entry.attrs).sort();
            for (var attr_idx = 0; attr_idx < attr_keys.length; attr_idx++) {
                var attr_key = attr_keys[attr_idx];
                $dl.append('<dt>' + attr_key + '</dt><dd>' + JSON.stringify(entry.attrs[attr_key]) + '</dd>');
            }
        }

        $detail.append($dl);
    }
};
