
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.arena === 'undefined') { $.fn.zato.arena = {}; }
if (typeof $.fn.zato.arena.logs === 'undefined') { $.fn.zato.arena.logs = {}; }

$.fn.zato.arena.logs.search = {

    current_scope: null,
    current_offset: 0,
    current_limit: 50,
    current_input: '',

    init: function(scope) {
        this.current_scope = scope;
        this.current_limit = $.fn.zato.arena.logs.config.pagination.default_limit;

        var self = this;

        $('#arena-search-input').on('keypress', function(event) {
            if (event.which === 13) {
                self.execute(0);
            }
        });

        $('#arena-search-button').on('click', function() {
            self.execute(0);
        });
    },

    execute: function(offset) {
        var input = $('#arena-search-input').val();
        if (!input) {
            return;
        }

        this.current_input = input;
        this.current_offset = offset;

        var self = this;

        $.ajax({
            url: $.fn.zato.arena.logs.config.urls.search,
            type: 'POST',
            data: {
                scope: this.current_scope,
                input: input,
                offset: offset,
                limit: this.current_limit
            },
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                $.fn.zato.arena.logs.results.render(data);
                $.fn.zato.arena.logs.pagination.update(data.total, self.current_offset, self.current_limit);
            },
            error: function(xhr) {
                var err = 'Search failed';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    err = xhr.responseJSON.error;
                }
                $('#arena-results').html('<div class="arena-error">' + err + '</div>');
            }
        });
    },

    next_page: function() {
        this.execute(this.current_offset + this.current_limit);
    },

    prev_page: function() {
        var new_offset = this.current_offset - this.current_limit;
        if (new_offset < 0) {
            new_offset = 0;
        }
        this.execute(new_offset);
    },

    set_page_size: function(limit) {
        this.current_limit = limit;
        this.execute(0);
    }
};
