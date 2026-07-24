'use strict';

// The page shell: the collapsible navigation, the problems panel with its
// resize handle and sticky collapsed state, pane and column resize grips
// and the drag ghosts. Augments the shared namespace from shared.js.

(function() {

shared.initShell = function() {
    document.getElementById('navigation-collapse-button').innerHTML = shared.icon('chevron-left', 14);
    var vocabularyButton = document.getElementById('vocabulary-collapse-button');
    if (vocabularyButton !== null) { vocabularyButton.innerHTML = shared.icon('chevron-right', 14); }
    shared.initProblemsResize();
    shared.initProblemsCollapse();
};

// ////////////////////////////////////////////////////////////////////////

// Dragging a handle resizes the pane next to it. On the x axis the pane
// grows to the right, on the y axis it grows upward, which is what the
// bottom problems panel needs.
shared.attachPaneResize = function(handle, pane, axis) {
    handle.addEventListener('mousedown', function(event) {
        event.preventDefault();
        var startX = event.clientX;
        var startY = event.clientY;
        var rectangle = pane.getBoundingClientRect();
        handle.classList.add('pane-resizer-active');

        var onMove = function(moveEvent) {
            if (axis === 'x') {
                pane.style.width = Math.max(140, rectangle.width + moveEvent.clientX - startX) + 'px';
            } else if (axis === 'x-right') {
                // A right-hand pane grows when its handle moves left
                pane.style.width = Math.max(140, rectangle.width + startX - moveEvent.clientX) + 'px';
            } else {
                pane.style.height = Math.max(60, rectangle.height + startY - moveEvent.clientY) + 'px';
                pane.style.maxHeight = 'none';
            }
        };

        var onUp = function() {
            handle.classList.remove('pane-resizer-active');
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    });
};

// Every page gets a resize handle on top of its problems panel
shared.initProblemsResize = function() {
    var panel = document.querySelector('.problems-panel');
    if (panel === null) { return; }

    var handle = document.createElement('div');
    handle.className = 'pane-resizer pane-resizer-horizontal';
    panel.insertBefore(handle, panel.firstChild);
    shared.attachPaneResize(handle, panel, 'y');
};

// ////////////////////////////////////////////////////////////////////////

// The problems panel collapses to its head strip at the bottom on a
// click of the head, and the state sticks across pages and visits
shared.initProblemsCollapse = function() {
    var panel = document.querySelector('.problems-panel');
    var head = document.getElementById('problems-head');
    if (panel === null || head === null) { return; }

    // localStorage is a boundary, a first visit has nothing stored
    var stored = window.localStorage.getItem('ui-problems-collapsed');
    if (stored === '1') { panel.classList.add('problems-collapsed'); }

    head.addEventListener('click', function() {
        var collapsed = panel.classList.toggle('problems-collapsed');
        window.localStorage.setItem('ui-problems-collapsed', collapsed ? '1' : '0');

        // A hand-resized panel drops its inline height, otherwise the
        // head strip would keep the full height it was dragged to
        panel.style.height = '';
        panel.style.maxHeight = '';
    });
};

// ////////////////////////////////////////////////////////////////////////

// A grip on the right edge of a header cell resizes its whole column.
// Widths are remembered by key in the caller's object and reapplied
// after every re-render.
shared.attachColumnResize = function(headerCell, key, widths) {
    if (widths[key] !== undefined) {
        headerCell.style.width = widths[key] + 'px';
        headerCell.style.minWidth = widths[key] + 'px';
        headerCell.style.maxWidth = widths[key] + 'px';
    }

    var grip = document.createElement('span');
    grip.className = 'column-resize-grip';
    headerCell.appendChild(grip);

    // Clicks on the grip must never select or drag the column
    grip.addEventListener('click', function(event) { event.stopPropagation(); });

    grip.addEventListener('mousedown', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var startX = event.clientX;
        var startWidth = headerCell.getBoundingClientRect().width;

        var onMove = function(moveEvent) {
            var width = Math.max(60, Math.round(startWidth + moveEvent.clientX - startX));
            widths[key] = width;
            headerCell.style.width = width + 'px';
            headerCell.style.minWidth = width + 'px';
            headerCell.style.maxWidth = width + 'px';
        };

        var onUp = function() {
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    });
};

// ////////////////////////////////////////////////////////////////////////

shared.toggleNavigation = function() {
    var navigation = document.getElementById('navigation');
    navigation.classList.toggle('collapsed');

    var iconName = navigation.classList.contains('collapsed') ? 'chevron-right' : 'chevron-left';
    document.getElementById('navigation-collapse-button').innerHTML = shared.icon(iconName, 14);
};

shared.toggleVocabulary = function() {
    var pane = document.getElementById('vocabulary-pane');
    pane.classList.toggle('collapsed');

    var iconName = pane.classList.contains('collapsed') ? 'chevron-left' : 'chevron-right';
    document.getElementById('vocabulary-collapse-button').innerHTML = shared.icon(iconName, 14);
};

// ////////////////////////////////////////////////////////////////////////

// A ghost preview built from real values, attached off-viewport so the
// browser uses it as the drag image following the cursor. One ghost at
// a time, every screen shares this pair.
shared.ghostElement = null;

shared.makeGhost = function(cellTexts, isColumn) {
    shared.removeGhost();

    var ghost = document.createElement('div');
    ghost.className = isColumn ? 'drag-ghost drag-ghost-column' : 'drag-ghost';

    cellTexts.forEach(function(text) {
        var cell = document.createElement('div');
        cell.className = 'drag-ghost-cell';
        cell.textContent = text;
        ghost.appendChild(cell);
    });

    document.body.appendChild(ghost);
    shared.ghostElement = ghost;

    return ghost;
};

shared.removeGhost = function() {
    if (shared.ghostElement !== null) {
        shared.ghostElement.remove();
        shared.ghostElement = null;
    }
};

})();
