'use strict';

(function() {

var shellReady = false;

shared.initShell = function() {

    if (shellReady) { return; }
    shellReady = true;

    var collapseButton = document.getElementById('navigation-collapse-button');
    if (collapseButton !== null) { collapseButton.innerHTML = shared.icon('chevron-left', 14); }

    shared.initProblemsResize();
    shared.initVocabularyResize();
    shared.initProblemsCollapse();
};

// ////////////////////////////////////////////////////////////////////////

shared.attachPaneResize = function(handle, pane, axis) {
    handle.addEventListener('mousedown', function(event) {
        event.preventDefault();
        var startX = event.clientX;
        var startY = event.clientY;
        var rectangle = pane.getBoundingClientRect();
        handle.classList.add('pane-resizer-active');

        // A pane animating its own size would trail behind the pointer
        var paneTransition = pane.style.transition;
        pane.style.transition = 'none';

        var onMove = function(moveEvent) {
            if (axis === 'x') {
                pane.style.width = Math.max(140, rectangle.width + moveEvent.clientX - startX) + 'px';
            } else if (axis === 'x-right') {
                pane.style.width = Math.max(140, rectangle.width + startX - moveEvent.clientX) + 'px';
            } else {
                pane.style.height = Math.max(60, rectangle.height + startY - moveEvent.clientY) + 'px';
                pane.style.maxHeight = 'none';
            }
        };

        var onUp = function() {
            handle.classList.remove('pane-resizer-active');
            pane.style.transition = paneTransition;
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    });
};

// The problems panel's split bar, so the panel's collapse toggle can put
// it away and bring it back
shared.problemsSplitBar = null;

shared.initProblemsResize = function() {
    var panel = document.querySelector('.problems-panel');
    if (panel === null) { return; }

    // The bar stands between the editor area and the panel, carrying the
    // dividing line the panel itself no longer draws
    var bar = document.createElement('div');
    bar.className = 'pane-split-bar pane-split-bar-horizontal';
    panel.parentNode.insertBefore(bar, panel);

    paneSplit.init({
        bar: bar,
        pane: panel,
        container: panel.parentNode,
        axis: 'y',
        minSize: 60,
        minOther: 160,
        snapSize: 40,
        activeClass: 'pane-split-active',
        storageKey: 'zato.rule-editor.split.problems',

        // The panel opens capped by its stylesheet - the first pull, or the
        // size a past visit kept, takes over from the cap
        apply: function(size) {
            panel.style.height = size + 'px';
            panel.style.maxHeight = 'none';
        },
    });

    shared.problemsSplitBar = bar;
};

shared.initVocabularyResize = function() {
    var pane = document.getElementById('vocabulary-pane');
    if (pane === null) { return; }

    var bar = document.createElement('div');
    bar.className = 'pane-split-bar pane-split-bar-vertical';
    pane.parentNode.insertBefore(bar, pane);

    paneSplit.init({
        bar: bar,
        pane: pane,
        container: pane.parentNode,
        axis: 'x',
        minSize: 160,
        minOther: 420,
        snapSize: 120,
        activeClass: 'pane-split-active',
        storageKey: 'zato.rule-editor.split.vocabulary',
    });
};

// ////////////////////////////////////////////////////////////////////////

shared.initProblemsCollapse = function() {
    var panel = document.querySelector('.problems-panel');
    var head = document.getElementById('problems-head');
    if (panel === null || head === null) { return; }

    var indicator = document.createElement('span');
    indicator.className = 'problems-collapse-indicator';
    head.appendChild(indicator);

    var drawIndicator = function() {
        var collapsed = panel.classList.contains('problems-collapsed');
        indicator.innerHTML = shared.icon(collapsed ? 'chevron-up' : 'chevron-down', 12);
    };

    // The pulled-to height steps aside while the panel is collapsed - only the
    // head shows then - and comes back with the panel, its split bar likewise
    var storedHeight = '';
    var storedMaxHeight = '';

    var stashSize = function() {
        storedHeight = panel.style.height;
        storedMaxHeight = panel.style.maxHeight;
        panel.style.height = '';
        panel.style.maxHeight = '';
    };

    var applyCollapsed = function(collapsed) {
        if (collapsed) {
            stashSize();
        }
        else {
            panel.style.height = storedHeight;
            panel.style.maxHeight = storedMaxHeight;
        }

        if (shared.problemsSplitBar !== null) {
            shared.problemsSplitBar.style.display = collapsed ? 'none' : '';
        }
    };

    var stored = window.localStorage.getItem('ui-problems-collapsed');

    if (stored === '1') {
        panel.classList.add('problems-collapsed');
        applyCollapsed(true);
    }

    drawIndicator();

    head.addEventListener('click', function() {
        var collapsed = panel.classList.toggle('problems-collapsed');
        window.localStorage.setItem('ui-problems-collapsed', collapsed ? '1' : '0');
        drawIndicator();
        applyCollapsed(collapsed);
    });
};

// ////////////////////////////////////////////////////////////////////////

shared.attachColumnResize = function(headerCell, key, widths) {
    if (widths[key] !== undefined) {
        headerCell.style.width = widths[key] + 'px';
        headerCell.style.minWidth = widths[key] + 'px';
        headerCell.style.maxWidth = widths[key] + 'px';
    }

    var grip = document.createElement('span');
    grip.className = 'column-resize-grip';
    headerCell.appendChild(grip);

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

// ////////////////////////////////////////////////////////////////////////

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

    shared.floatingRoot().appendChild(ghost);
    shared.ghostElement = ghost;

    return ghost;
};

shared.removeGhost = function() {
    if (shared.ghostElement !== null) {
        shared.ghostElement.remove();
        shared.ghostElement = null;
    }
};

// ////////////////////////////////////////////////////////////////////////

shared.dropPlaceholderElement = null;

shared.showDropPlaceholder = function(left, top, width, height) {
    if (shared.dropPlaceholderElement === null) {
        var element = document.createElement('div');
        element.className = 'drop-placeholder';
        shared.floatingRoot().appendChild(element);
        shared.dropPlaceholderElement = element;
    }

    shared.dropPlaceholderElement.style.left = left + 'px';
    shared.dropPlaceholderElement.style.top = top + 'px';
    shared.dropPlaceholderElement.style.width = width + 'px';
    shared.dropPlaceholderElement.style.height = height + 'px';
};

shared.removeDropPlaceholder = function() {
    if (shared.dropPlaceholderElement !== null) {
        shared.dropPlaceholderElement.remove();
        shared.dropPlaceholderElement = null;
    }
};

// ////////////////////////////////////////////////////////////////////////

shared.termFromHash = function() {
    var match = /#term=([A-Za-z0-9._]+)/.exec(window.location.hash);
    var out = match === null ? null : match[1];
    return out;
};

shared.applyTermHighlight = function(elements) {
    if (elements.length === 0) { return; }

    elements.forEach(function(element) { element.classList.add('term-highlight'); });
    elements[0].scrollIntoView({block: 'center'});

    setTimeout(function() {
        elements.forEach(function(element) { element.classList.remove('term-highlight'); });
    }, shared.config.termHighlightMilliseconds);
};

})();
