
// ////////////////////////////////////////////////////////////////////////

(function($) {

    $.namespace('zato.ui_helpers');

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.esc_html = function(text) {
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.flash_tooltip = function(element, message) {
        var tip = tippy(element, {
            content: message,
            trigger: 'manual',
            placement: 'top',
            duration: [100, 100]
        });
        tip.show();
        setTimeout(function() { tip.hide(); tip.destroy(); }, 600);
    };

// ////////////////////////////////////////////////////////////////////////

    $.fn.zato.ui_helpers.copy_to_clipboard = function(element, text) {
        navigator.clipboard.writeText(text).then(function() {
            $.fn.zato.ui_helpers.flash_tooltip(element, 'Copied to clipboard');
        });
    };

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
