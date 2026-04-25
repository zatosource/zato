
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.arena === 'undefined') { $.fn.zato.arena = {}; }
if (typeof $.fn.zato.arena.logs === 'undefined') { $.fn.zato.arena.logs = {}; }

$.fn.zato.arena.logs.series = {

    load: function(entry_id) {
        $.ajax({
            url: $.fn.zato.arena.logs.config.urls.series,
            type: 'POST',
            data: {series_id: entry_id},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                $.fn.zato.arena.logs.series.render(data);
            }
        });
    },

    render: function(entries) {
        var $container = $('#arena-series');
        $container.empty();

        if (!entries || entries.length === 0) {
            $container.html('<div class="arena-no-results">No series entries</div>');
            return;
        }

        var $tree = $('<ul class="arena-series-tree"></ul>');

        for (var idx = 0; idx < entries.length; idx++) {
            var entry = entries[idx];
            var indent = entry.depth * 20;
            var $item = $('<li class="arena-series-entry" style="padding-left: ' + indent + 'px"></li>');

            var label = '#' + entry.entry_id;
            if (entry.attrs && entry.attrs.message) {
                label = label + ' - ' + entry.attrs.message;
            }

            var $link = $('<a href="#" class="arena-entry-link" data-entry-id="' + entry.entry_id + '">' + label + '</a>');
            $item.append($link);

            // Expand/collapse for children
            var $expand = $('<a href="#" class="arena-expand-link" data-entry-id="' + entry.entry_id + '"> [+]</a>');
            $item.append($expand);

            $tree.append($item);
        }

        $container.append($tree);

        $container.find('.arena-entry-link').on('click', function(event) {
            event.preventDefault();
            var target_entry_id = $(this).data('entry-id');
            $.fn.zato.arena.logs.results.load_detail(target_entry_id);
        });

        $container.find('.arena-expand-link').on('click', function(event) {
            event.preventDefault();
            var target_entry_id = $(this).data('entry-id');
            $.fn.zato.arena.logs.series.load_children(target_entry_id, $(this).parent());
        });
    },

    load_children: function(entry_id, $parent_item) {
        $.ajax({
            url: $.fn.zato.arena.logs.config.urls.children,
            type: 'POST',
            data: {entry_id: entry_id},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (data && data.length > 0) {
                    var $sub = $('<ul class="arena-children-list"></ul>');
                    for (var idx = 0; idx < data.length; idx++) {
                        var child = data[idx];
                        var label = '#' + child.entry_id;
                        if (child.attrs && child.attrs.message) {
                            label = label + ' - ' + child.attrs.message;
                        }
                        $sub.append('<li><a href="#" class="arena-entry-link" data-entry-id="' + child.entry_id + '">' + label + '</a></li>');
                    }
                    $parent_item.append($sub);
                }
            }
        });
    }
};
