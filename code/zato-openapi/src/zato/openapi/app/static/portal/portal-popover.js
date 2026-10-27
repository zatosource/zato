zatoPortal.popover = {};

zatoPortal.popover.config = {
    popoverId: 'portal-popover',
    gap: 6,
    edgeMargin: 8,
    escapeKey: 'Escape',
    unit: 'px',
};

zatoPortal.popover.state = {
    anchor: null,
    onClose: null,
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.popover.open = function(anchor, content, onClose) {

    var config = zatoPortal.popover.config;
    var state = zatoPortal.popover.state;
    var popover = document.getElementById(config.popoverId);

    // A second click on the button that opened the popover closes it ..
    if(state.anchor === anchor) {
        zatoPortal.popover.close();
        return;
    }

    // .. while a click on any other button replaces what is shown.
    if(state.anchor !== null) {
        zatoPortal.popover.close();
    }

    state.anchor = anchor;
    state.onClose = onClose;

    popover.textContent = '';
    popover.appendChild(content);
    popover.hidden = false;

    zatoPortal.popover.place(anchor, popover);

    // The panel holding the button scrolls on its own, so the popover follows the button whenever any panel scrolls
    document.addEventListener('scroll', zatoPortal.popover.onDocumentScroll, true);
    document.addEventListener('pointerdown', zatoPortal.popover.onDocumentPointerDown, true);
    document.addEventListener('keydown', zatoPortal.popover.onDocumentKeyDown);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.popover.onDocumentScroll = function() {

    var popover = document.getElementById(zatoPortal.popover.config.popoverId);
    var anchor = zatoPortal.popover.state.anchor;

    zatoPortal.popover.place(anchor, popover);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.popover.place = function(anchor, popover) {

    var config = zatoPortal.popover.config;

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

zatoPortal.popover.close = function() {

    var config = zatoPortal.popover.config;
    var state = zatoPortal.popover.state;
    var popover = document.getElementById(config.popoverId);
    var onClose = state.onClose;

    popover.hidden = true;
    popover.textContent = '';

    state.anchor = null;
    state.onClose = null;

    document.removeEventListener('scroll', zatoPortal.popover.onDocumentScroll, true);
    document.removeEventListener('pointerdown', zatoPortal.popover.onDocumentPointerDown, true);
    document.removeEventListener('keydown', zatoPortal.popover.onDocumentKeyDown);

    if(onClose !== null) {
        onClose();
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.popover.onDocumentPointerDown = function(event) {

    var popover = document.getElementById(zatoPortal.popover.config.popoverId);
    var anchor = zatoPortal.popover.state.anchor;

    // Pointers inside the popover use it, and the button that opened it handles its own clicks
    if(popover.contains(event.target)) {
        return;
    }

    if(anchor.contains(event.target)) {
        return;
    }

    zatoPortal.popover.close();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.popover.onDocumentKeyDown = function(event) {

    if(event.key !== zatoPortal.popover.config.escapeKey) {
        return;
    }

    var anchor = zatoPortal.popover.state.anchor;

    zatoPortal.popover.close();
    anchor.focus();
};
