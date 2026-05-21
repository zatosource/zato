
// ////////////////////////////////////////////////////////////////////////

(function($) {

    var kit = $.fn.zato.dashboard_kit;
    kit.preview_overlay = {};

    var _$overlay = null;
    var _config = null;

// ////////////////////////////////////////////////////////////////////////

    function _escape_html(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

// ////////////////////////////////////////////////////////////////////////

    function _sync_highlight() {
        var text = $('#kit-overlay-textarea').val();
        var $layer = $('#kit-overlay-highlight');

        $layer[0].innerHTML = _escape_html(text + '\n');

        $.ajax({
            type: 'POST',
            url: '/zato/highlight/',
            data: {text: text},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            dataType: 'json',
            success: function(data) {
                $layer[0].innerHTML = data.html;
            }
        });
    }

// ////////////////////////////////////////////////////////////////////////

    function _make_draggable($overlay) {
        var is_dragging = false;
        var offset_x = 0;
        var offset_y = 0;
        var $content = $overlay.find('.kit-overlay-content');
        var $header = $overlay.find('.kit-overlay-header');

        $header.on('mousedown.kit_overlay', function(e) {
            if ($(e.target).is('button, input, a')) return;
            is_dragging = true;
            var rect = $content[0].getBoundingClientRect();
            offset_x = e.clientX - rect.left;
            offset_y = e.clientY - rect.top;
            $content.css({position: 'fixed', margin: '0', left: rect.left + 'px', top: rect.top + 'px', transform: 'none'});
            e.preventDefault();
        });

        $(document).on('mousemove.kit_overlay', function(e) {
            if (!is_dragging) return;
            $content.css({left: (e.clientX - offset_x) + 'px', top: (e.clientY - offset_y) + 'px'});
        });

        $(document).on('mouseup.kit_overlay', function() {
            is_dragging = false;
        });
    }

// ////////////////////////////////////////////////////////////////////////

    function _build_dom() {
        var html = '' +
            '<div class="kit-overlay hidden" id="kit-preview-overlay">' +
                '<div class="kit-overlay-backdrop"></div>' +
                '<div class="kit-overlay-content">' +
                    '<div class="kit-overlay-header">' +
                        '<h2 id="kit-overlay-title"></h2>' +
                        '<button class="kit-overlay-close-btn">\u00d7</button>' +
                    '</div>' +
                    '<div class="kit-overlay-body">' +
                        '<div class="kit-overlay-editor">' +
                            '<textarea id="kit-overlay-textarea" class="kit-overlay-textarea" spellcheck="false"></textarea>' +
                            '<pre id="kit-overlay-highlight" class="kit-overlay-highlight syntax-monokai"></pre>' +
                        '</div>' +
                        '<div class="kit-overlay-footer">' +
                            '<button class="record-edit-action-button" id="kit-overlay-copy" type="button">Copy</button>' +
                            '<button class="record-edit-action-button" id="kit-overlay-save" type="button">Save</button>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>';

        _$overlay = $(html);
        $('body').append(_$overlay);

        _$overlay.find('.kit-overlay-backdrop').on('click', function() {
            kit.preview_overlay.close();
        });

        _$overlay.find('.kit-overlay-close-btn').on('click', function() {
            kit.preview_overlay.close();
        });

        $('#kit-overlay-textarea').on('input', _sync_highlight);

        $('#kit-overlay-textarea').on('scroll', function() {
            var layer = $('#kit-overlay-highlight')[0];
            layer.scrollTop = this.scrollTop;
            layer.scrollLeft = this.scrollLeft;
        });

        $('#kit-overlay-copy').on('click', function() {
            var text = $('#kit-overlay-textarea').val();
            var btn = this;
            navigator.clipboard.writeText(text).then(function() {
                kit.flash_tooltip(btn, 'Copied to clipboard');
            });
        });

        $('#kit-overlay-save').on('click', function() {
            var btn = this;
            var text = $('#kit-overlay-textarea').val();

            var payload = {
                action: _config.save_action,
                msg_id: _config.msg_id,
                topic_name: _config.topic_name,
                redis_stream_id: _config.redis_stream_id,
                data: text
            };

            $.ajax({
                type: 'POST',
                url: _config.poll_url,
                headers: {'X-CSRFToken': $.cookie('csrftoken')},
                data: JSON.stringify(payload),
                contentType: 'application/json',
                success: function() {
                    kit.flash_tooltip(btn, 'OK, saved');
                },
                error: function() {
                    kit.flash_tooltip(btn, 'Save failed');
                }
            });
        });

        $(document).on('keydown.kit_overlay', function(e) {
            if (e.key === 'Escape') {
                kit.preview_overlay.close();
            }
        });

        _make_draggable(_$overlay);
    }

// ////////////////////////////////////////////////////////////////////////

    kit.preview_overlay.open = function(config) {
        if (!_$overlay) {
            _build_dom();
        }

        _config = config;

        $('#kit-overlay-title').text(config.title);

        var $textarea = $('#kit-overlay-textarea');
        $textarea.val(config.text);

        var editable = config.editable !== false;
        $textarea.prop('readonly', !editable);

        var show_save = config.show_save !== false;
        $('#kit-overlay-save').toggle(show_save);

        var $content = _$overlay.find('.kit-overlay-content');
        $content.css({position: '', margin: '', left: '', top: '', transform: ''});

        _$overlay.removeClass('hidden');
        _sync_highlight();
    };

// ////////////////////////////////////////////////////////////////////////

    kit.preview_overlay.close = function() {
        if (_$overlay) {
            _$overlay.addClass('hidden');
        }
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
