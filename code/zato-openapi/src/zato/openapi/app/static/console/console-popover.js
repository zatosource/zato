zatoConsole.popover = {};

zatoConsole.popover.config = {
    popoverId: 'console-popover',
    gap: 6,
    edgeMargin: 8,
    escapeKey: 'Escape',
    unit: 'px',
};

zatoConsole.popover.state = {
    anchor: null,
    onClose: null,
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.open = function(anchor, content, onClose) {

    var config = zatoConsole.popover.config;
    var state = zatoConsole.popover.state;
    var popover = document.getElementById(config.popoverId);

    // A second click on the button that opened the popover closes it ..
    if(state.anchor === anchor) {
        zatoConsole.popover.close();
        return;
    }

    // .. while a click on any other button replaces what is shown.
    if(state.anchor !== null) {
        zatoConsole.popover.close();
    }

    state.anchor = anchor;
    state.onClose = onClose;

    popover.textContent = '';
    popover.appendChild(content);
    popover.hidden = false;

    zatoConsole.popover.place(anchor, popover);

    // The panel holding the button scrolls on its own, so the popover follows the button whenever any panel scrolls
    document.addEventListener('scroll', zatoConsole.popover.onDocumentScroll, true);
    document.addEventListener('pointerdown', zatoConsole.popover.onDocumentPointerDown, true);
    document.addEventListener('keydown', zatoConsole.popover.onDocumentKeyDown);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.onDocumentScroll = function() {

    var popover = document.getElementById(zatoConsole.popover.config.popoverId);
    var anchor = zatoConsole.popover.state.anchor;

    zatoConsole.popover.place(anchor, popover);
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.place = function(anchor, popover) {

    var config = zatoConsole.popover.config;

    var anchorRect = anchor.getBoundingClientRect();
    var popoverWidth = popover.offsetWidth;
    var pageWidth = document.documentElement.clientWidth;

    // The popover opens below its button, with their right edges aligned, and never past either side of the page
    var left = anchorRect.right - popoverWidth;
    var rightmost = pageWidth - popoverWidth - config.edgeMargin;

    left = Math.min(left, rightmost);
    left = Math.max(left, config.edgeMargin);

    var top = anchorRect.bottom + config.gap + window.scrollY;
    var pageLeft = left + window.scrollX;

    popover.style.top = top + config.unit;
    popover.style.left = pageLeft + config.unit;
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.close = function() {

    var config = zatoConsole.popover.config;
    var state = zatoConsole.popover.state;
    var popover = document.getElementById(config.popoverId);
    var onClose = state.onClose;

    popover.hidden = true;
    popover.textContent = '';

    state.anchor = null;
    state.onClose = null;

    document.removeEventListener('scroll', zatoConsole.popover.onDocumentScroll, true);
    document.removeEventListener('pointerdown', zatoConsole.popover.onDocumentPointerDown, true);
    document.removeEventListener('keydown', zatoConsole.popover.onDocumentKeyDown);

    if(onClose !== null) {
        onClose();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.onDocumentPointerDown = function(event) {

    var popover = document.getElementById(zatoConsole.popover.config.popoverId);
    var anchor = zatoConsole.popover.state.anchor;

    // Pointers inside the popover use it, and the button that opened it handles its own clicks
    if(popover.contains(event.target)) {
        return;
    }

    if(anchor.contains(event.target)) {
        return;
    }

    zatoConsole.popover.close();
};

// ////////////////////////////////////////////////////////////////////////

zatoConsole.popover.onDocumentKeyDown = function(event) {

    if(event.key !== zatoConsole.popover.config.escapeKey) {
        return;
    }

    var anchor = zatoConsole.popover.state.anchor;

    zatoConsole.popover.close();
    anchor.focus();
};
