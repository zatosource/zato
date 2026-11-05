zatoApp.popover = {};

zatoApp.popover.config = {
    popoverId: 'app-popover',
    gap: 6,
    edgeMargin: 8,
    escapeKey: 'Escape',
    unit: 'px',
};

zatoApp.popover.state = {
    anchor: null,
    onClose: null,
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.popover.open = function(anchor, content, onClose) {

    var config = zatoApp.popover.config;
    var state = zatoApp.popover.state;
    var popover = document.getElementById(config.popoverId);

    // A second click on the button that opened the popover closes it ..
    if(state.anchor === anchor) {
        zatoApp.popover.close();
        return;
    }

    // .. while a click on any other button replaces what is shown.
    if(state.anchor !== null) {
        zatoApp.popover.close();
    }

    state.anchor = anchor;
    state.onClose = onClose;

    popover.textContent = '';
    popover.appendChild(content);
    popover.hidden = false;

    zatoApp.popover.place(anchor, popover);

    // The panel holding the button scrolls on its own, so the popover follows the button whenever any panel scrolls
    document.addEventListener('scroll', zatoApp.popover.onDocumentScroll, true);
    document.addEventListener('pointerdown', zatoApp.popover.onDocumentPointerDown, true);
    document.addEventListener('keydown', zatoApp.popover.onDocumentKeyDown);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.popover.onDocumentScroll = function() {

    var popover = document.getElementById(zatoApp.popover.config.popoverId);
    var anchor = zatoApp.popover.state.anchor;

    zatoApp.popover.place(anchor, popover);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.popover.place = function(anchor, popover) {

    var config = zatoApp.popover.config;

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

zatoApp.popover.close = function() {

    var config = zatoApp.popover.config;
    var state = zatoApp.popover.state;
    var popover = document.getElementById(config.popoverId);
    var onClose = state.onClose;

    popover.hidden = true;
    popover.textContent = '';

    state.anchor = null;
    state.onClose = null;

    document.removeEventListener('scroll', zatoApp.popover.onDocumentScroll, true);
    document.removeEventListener('pointerdown', zatoApp.popover.onDocumentPointerDown, true);
    document.removeEventListener('keydown', zatoApp.popover.onDocumentKeyDown);

    if(onClose !== null) {
        onClose();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.popover.onDocumentPointerDown = function(event) {

    var popover = document.getElementById(zatoApp.popover.config.popoverId);
    var anchor = zatoApp.popover.state.anchor;

    // Pointers inside the popover use it, and the button that opened it handles its own clicks
    if(popover.contains(event.target)) {
        return;
    }

    if(anchor.contains(event.target)) {
        return;
    }

    zatoApp.popover.close();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.popover.onDocumentKeyDown = function(event) {

    if(event.key !== zatoApp.popover.config.escapeKey) {
        return;
    }

    var anchor = zatoApp.popover.state.anchor;

    zatoApp.popover.close();
    anchor.focus();
};
