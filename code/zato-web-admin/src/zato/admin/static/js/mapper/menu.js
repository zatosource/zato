
// Mapper kit - anchored dropdown menu.
// Opens a grouped menu below an anchor element, styled by the shared
// dropdown-menu stylesheet the rate limiting pages use too. Clicking
// the anchor again, clicking outside or picking an item closes it.

(function($) {

    zato.mapper.menu = {};

// ////////////////////////////////////////////////////////////////////////

    var activeMenu = null;
    var activeAnchor = null;

// ////////////////////////////////////////////////////////////////////////

    function close() {

        if (activeMenu === null) {
            return;
        }

        activeMenu.parentNode.removeChild(activeMenu);
        activeMenu = null;
        activeAnchor = null;
    }

    zato.mapper.menu.close = close;

// ////////////////////////////////////////////////////////////////////////

    function buildItem(item) {

        var row = document.createElement('div');
        row.className = item.selected ? 'zato-dropdown-item zato-dropdown-item-selected' : 'zato-dropdown-item';

        var label = document.createElement('span');
        label.className = 'zato-dropdown-item-text';
        label.textContent = item.label;
        row.appendChild(label);

        $(row).on('click', function() {
            close();
            item.onSelect();
        });

        return row;
    }

// ////////////////////////////////////////////////////////////////////////

    // Opens the menu below the anchor, or closes it when it is already
    // open for that anchor.
    // menuConfig:
    //   anchor:  the element the menu attaches to
    //   groups:  [{group, items: [{label, selected, onSelect}]}]
    zato.mapper.menu.toggle = function(menuConfig) {

        // A second click on the same anchor works as a toggle.
        if (activeAnchor === menuConfig.anchor) {
            close();
            return;
        }

        close();

        var menu = document.createElement('div');
        menu.className = 'zato-dropdown-menu';

        for (var groupIdx = 0; groupIdx < menuConfig.groups.length; groupIdx++) {
            var group = menuConfig.groups[groupIdx];

            if (groupIdx > 0) {
                var separator = document.createElement('div');
                separator.className = 'zato-dropdown-separator';
                menu.appendChild(separator);
            }

            var header = document.createElement('div');
            header.className = 'zato-dropdown-header';
            header.textContent = group.group;
            menu.appendChild(header);

            for (var itemIdx = 0; itemIdx < group.items.length; itemIdx++) {
                menu.appendChild(buildItem(group.items[itemIdx]));
            }
        }

        var rect = menuConfig.anchor.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top = (rect.bottom + 2) + 'px';
        menu.style.left = rect.left + 'px';

        document.body.appendChild(menu);

        activeMenu = menu;
        activeAnchor = menuConfig.anchor;
    };

// ////////////////////////////////////////////////////////////////////////

    // A click anywhere else closes the menu. The anchor is excluded so
    // its own click handler can toggle instead of reopening right away.
    $(document).on('mousedown', function(event) {

        if (activeMenu === null) {
            return;
        }

        var target = $(event.target);
        if (!target.closest('.zato-dropdown-menu').length && event.target !== activeAnchor) {
            close();
        }
    });

    // Escape closes the menu and does nothing else - the capture phase
    // stops the key before any other Escape behavior (like clearing the
    // mapping selection) reacts to the same press.
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && activeMenu !== null) {
            event.stopPropagation();
            close();
        }
    }, true);

})(jQuery);
