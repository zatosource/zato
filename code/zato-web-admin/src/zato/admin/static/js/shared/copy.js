// Copying to the clipboard, confirmed where it was asked for - the tooltip is the
// one common.js shows, put either beside the button or above it, and it goes away
// on its own so nothing has to be dismissed.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy.config = {

    // What the confirmation says and how long it stays on screen
    confirmation: 'Copied to clipboard',
    confirmationShownMS: 600
};

// ////////////////////////////////////////////////////////////////////////

// Puts the text on the clipboard and says so beside the element that was pressed.
// The placement is tippy's, so 'left' and 'top' read as they do everywhere else.
// The element needs an id of its own, since that is what the tooltip is anchored by.
$.fn.zato.copy.to_clipboard = function(elem, text, placement) {

    navigator.clipboard.writeText(text);
    $.fn.zato.copy.confirm(elem, placement);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy.confirm = function(elem, placement) {

    var config = $.fn.zato.copy.config;

    // A confirmation from a moment ago may still be on screen, and one element
    // holds one tooltip at a time - a second one for the same element is refused,
    // so the previous one goes first
    if(elem._tippy) {
        elem._tippy.destroy();
    }

    // The tooltip is asked for by selector, which is what common.js takes
    $.fn.zato.show_tooltip_common(placement, '#' + elem.id, config.confirmation, false);

    setTimeout(function() {

        if(elem._tippy) {
            elem._tippy.destroy();
        }

    }, config.confirmationShownMS);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
