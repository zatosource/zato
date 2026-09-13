// Micro-forms - resizing a popover by its bottom right corner and keeping
// the size it was left at. Loaded after micro-forms/popover.js, core.js
// calls installResize from setup and hands each popover it opens over to
// forms.makeResizable once the popover is on screen.
//
// Every popover a micro-form opens grows a grip in its bottom right corner.
// Dragging it changes the popover's width and height, the fields inside
// follow the new width and the buttons keep to the bottom edge - the look of
// that is static/css/shared/micro-forms-resize.css. A popover never shrinks
// below what its content needs.
//
// The size is kept in the browser's local storage under a key of the host's
// popup id and the form's name, so the same form opens at the same size next
// time, on this page and on every other page hosting it under the same id.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var microForms = $.fn.zato.micro_forms;

// ////////////////////////////////////////////////////////////////////////

microForms.resizeConfig = {

    // Where the sizes are kept, one entry per form
    sizePrefix: 'zato.micro-form.size.',

    // A popover being resized, and one standing at a size of its own
    resizableClass: 'micro-form-resizable',
    resizedClass: 'micro-form-resized',

    // The grip's classes and the page-wide cursor mid-resize, shared with the popup chrome
    gripClass: 'zato-popup-grip zato-popup-grip-right micro-form-grip',
    resizingClass: 'zato-popup-resizing-right',

    // How much of the window a restored popover leaves free on each side
    viewportMargin: 20
};

// ////////////////////////////////////////////////////////////////////////

microForms.installResize = function(host, forms) {

    var resizeConfig = microForms.resizeConfig;

// ////////////////////////////////////////////////////////////////////////

    // The storage key of one form
    forms.sizeKey = function(descriptorName) {
        var out = resizeConfig.sizePrefix + forms.config.popupId + '.' + descriptorName;
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // The size a form was left at, or null when it was never resized. The
    // browser is free to refuse the storage altogether, in which case the
    // popover opens at its natural size.
    forms.loadSize = function(sizeKey) {

        var stored = null;

        try {
            stored = window.localStorage.getItem(sizeKey);
        }
        catch(storageError) {
            return null;
        }

        if(stored === null) {
            return null;
        }

        var out = JSON.parse(stored);
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    forms.saveSize = function(sizeKey, container) {

        var size = {
            width: container.offsetWidth,
            height: container.offsetHeight
        };

        try {
            window.localStorage.setItem(sizeKey, JSON.stringify(size));
        }
        catch(storageError) {
            return;
        }
    };

// ////////////////////////////////////////////////////////////////////////

    // How big the popover is with no size of its own - its inline size is
    // lifted for the measurement and put back before anything is painted
    forms.naturalSize = function(container) {

        var width = container.style.width;
        var height = container.style.height;
        var maxWidth = container.style.maxWidth;

        container.style.width = '';
        container.style.height = '';
        container.style.maxWidth = '';
        container.classList.remove(resizeConfig.resizedClass);

        var out = {
            width: container.offsetWidth,
            height: container.offsetHeight
        };

        container.style.width = width;
        container.style.height = height;
        container.style.maxWidth = maxWidth;

        if(width) {
            container.classList.add(resizeConfig.resizedClass);
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    forms.applySize = function(container, width, height) {
        container.classList.add(resizeConfig.resizedClass);
        container.style.width = width + 'px';
        container.style.height = height + 'px';
        container.style.maxWidth = 'none';
    };

// ////////////////////////////////////////////////////////////////////////

    // Sizes a popover about to open to what it was left at, before it is
    // shown - so it never flashes at its natural size first. Returns whether
    // there was a size to restore, which is when the popover must be let
    // grow past the width tippy would cap it at.
    forms.restoreSize = function(container, sizeKey) {

        var size = forms.loadSize(sizeKey);

        if(size === null) {
            return false;
        }

        // The window may be smaller now than it was then
        var maxWidth = window.innerWidth - 2 * resizeConfig.viewportMargin;
        var maxHeight = window.innerHeight - 2 * resizeConfig.viewportMargin;

        var width = Math.min(size.width, maxWidth);
        var height = Math.min(size.height, maxHeight);

        forms.applySize(container, width, height);

        return true;
    };

// ////////////////////////////////////////////////////////////////////////

    // Puts the grip in the popover's corner. Called once the popover is on
    // screen, which is when its content, and with it its smallest size, is
    // known - a restored size smaller than the content now needs is grown to fit.
    forms.makeResizable = function(tippyInstance, sizeKey) {

        var container = tippyInstance.popper.querySelector('.micro-form');
        var box = tippyInstance.popper.querySelector('.tippy-box');

        container.classList.add(resizeConfig.resizableClass);

        if(container.classList.contains(resizeConfig.resizedClass)) {
            var natural = forms.naturalSize(container);
            var width = Math.max(container.offsetWidth, natural.width);
            var height = Math.max(container.offsetHeight, natural.height);
            forms.applySize(container, width, height);
        }

        var grip = document.createElement('span');
        grip.className = resizeConfig.gripClass;
        grip.innerHTML = $.fn.zato.popup.resize_icon;
        container.appendChild(grip);

        grip.addEventListener('mousedown', function(event) {

            event.preventDefault();

            // A press inside a popover is the popover's own - whatever closes it
            // on an outside press must not see this one
            event.stopPropagation();

            var grabX = event.pageX;
            var grabY = event.pageY;

            var startWidth = container.offsetWidth;
            var startHeight = container.offsetHeight;

            // The content sets how small the popover may be dragged
            var natural = forms.naturalSize(container);

            // Tippy caps its box at the width it was opened with - a popover
            // resized by hand grows past that
            box.style.maxWidth = 'none';

            // The pointer spends the drag outside the grip, so the cursor is
            // held for the whole page instead of only for the corner
            document.documentElement.classList.add(resizeConfig.resizingClass);

            var onMove = function(move) {
                var width = Math.max(startWidth + move.pageX - grabX, natural.width);
                var height = Math.max(startHeight + move.pageY - grabY, natural.height);
                forms.applySize(container, width, height);
            };

            var onUp = function() {
                document.documentElement.classList.remove(resizeConfig.resizingClass);
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
                forms.saveSize(sizeKey, container);
            };

            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        });
    };

// ////////////////////////////////////////////////////////////////////////

};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
