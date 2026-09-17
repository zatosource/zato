
// Dashboard kit - where the select's menu is placed and how the document drives it.
// Loaded after dashboard-kit/select.js, which holds the menu and the select.

(function() {
    var ns = $.fn.zato.dashboard_kit;
    var select = ns.select;

    // The drag handle of a popup the anchor may sit in, and the event a popup fires
    // on the document as it moves
    var dragHandleSelector = '.zato-popup-header';
    var popupMovedEvent = 'zato:popup-moved';

    // How far under its anchor the menu opens
    var menuGapPx = 2;

    // ////////////////////////////////////////////////////////////////////////

    // Puts the menu right under its anchor, wherever the anchor is now
    select.placeMenu = function(menu, anchor) {
        var rect = anchor.getBoundingClientRect();
        menu.style.top = (rect.bottom + menuGapPx) + 'px';
        menu.style.left = rect.left + 'px';
    };

    // ////////////////////////////////////////////////////////////////////////

    // A popup carrying the anchor has moved - the menu moves with it
    document.addEventListener(popupMovedEvent, function() {
        var menu = document.getElementById(select.menuId);
        var activeAnchor = select.activeAnchor();

        if (menu !== null) {
            if (activeAnchor !== null) {
                select.placeMenu(menu, activeAnchor);
            }
        }
    });

    // ////////////////////////////////////////////////////////////////////////

    // A press on a row picks it without taking focus from the anchor. The filter
    // box is the one thing in the menu that does take focus.
    document.addEventListener('mousedown', function(event) {
        var menu = document.getElementById(select.menuId);

        if (menu === null) {
            return;
        }

        if (!menu.contains(event.target)) {
            return;
        }

        if (event.target.tagName !== 'INPUT') {
            event.preventDefault();
        }
    }, true);

    // ////////////////////////////////////////////////////////////////////////

    // A click landing outside both the menu and its anchor puts the menu away
    $(document).on('mousedown', function(event) {
        var menu = document.getElementById(select.menuId);
        var activeAnchor = select.activeAnchor();

        if (menu === null) {
            return;
        }

        if (menu.contains(event.target)) {
            return;
        }

        if (activeAnchor !== null) {
            if (activeAnchor.contains(event.target)) {
                return;
            }
        }

        // Grabbing the popup the anchor sits in to drag it is not a click away
        if (event.target.closest(dragHandleSelector) !== null) {
            return;
        }

        select.hide_menu();
    });

    // ////////////////////////////////////////////////////////////////////////

    // The row the arrow keys stand on moves one step, wrapping at either end
    var moveActive = function(menu, step) {
        var activeRowClass = select.activeRowClass;
        var rows = menu.querySelectorAll('.zato-dropdown-item');

        if (rows.length === 0) {
            return;
        }

        var current = -1;

        for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
            if (rows[rowIdx].classList.contains(activeRowClass)) {
                current = rowIdx;
            }
        }

        var next = current + step;

        if (next < 0) {
            next = rows.length - 1;
        }

        if (next >= rows.length) {
            next = 0;
        }

        if (current !== -1) {
            rows[current].classList.remove(activeRowClass);
        }

        rows[next].classList.add(activeRowClass);
        rows[next].scrollIntoView({block: 'nearest'});
    };

    // ////////////////////////////////////////////////////////////////////////

    // The keyboard drives an open menu - arrows walk the rows, Enter picks the one
    // stood on, Escape first empties the filter and only then puts the menu away
    $(document).on('keydown', function(event) {
        var menu = document.getElementById(select.menuId);

        if (menu === null) {
            return;
        }

        if (event.key === 'ArrowDown') {
            // The page must not scroll under the menu
            event.preventDefault();
            moveActive(menu, 1);
            return;
        }

        if (event.key === 'ArrowUp') {
            event.preventDefault();
            moveActive(menu, -1);
            return;
        }

        if (event.key === 'Enter') {
            // The trigger stands inside a form - Enter must not submit it
            event.preventDefault();
            var active = menu.querySelector('.' + select.activeRowClass);

            if (active !== null) {
                active.click();
            }

            return;
        }

        if (event.key === 'Escape') {
            var filterInput = menu.querySelector('.dashboard-select-filter');

            // A filter with text in it is what Escape clears first ..
            if (filterInput !== null) {
                if (filterInput.value !== '') {
                    filterInput.value = '';

                    // .. and the rows are rebuilt the same way typing rebuilds them
                    var inputEvent = new Event('input');
                    filterInput.dispatchEvent(inputEvent);
                    return;
                }
            }

            select.hide_menu();
        }
    });
})();
