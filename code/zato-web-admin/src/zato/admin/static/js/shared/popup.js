// The shared popup machinery - dragging, resizing and the header grip
// glyph, used by the IDE's right-click document menus and by the wizard
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

// The corner glyph both resize grips wear - two diagonal strokes drawn into
// the corner. The left grip is the same picture mirrored, which popup.css
// does, so one icon covers both.
$.fn.zato.popup.resize_icon =
    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" ' +
    'stroke-width="1.4" stroke-linecap="round">' +
    '<line x1="11" y1="4" x2="4" y2="11"></line>' +
    '<line x1="11" y1="8" x2="8" y2="11"></line></svg>';

// ////////////////////////////////////////////////////////////////////////

// Puts a resize grip in each bottom corner of a popup. A corner follows the
// pointer while the two edges it does not touch stay exactly where they are,
// so resizing by the left corner keeps the right edge in place and the other
// way round. The popup has to be positioned for this, which every popup is.
//
// options:
//   min_width, min_height - how small a popup may be dragged
$.fn.zato.popup.install_resize = function(popup, options) {

    $.fn.zato.popup._install_grip(popup, options, 'left');
    $.fn.zato.popup._install_grip(popup, options, 'right');
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.popup._install_grip = function(popup, options, side) {

    var grip = $('<span>').addClass('zato-popup-grip zato-popup-grip-' + side);
    grip.html($.fn.zato.popup.resize_icon);
    $(popup).append(grip);

    grip.on('mousedown', function(event) {

        event.preventDefault();

        // A press inside a popup is the popup's own - whatever closes it on
        // an outside press must not see this one
        event.stopPropagation();

        var grab_x = event.pageX;
        var grab_y = event.pageY;

        var start_left = popup.offsetLeft;
        var start_width = popup.offsetWidth;
        var start_height = popup.offsetHeight;

        // The right edge is what the left corner is measured against, since
        // that edge is the one standing still while the corner travels
        var right_edge = start_left + start_width;

        // The pointer spends the drag outside the grip, so the cursor is
        // held for the whole page instead of only for the corner
        $(document.documentElement).addClass('zato-popup-resizing-' + side);

        $(document).on('mousemove.zato-popup-resize', function(move) {

            popup.style.height = Math.max(start_height + move.pageY - grab_y, options.min_height) + 'px';

            if(side === 'right') {
                popup.style.width = Math.max(start_width + move.pageX - grab_x, options.min_width) + 'px';
                return;
            }

            // Past the minimum the left edge stops instead of pushing the
            // right one, which is what keeps the far edge where it was
            var left = Math.min(start_left + move.pageX - grab_x, right_edge - options.min_width);

            popup.style.left = left + 'px';
            popup.style.width = (right_edge - left) + 'px';
        });

        $(document).on('mouseup.zato-popup-resize', function() {

            $(document.documentElement).removeClass('zato-popup-resizing-' + side);
            $(document).off('mousemove.zato-popup-resize');
            $(document).off('mouseup.zato-popup-resize');
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
