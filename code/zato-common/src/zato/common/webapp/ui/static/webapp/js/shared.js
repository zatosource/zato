'use strict';

(function() {

var shared = {

    config: {
        popoverMilliseconds: 4800,
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
            appendTo: document.body,
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
