// Copying to the clipboard, confirmed where it was asked for - the tooltip is the
// one common.js shows, put either beside the button or above it, and it goes away
// on its own so nothing has to be dismissed.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy.config = {

    // What the confirmation says when the caller has nothing more particular to say, and how
    // long it stays on screen
    confirmation: 'Copied to clipboard',
    confirmationShownMS: 600,

    // How far from the element the confirmation stands, which is tippy's own offset -
    // along the element's side first, away from it second
    offset: [0, 10]
};

// ////////////////////////////////////////////////////////////////////////

// Puts the text on the clipboard and says so beside the element that was pressed.
// The placement is tippy's, so 'left' and 'top' read as they do everywhere else, and so
// is the offset, which is how close to the element the confirmation stands. The element
// needs an id of its own, since that is what the tooltip is anchored by. A caller with
// something more particular to say than that a copy was taken says it as the message.
$.fn.zato.copy.to_clipboard = function(elem, text, placement, offset, message) {

    navigator.clipboard.writeText(text);
    $.fn.zato.copy.confirm(elem, placement, offset, message);
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.copy.confirm = function(elem, placement, offset, message) {

    var config = $.fn.zato.copy.config;

    if(message === undefined) {
        message = config.confirmation;
    }

    // A confirmation from a moment ago may still be on screen, and one element
    // holds one tooltip at a time - a second one for the same element is refused,
    // so the previous one goes first
    if(elem._tippy) {
        elem._tippy.destroy();
    }

    // The tooltip is asked for by selector, which is what common.js takes
    $.fn.zato.show_tooltip_common(placement, '#' + elem.id, message, false);

    // How far it stands from the element is the caller's to say, and common.js shows it
    // at tippy's own distance, so that is set on the tooltip it has just made
    elem._tippy.setProps({offset: offset});

    setTimeout(function() {

        if(elem._tippy) {
            elem._tippy.destroy();
        }

    }, config.confirmationShownMS);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
