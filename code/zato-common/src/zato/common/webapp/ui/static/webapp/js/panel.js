'use strict';

(function() {

shared.panelElement = null;

shared.panelAnchor = null;

shared.panelToggles = ['#settings-button'];

// ////////////////////////////////////////////////////////////////////////

shared.closePanel = function() {
    if (shared.panelElement === null) { return; }
    shared.panelElement.remove();
    shared.panelElement = null;
    shared.panelAnchor = null;
};

// ////////////////////////////////////////////////////////////////////////

shared.openPanel = function(anchor, html) {
    shared.closePanel();

    var panel = document.createElement('div');
    panel.className = 'floating-panel';
    panel.innerHTML = html;
    document.body.appendChild(panel);

    shared.placeFloating(panel, anchor.getBoundingClientRect());
    shared.panelElement = panel;
    shared.panelAnchor = anchor;

    var input = panel.querySelector('input');
    if (input !== null) { input.focus(); input.select(); }
};

// ////////////////////////////////////////////////////////////////////////

document.addEventListener('mousedown', function(event) {
    if (shared.panelElement === null) { return; }

    var isToggle = shared.panelToggles.some(function(selector) {
        return event.target.closest(selector) !== null;
    });
    if (isToggle) { return; }

    if (!shared.panelElement.contains(event.target)) { shared.closePanel(); }
});

// A window that changed size leaves the panel where it can still be reached and used
window.addEventListener('resize', function() {
    if (shared.panelElement === null) { return; }

    // A repainted screen can replace the element the panel came from, and a gone anchor
    // has no rectangle to place anything against
    if (!document.body.contains(shared.panelAnchor)) { return; }

    shared.placeFloating(shared.panelElement, shared.panelAnchor.getBoundingClientRect());
});

})();
