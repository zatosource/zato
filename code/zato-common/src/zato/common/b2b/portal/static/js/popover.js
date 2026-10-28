'use strict';

// A popover is a tippy box opened by a press on its anchor, with a header it is dragged by,
// a body the host builds each time it opens and a row of buttons under the body.
//
// spec:
//   title         - what the header says
//   build(handle) - returns the body element, called each time the popover opens
//   buttons(handle) - returns a list of {label, isPrimary, onClick}, called right after build
//   placement     - optional, where the popover opens in relation to its anchor
//   isCellAnchored - optional, the popover of a table row opens at the cell that was pressed rather than at the row
//
// A press that ends a selection of text leaves the text selected rather than opening the popover.
//
// The handle passed to build and buttons has close(), which hides the popover.

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var popover = {};

popover.config = {
    placement: 'bottom-start',
    theme: 'popup',

    // The tippies that Escape closes before it reaches what is under them
    closedByEscape: '.tippy-box[data-theme~="popup"], .tippy-box[data-theme~="details"]'
};

// ////////////////////////////////////////////////////////////////////////

popover.attach = function(anchor, spec) {

    var placement = spec.placement === undefined ? popover.config.placement : spec.placement;

    var handle = {
        instance: null,
        cell: null,
        offsetX: 0,
        offsetY: 0
    };

    handle.close = function() {
        handle.instance.hide();
    };

    handle.instance = window.tippy(anchor, {
        content: '',
        trigger: 'click',
        interactive: true,
        hideOnClick: true,
        arrow: false,
        animation: false,
        theme: popover.config.theme,
        placement: placement,
        offset: portal.config.popoverOffset,
        maxWidth: 'none',
        appendTo: document.body,
        getReferenceClientRect: function() {
            var out = popover.shiftedRect(handle);
            return out;
        },
        onTrigger: function(instance, event) {
            if (spec.isCellAnchored) {
                handle.cell = event.target.closest('td');
            }
        },
        onShow: function(instance) {

            if (popover.hasSelectedText(instance.reference)) {
                return false;
            }

            var content = popover.buildContent(spec, handle);
            instance.setContent(content);
        },
        onShown: function(instance) {
            popover.focusFirst(instance.popper);
        },
        onHidden: function(instance) {
            popover.resetOffset(handle);
            instance.setContent('');
        }
    });

    return handle;
};

// ////////////////////////////////////////////////////////////////////////

popover.hasSelectedText = function(anchor) {

    var selected = window.getSelection();

    if (selected.isCollapsed) {
        return false;
    }

    var out = anchor.contains(selected.anchorNode);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.buildContent = function(spec, handle) {

    var container = portal.create('div', 'popup', '');

    // The header names the popover and is what it is dragged by ..
    var header = portal.create('div', 'popup-header', spec.title);
    header.addEventListener('mousedown', function(event) {
        popover.startDrag(event, handle);
    });
    container.appendChild(header);

    // .. the body is the host's own ..
    var body = portal.create('div', 'popup-body', '');
    body.appendChild(spec.build(handle));
    container.appendChild(body);

    // .. and the buttons under it close it.
    var buttons = portal.create('div', 'popup-buttons', '');
    var buttonSpecs = spec.buttons(handle);

    for (var buttonIndex = 0; buttonIndex < buttonSpecs.length; buttonIndex++) {
        var buttonSpec = buttonSpecs[buttonIndex];
        var button = portal.createButton(buttonSpec.label, buttonSpec.isPrimary, buttonSpec.onClick);
        buttons.appendChild(button);
    }

    body.appendChild(buttons);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

popover.focusFirst = function(popper) {

    var field = popper.querySelector('input:not([type="checkbox"]), select');

    if (field) {
        field.focus();
    }
};

// ////////////////////////////////////////////////////////////////////////

// The popover is positioned against its anchor, so a drag moves the rectangle the anchor is measured as.
popover.shiftedRect = function(handle) {

    var element = handle.cell === null ? handle.instance.reference : handle.cell;
    var rect = element.getBoundingClientRect();

    var out = {
        width: rect.width,
        height: rect.height,
        top: rect.top + handle.offsetY,
        bottom: rect.bottom + handle.offsetY,
        left: rect.left + handle.offsetX,
        right: rect.right + handle.offsetX,
        x: rect.left + handle.offsetX,
        y: rect.top + handle.offsetY
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

popover.startDrag = function(event, handle) {

    event.preventDefault();

    var startX = event.clientX - handle.offsetX;
    var startY = event.clientY - handle.offsetY;

    // A dragged popover stays where it was put rather than flipping to the other side of its anchor
    handle.instance.setProps({
        popperOptions: {modifiers: [{name: 'flip', enabled: false}]}
    });

    document.body.classList.add('popup-dragging');

    var onMove = function(moveEvent) {
        handle.offsetX = moveEvent.clientX - startX;
        handle.offsetY = moveEvent.clientY - startY;
        handle.instance.popperInstance.update();
    };

    var onUp = function() {
        document.body.classList.remove('popup-dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
};

// ////////////////////////////////////////////////////////////////////////

popover.resetOffset = function(handle) {

    handle.offsetX = 0;
    handle.offsetY = 0;

    handle.instance.setProps({popperOptions: {}});
};

// ////////////////////////////////////////////////////////////////////////

// Escape closes the popovers first, and only when none is open does it reach what is under them.
popover.onKeyDown = function(event) {

    if (event.key !== 'Escape') {
        return;
    }

    if (document.querySelector(popover.config.closedByEscape) === null) {
        return;
    }

    window.tippy.hideAll({duration: 0});
    event.stopImmediatePropagation();
};

// ////////////////////////////////////////////////////////////////////////

portal.popover = popover;

document.addEventListener('keydown', popover.onKeyDown);

// ////////////////////////////////////////////////////////////////////////

})();
