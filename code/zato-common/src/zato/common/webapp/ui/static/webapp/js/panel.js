'use strict';

(function() {

shared.panelElement = null;

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

document.addEventListener('mousedown', function(event) {
    if (shared.panelElement === null) { return; }

    var isToggle = shared.panelToggles.some(function(selector) {
        return event.target.closest(selector) !== null;
    });
    if (isToggle) { return; }

    if (!shared.panelElement.contains(event.target)) { shared.closePanel(); }
});

})();
