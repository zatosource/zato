// The shared popup machinery - dragging and the header grip glyph,
// used by the IDE's right-click document menus and by the wizard
// popover micro-forms. The look lives in css/shared/popup.css.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.popup = {};

// ////////////////////////////////////////////////////////////////////////

// The grip glyph a popup header starts with - the visual cue that
// the header drags the popup around.
$.fn.zato.popup.build_grip = function() {
    var out = $('<span>').addClass('zato-popup-header-grip').text('\u2261');
    return out[0];
};

// ////////////////////////////////////////////////////////////////////////

// Lets a popup be dragged by the given handle. How a popup actually moves
// is up to the caller - on_start returns the popup's current origin and
// each on_move receives that origin shifted by however far the pointer
// has traveled since the press.
//
// options:
//   dragging_elem  - the element wearing the zato-popup-dragging class
//                    mid-drag, the handle when not given
//   should_ignore  - presses on these targets never start a drag
//   on_start(evt)  - called once per drag, returns {x, y} - the origin
//   on_move(x, y)  - applies one position
//   on_end(x, y)   - optional, runs when the button is released
$.fn.zato.popup.install_drag = function(handle, options) {

    var dragging_elem = options.dragging_elem || handle;

    $(handle).on('mousedown', function(event) {

        if(options.should_ignore && options.should_ignore(event.target)) {
            return;
        }

        event.preventDefault();

        var origin = options.on_start(event);
        var grab_x = event.pageX;
        var grab_y = event.pageY;

        var current_x = origin.x;
        var current_y = origin.y;

        $(dragging_elem).addClass('zato-popup-dragging');

        $(document).on('mousemove.zato-popup-drag', function(move) {
            current_x = origin.x + move.pageX - grab_x;
            current_y = origin.y + move.pageY - grab_y;
            options.on_move(current_x, current_y);
        });

        $(document).on('mouseup.zato-popup-drag', function() {

            $(dragging_elem).removeClass('zato-popup-dragging');
            $(document).off('mousemove.zato-popup-drag');
            $(document).off('mouseup.zato-popup-drag');

            if(options.on_end) {
                options.on_end(current_x, current_y);
            }
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
