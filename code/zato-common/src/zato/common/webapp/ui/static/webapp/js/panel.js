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

    var rectangle = anchor.getBoundingClientRect();

    var panel = document.createElement('div');
    panel.className = 'floating-panel';
    panel.innerHTML = html;
    document.body.appendChild(panel);

    var top = rectangle.bottom + 6;
    var left = rectangle.left;

    panel.style.top = Math.min(top, window.innerHeight - panel.offsetHeight - 8) + 'px';
    panel.style.left = Math.min(left, window.innerWidth - panel.offsetWidth - 8) + 'px';
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
