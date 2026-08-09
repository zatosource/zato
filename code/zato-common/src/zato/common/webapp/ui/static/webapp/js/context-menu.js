'use strict';

(function() {

shared.contextMenuElement = null;
shared.contextMenuItems = [];

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

        entry.addEventListener('click', function() {
            shared.closeContextMenu();
            item.action();
        });

        list.appendChild(entry);
    });

    menu.appendChild(head);
    menu.appendChild(list);
    shared.floatingRoot().appendChild(menu);

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
