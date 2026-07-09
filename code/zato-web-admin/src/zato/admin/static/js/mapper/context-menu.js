
// Mapper kit - the context menu.
// One small menu opened at the pointer, used by the canvas for lines
// and target fields. Entries are plain actions, optionally grouped
// under header rows. The menu closes on Escape, on any outside click
// and right after an entry runs.

(function($) {

    zato.mapper.contextMenu = {};

// ////////////////////////////////////////////////////////////////////////

    var current = null;

// ////////////////////////////////////////////////////////////////////////

    // Closes the open menu, if any. Returns whether one was open.
    zato.mapper.contextMenu.close = function() {

        if (current === null) {
            return false;
        }

        $(current).remove();
        current = null;
        return true;
    };

// ////////////////////////////////////////////////////////////////////////

    // Opens a menu at the given viewport position.
    // menuConfig:
    //   x, y:   viewport coordinates the menu opens at
    //   items:  [{label, onSelect}] entries and {header} group rows
    zato.mapper.contextMenu.open = function(menuConfig) {

        // Only one menu at a time - a new one replaces the old one.
        zato.mapper.contextMenu.close();

        var menu = document.createElement('div');
        menu.className = 'mapper-context-menu';
        menu.setAttribute('role', 'menu');

        for (var itemIdx = 0; itemIdx < menuConfig.items.length; itemIdx++) {
            var item = menuConfig.items[itemIdx];

            if (item.header !== undefined) {
                var header = document.createElement('div');
                header.className = 'mapper-context-menu-header';
                header.textContent = item.header;
                menu.appendChild(header);
                continue;
            }

            var entry = document.createElement('button');
            entry.className = 'mapper-context-menu-item';
            entry.type = 'button';
            entry.setAttribute('role', 'menuitem');
            entry.setAttribute('data-index', itemIdx);
            entry.textContent = item.label;
            menu.appendChild(entry);
        }

        document.body.appendChild(menu);
        current = menu;

        // The menu opens at the pointer but never leaves the viewport.
        var menuRect = menu.getBoundingClientRect();

        var menuX = menuConfig.x;
        if (menuX + menuRect.width > window.innerWidth) {
            menuX = window.innerWidth - menuRect.width;
        }

        var menuY = menuConfig.y;
        if (menuY + menuRect.height > window.innerHeight) {
            menuY = window.innerHeight - menuRect.height;
        }

        menu.style.left = menuX + 'px';
        menu.style.top = menuY + 'px';

        $(menu).on('click', '.mapper-context-menu-item', function() {

            var item = menuConfig.items[parseInt(this.getAttribute('data-index'), 10)];

            // The entry runs after the menu is gone, so an entry opening
            // another menu (or a dialog) never fights the old one.
            zato.mapper.contextMenu.close();

            zato.mapper.log('context-menu', 'entry chosen', {label: item.label});
            item.onSelect();
        });
    };

// ////////////////////////////////////////////////////////////////////////

    // One document-level pair of close triggers serves every menu.
    $(document).on('mousedown', function(event) {
        if (current !== null && !current.contains(event.target)) {
            zato.mapper.contextMenu.close();
        }
    });

    // Escape closes the menu and does nothing else - the capture phase
    // stops the key before any other Escape behavior (like clearing the
    // mapping selection) reacts to the same press.
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && current !== null) {
            event.stopPropagation();
            zato.mapper.contextMenu.close();
        }
    }, true);

})(jQuery);
