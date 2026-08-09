'use strict';

(function() {

var shared = {

    config: {
        popoverMilliseconds: 4800,

        // Where floating surfaces attach - panels, context menus, popovers, drag ghosts.
        // The dashboard leaves this alone and they land on the body, which carries the
        // .rule-engine-ui scope class itself. A host page that embeds a component sets
        // this to an element carrying the scope class and its theme, so the surfaces
        // keep their styling outside the component's own container.
        floatingRoot: null,

        // How far a floating surface keeps from the window's edges, and from its own anchor
        viewportMarginPixels: 8,
        floatingGapPixels: 6,


        // What a field says in its own placeholder when it has nothing usable in it
        requiredText: {
            name: 'Name is required',
            comment: 'Comment is required',
            channel: 'Channel is required',
            term: 'Term is required',
            entity: 'Entity is required',
            range: 'Range reads low .. high',
            find: 'Text is required',
        },

        tippyShowDelayMilliseconds: 350,
        termHighlightMilliseconds: 4000,
        dropPlaceholderThickness: 6,
    },

    iconPaths: {
        'chevron-left': '<path d="m15 18-6-6 6-6"/>',
        'chevron-right': '<path d="m9 18 6-6-6-6"/>',
        'chevrons-up-down': '<path d="m7 15 5 5 5-5"/><path d="m7 9 5-5 5 5"/>',
        'chevrons-down-up': '<path d="m7 20 5-5 5 5"/><path d="m7 4 5 5 5-5"/>',
        'grip-vertical': '<circle cx="9" cy="12" r="1"/><circle cx="9" cy="5" r="1"/><circle cx="9" cy="19" r="1"/>' +
            '<circle cx="15" cy="12" r="1"/><circle cx="15" cy="5" r="1"/><circle cx="15" cy="19" r="1"/>',
        'grip-horizontal': '<circle cx="12" cy="9" r="1"/><circle cx="19" cy="9" r="1"/><circle cx="5" cy="9" r="1"/>' +
            '<circle cx="12" cy="15" r="1"/><circle cx="19" cy="15" r="1"/><circle cx="5" cy="15" r="1"/>',
        'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
        'chevron-down': '<path d="m6 9 6 6 6-6"/>',
        'chevron-up': '<path d="m18 15-6-6-6 6"/>',
        'copy': '<rect width="14" height="14" x="8" y="8" rx="2"/>' +
            '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
        'check': '<path d="M20 6 9 17l-5-5"/>',
        'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        'plus': '<path d="M5 12h14"/><path d="M12 5v14"/>',
        'play': '<polygon points="6 3 20 12 6 21 6 3"/>',
        'trending-up': '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
        'arrow-left': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
        'external-link': '<path d="M15 3h6v6"/><path d="M10 14 21 3"/>' +
            '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    },

    icon: function(name, size) {
        return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + this.iconPaths[name] + '</svg>';
    },

// ////////////////////////////////////////////////////////////////////////

    floatingRoot: function() {
        var out = shared.config.floatingRoot === null ? document.body : shared.config.floatingRoot;
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    escape: function(text) {
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    },

// ////////////////////////////////////////////////////////////////////////

    initTips: function() {
        document.querySelectorAll('[data-tippy-content]').forEach(function(element) {
            if (element._tippy) { return; }
            tippy(element, {
                theme: 'dt',
                animation: 'shift-away',
                delay: [shared.config.tippyShowDelayMilliseconds, 0],
                allowHTML: false,
                appendTo: function() { return shared.floatingRoot(); },
            });
        });
    },

// ////////////////////////////////////////////////////////////////////////

    popover: function(anchor, text, color) {
        if (anchor === null) { return; }

        var rectangle = anchor.getBoundingClientRect();
        var instance = tippy(document.body, {
            getReferenceClientRect: function() { return rectangle; },
            content: text,
            trigger: 'manual',
            theme: 'dt',
            animation: 'shift-away',
            placement: 'bottom',
            maxWidth: 340,
            appendTo: shared.floatingRoot(),
            zIndex: 1200,
            onCreate: function(created) {
                if (color === 'green') { created.popper.querySelector('.tippy-box').classList.add('popover-green'); }
                if (color === 'red') { created.popper.querySelector('.tippy-box').classList.add('popover-red'); }
            },
            onHidden: function(hidden) { hidden.destroy(); },
        });

        instance.show();
        setTimeout(function() { instance.hide(); }, shared.config.popoverMilliseconds);
    },

// ////////////////////////////////////////////////////////////////////////

    // Any floating surface is laid under its anchor and then pulled back inside the window, and
    // it flips above the anchor when what is below cannot hold it, so nothing in it is ever out
    // of reach, whatever the window's size
    placeFloating: function(element, anchorRect) {
        var margin = shared.config.viewportMarginPixels;
        var gap = shared.config.floatingGapPixels;
        var width = element.offsetWidth;
        var height = element.offsetHeight;

        var left = anchorRect.left;
        var rightmost = window.innerWidth - margin - width;
        if (left > rightmost) { left = rightmost; }
        if (left < margin) { left = margin; }

        var top = anchorRect.bottom + gap;

        if (top + height + margin > window.innerHeight) {
            var above = anchorRect.top - gap - height;

            if (above >= margin) {
                top = above;
            } else {
                top = window.innerHeight - margin - height;
                if (top < margin) { top = margin; }
            }
        }

        // A surface inside a container counts from that container, not from the window
        if (window.getComputedStyle(element).position !== 'fixed') {
            var box = element.getBoundingClientRect();
            left = left - (box.left - element.offsetLeft);
            top = top - (box.top - element.offsetTop);
        }

        element.style.left = left + 'px';
        element.style.top = top + 'px';
    },

// ////////////////////////////////////////////////////////////////////////

    // A field that came in empty or unusable says so where the value belongs, and takes
    // its own hint back as soon as the next character arrives
    requireInput: function(element, text) {
        var field = element.closest('.field');
        var hint = field.dataset.hint;

        var restore = function() {
            field.classList.remove('field-missing');
            field.dataset.hint = hint;
            element.removeEventListener('input', restore);
        };

        element.value = '';
        field.dataset.hint = text;
        field.classList.add('field-missing');
        element.addEventListener('input', restore);
        element.focus();
    },

// ////////////////////////////////////////////////////////////////////////

    inFlight: function(button, onDone, onError) {
        if (button.disabled) { return null; }

        button.disabled = true;

        var release = function() { button.disabled = false; };

        return {
            done: function() { release(); onDone.apply(null, arguments); },
            error: function() { release(); onError.apply(null, arguments); },
            release: release,
        };
    },
};

window.shared = shared;

})();
