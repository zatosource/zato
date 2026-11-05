'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

var portal = window.portal;

var tooltips = {};

// ////////////////////////////////////////////////////////////////////////

tooltips.readTip = function(reference) {
    var out = reference.getAttribute('data-tip');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A value that was edited no longer has the tip it was given, and its tooltip stays closed.
tooltips.onShow = function(instance) {
    if (!instance.reference.hasAttribute('data-tip')) {
        return false;
    }
};

// ////////////////////////////////////////////////////////////////////////

// Attaches a tooltip to each element under the root that has a data-tip attribute and no tooltip yet.
tooltips.attach = function(root) {

    var elements = root.querySelectorAll('[data-tip]');

    for (var elementIndex = 0; elementIndex < elements.length; elementIndex++) {

        var element = elements[elementIndex];

        if (element._tippy) {
            continue;
        }

        window.tippy(element, {
            content: tooltips.readTip,
            delay: portal.config.tipDelay,
            placement: 'top',
            appendTo: document.body,
            onShow: tooltips.onShow
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

tooltips.init = function() {
    tooltips.attach(document);
};

// ////////////////////////////////////////////////////////////////////////

portal.tooltips = tooltips;

document.addEventListener('DOMContentLoaded', tooltips.init);

// ////////////////////////////////////////////////////////////////////////

})();
