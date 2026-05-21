
// ////////////////////////////////////////////////////////////////////////

(function($) {

    var kit = $.fn.zato.dashboard_kit;
    kit.preview_overlay = {};

    var _$overlay = null;
    var _raw_text = '';

// ////////////////////////////////////////////////////////////////////////

    function _escape_html(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

// ////////////////////////////////////////////////////////////////////////

    function _update_gutter($pre, $gutter) {
        var text = $pre.text();
        if (!text) {
            $gutter.html('');
            return;
        }
        var count = text.split('\n').length;
        var lines = [];
        for (var i = 1; i <= count; i++) {
            lines.push(i + ' ');
        }
        $gutter.html(lines.join('\n'));
    }

// ////////////////////////////////////////////////////////////////////////

    function _highlight($pre, $gutter, text) {
        var escaped = _escape_html(text);
        $pre.html(escaped);
        $pre.addClass('syntax-monokai');
        _update_gutter($pre, $gutter);

        $.ajax({
            type: 'POST',
            url: '/zato/highlight/',
            data: {text: text},
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            dataType: 'json',
            success: function(data) {
                $pre.html(data.html);
                $pre.addClass('syntax-monokai');
                _update_gutter($pre, $gutter);
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
                        '<div class="kit-overlay-actions">' +
                            '<a class="kit-overlay-action-link" id="kit-overlay-copy" href="javascript:void(0)">Copy</a>' +
                            '<span id="kit-overlay-save-sep">|</span>' +
                            '<a class="kit-overlay-action-link" id="kit-overlay-save" href="javascript:void(0)">Save</a>' +
                        '</div>' +
                        '<div class="kit-overlay-response-wrap">' +
                            '<div class="kit-overlay-gutter" id="kit-overlay-gutter"></div>' +
                            '<pre class="kit-overlay-pre" id="kit-overlay-pre"></pre>' +
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

        $('#kit-overlay-copy').on('click', function() {
            var link = this;
            navigator.clipboard.writeText(_raw_text).then(function() {
                kit.flash_tooltip(link, 'Copied to clipboard');
            });
        });

        $('#kit-overlay-save').on('click', function() {
            var filename = _$overlay.data('save-filename');
            var blob = new Blob([_raw_text], {type: 'text/plain;charset=utf-8'});
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
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

        _raw_text = config.text;

        $('#kit-overlay-title').text(config.title);

        var show_save = config.show_save !== false;
        $('#kit-overlay-save').toggle(show_save);
        $('#kit-overlay-save-sep').toggle(show_save);

        if (show_save && config.save_filename) {
            _$overlay.data('save-filename', config.save_filename);
        }

        var $content = _$overlay.find('.kit-overlay-content');
        $content.css({position: '', margin: '', left: '', top: '', transform: ''});

        _$overlay.removeClass('hidden');

        var $pre = $('#kit-overlay-pre');
        var $gutter = $('#kit-overlay-gutter');
        _highlight($pre, $gutter, _raw_text);
    };

// ////////////////////////////////////////////////////////////////////////

    kit.preview_overlay.close = function() {
        if (_$overlay) {
            _$overlay.addClass('hidden');
        }
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
