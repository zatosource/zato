'use strict';

// The right-click menu shared by every screen: game-like hotkeys in front
// of the labels, a description pane that fills in as entries are hovered,
// dismissal by a click anywhere else or Escape, and one menu on screen at
// a time. Augments the shared namespace from shared.js.

(function() {

shared.contextMenuElement = null;
shared.contextMenuItems = [];

// The hotkeys are positional, the way games assign them: the right hand is
// on the mouse, the left hand rests on this cluster, the first entry is
// always Q, the second always W, no reading or reaching required
shared.contextMenuHotkeys = ['Q', 'W', 'E', 'R', 'A', 'S', 'D', 'F', 'Z', 'X', 'C', 'V'];

// ////////////////////////////////////////////////////////////////////////

shared.closeContextMenu = function() {
    if (shared.contextMenuElement === null) { return; }

    shared.contextMenuElement.remove();
    shared.contextMenuElement = null;
    document.removeEventListener('mousedown', shared.contextMenuDismiss);
    document.removeEventListener('keydown', shared.contextMenuKeys);
};

// ////////////////////////////////////////////////////////////////////////

// Opens the menu at the pointer. Every item carries a label, a description
// for the info pane and its action, null draws a separator. The hotkeys
// are assigned here, by position, never by the caller.
shared.openContextMenu = function(title, items, x, y) {
    shared.closeContextMenu();

    var nextHotkey = 0;
    items.forEach(function(item) {
        if (item === null) { return; }
        item.key = shared.contextMenuHotkeys[nextHotkey];
        nextHotkey += 1;
    });

    var menu = document.createElement('div');
    menu.className = 'context-menu';

    var head = document.createElement('div');
    head.className = 'context-menu-head';
    head.textContent = title;

    var list = document.createElement('div');
    list.className = 'context-menu-list';

    var info = document.createElement('div');
    info.className = 'context-menu-info';
    info.textContent = 'Hover an entry to read what it does, or press its key.';

    items.forEach(function(item) {
        if (item === null) {
            var separator = document.createElement('div');
            separator.className = 'context-menu-separator';
            list.appendChild(separator);
            return;
        }

        var entry = document.createElement('div');
        entry.className = 'context-menu-item' + (item.destructive ? ' context-menu-item-destructive' : '');
        entry.innerHTML = '<span class="context-menu-key">' + item.key + '</span>' +
            '<span class="context-menu-label">' + shared.escape(item.label) + '</span>';

        entry.addEventListener('mouseenter', function() { info.textContent = item.description; });
        entry.addEventListener('click', function() {
            shared.closeContextMenu();
            item.action();
        });

        list.appendChild(entry);
    });

    menu.appendChild(head);
    menu.appendChild(list);
    menu.appendChild(info);
    document.body.appendChild(menu);

    // Clamped to the viewport so the menu never opens off screen
    var left = Math.min(x, window.innerWidth - menu.offsetWidth - 8);
    var top = Math.min(y, window.innerHeight - menu.offsetHeight - 8);
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';

    shared.contextMenuElement = menu;
    shared.contextMenuItems = items;
    document.addEventListener('mousedown', shared.contextMenuDismiss);
    document.addEventListener('keydown', shared.contextMenuKeys);
};

// ////////////////////////////////////////////////////////////////////////

shared.contextMenuDismiss = function(event) {
    if (!shared.contextMenuElement.contains(event.target)) {
        shared.closeContextMenu();
    }
};

// Escape closes the menu, an entry's own key runs it directly
shared.contextMenuKeys = function(event) {
    if (event.key === 'Escape') { shared.closeContextMenu(); return; }

    var match = shared.contextMenuItems.filter(function(item) {
        return item !== null && item.key.toLowerCase() === event.key.toLowerCase();
    })[0];

    if (match !== undefined) {
        event.preventDefault();
        shared.closeContextMenu();
        match.action();
    }
};

})();
