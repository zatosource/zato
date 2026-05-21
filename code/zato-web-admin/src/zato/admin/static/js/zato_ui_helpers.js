
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.ui_helpers');

    var _labels = {
        copiedToClipboard: 'Copied to clipboard'
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.esc_html = function(text) {

        // Escape ampersands first ..
        var out = text.replace(/&/g, '&amp;');

        // .. then angle brackets ..
        out = out.replace(/</g, '&lt;');
        out = out.replace(/>/g, '&gt;');

        // .. and finally double quotes.
        out = out.replace(/"/g, '&quot;');

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    function _dismissTooltip(tip) {
        tip.hide();
        tip.destroy();
    }

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.flash_tooltip = function(element, message) {
        var tip = tippy(element, {
            content: message,
            trigger: 'manual',
            placement: 'top',
            duration: [100, 100],
            onShown: function(instance) {
                setTimeout(function() { _dismissTooltip(instance); }, 600);
            }
        });
        tip.show();
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.copy_to_clipboard = function(element, text) {
        navigator.clipboard.writeText(text).then(function() {
            $.fn.zato.ui_helpers.flash_tooltip(element, _labels.copiedToClipboard);
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
