'use strict';

// The floating panel, one at a time, app-wide: rename panels, publish
// confirmations, save-view panels, the settings panel. Always anchored
// to the element that was interacted with. Augments the shared
// namespace from shared.js.

(function() {

shared.panelElement = null;

// The selectors of every control that opens a panel: clicks on them
// toggle their panel instead of merely closing it, every other click
// outside the panel closes it. Screens push their own selectors here.
shared.panelToggles = ['#settings-button'];

// ////////////////////////////////////////////////////////////////////////

shared.closePanel = function() {
    if (shared.panelElement === null) { return; }
    shared.panelElement.remove();
    shared.panelElement = null;
};

// ////////////////////////////////////////////////////////////////////////

shared.openPanel = function(anchor, html) {
    shared.closePanel();

    var panel = document.createElement('div');
    panel.className = 'floating-panel';
    panel.innerHTML = html;
    document.body.appendChild(panel);

    var rectangle = anchor.getBoundingClientRect();
    panel.style.top = (rectangle.bottom + 6) + 'px';
    panel.style.left = Math.min(rectangle.left, window.innerWidth - panel.offsetWidth - 8) + 'px';
    shared.panelElement = panel;

    var input = panel.querySelector('input');
    if (input !== null) { input.focus(); input.select(); }
};

// ////////////////////////////////////////////////////////////////////////

// One outside-click handler for the floating panel, app-wide: the
// controls listed in panelToggles handle their own toggling, any other
// click outside the panel closes it
document.addEventListener('mousedown', function(event) {
    if (shared.panelElement === null) { return; }

    var isToggle = shared.panelToggles.some(function(selector) {
        return event.target.closest(selector) !== null;
    });
    if (isToggle) { return; }

    if (!shared.panelElement.contains(event.target)) { shared.closePanel(); }
});

})();
