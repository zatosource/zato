// Config tables - the listing's own menu, opened by a right click on it.
//
// Everything done to a file rather than to what is in it lives here - a right
// click on a file offers what can be done to that file, a right click anywhere
// else in the listing offers only what brings a new file in. The menu is the
// shared panel menu the IDE opens over a document, so the surface, the hotkey
// caps and the information pane are the ones from css/shared/panel-menu.css and
// css/shared/popup.css.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var menu = tables.menu;

// ////////////////////////////////////////////////////////////////////////

menu.config = {

    // The menu on screen, of which there is at most one
    elemId: 'config-tables-menu',

    // How close the menu may come to an edge of the screen
    edgeGap: 4,

    // What the header says when the menu is not about any one file
    rootTitle: 'Files',

    // The keys the actions answer to - a file's own actions first, so the two
    // that bring a file in keep their key whether a file was right-clicked or not.
    // Taking a copy of a file goes by the letter of its own name, since the row of
    // keys is where the other four are.
    renameKey: 'Q',
    deleteKey: 'W',
    addKey: 'E',
    uploadKey: 'R',
    downloadKey: 'D'
};

// ////////////////////////////////////////////////////////////////////////

menu.state = {

    // The file the menu is about, '' while it is about the listing itself
    name: ''
};

// ////////////////////////////////////////////////////////////////////////

menu.init = function() {

    // The whole column answers, not only the lines with a file on them, so the
    // room under a short listing is a place to right-click as well
    var browser = tables.get('browser');

    browser.addEventListener('contextmenu', function(event) {
        event.preventDefault();
        menu.openFromEvent(event);
    });
};

// ////////////////////////////////////////////////////////////////////////

// A right click on a file is about that file, which is also opened by it, and a
// right click on anything else in the listing is about the listing.
menu.openFromEvent = function(event) {

    var row = event.target.closest('.config-tables-file-row');
    var name = '';

    if(row) {
        name = row.dataset.name;
        tables.select(name);
    }

    menu.show(name, event.pageX, event.pageY);
};

// ////////////////////////////////////////////////////////////////////////

menu.show = function(name, x, y) {

    menu.close();
    menu.state.name = name;

    var itemList = menu.buildItemList(name);

    var elem = document.createElement('div');
    elem.id = menu.config.elemId;
    elem.className = 'zato-popup zato-panel-menu';

    elem.appendChild(menu.buildHeader(name));

    var body = document.createElement('div');
    body.className = 'grid-panel-body';

    var list = document.createElement('div');
    list.className = 'grid-panel-list';

    var info = document.createElement('div');
    info.className = 'grid-panel-info';

    menu.fillList(list, info, itemList);

    body.appendChild(list);
    body.appendChild(info);
    elem.appendChild(body);

    // On the page first, still invisible, so its size can be measured
    // against the viewport
    document.body.appendChild(elem);

    menu.installDrag(elem);
    menu.place(elem, x, y);
    menu.installDismiss(elem, itemList);

    // The visible class lands one frame later so the fade-in transition runs
    requestAnimationFrame(function() {
        elem.classList.add('zato-panel-menu-visible');
    });
};

// ////////////////////////////////////////////////////////////////////////

// The header names what the menu is about - the file's own path, or the
// directory the listing is of.
menu.buildHeader = function(name) {

    var header = document.createElement('div');
    header.className = 'zato-popup-header';
    header.appendChild($.fn.zato.popup.build_grip());

    var title = document.createElement('span');
    title.className = 'grid-panel-header-path';
    title.textContent = menu.config.rootTitle;

    if(name) {
        var table = tables.getByName(name);
        title.textContent = table.path;
    }

    header.appendChild(title);

    return header;
};

// ////////////////////////////////////////////////////////////////////////

// What the menu offers, in the order it offers it - a null is the line between
// what is done to the file right-clicked and what brings another file in.
menu.buildItemList = function(name) {

    var config = menu.config;
    var out = [];

    if(name) {

        var table = tables.getByName(name);
        var holds = tables.buildHolds(table.kind, table.entry_count, table.section_count);

        out.push({
            key: config.renameKey,
            label: 'Rename',
            isDestructive: false,
            action: tables.files.startRename,
            description: 'The new name is typed on the file\'s own line. Enter takes it, ' +
                'Escape keeps the current one.',
            details: [
                ['Called', table.file_name],
                ['In a service', tables.buildReference(table.name)]
            ]
        });

        out.push({
            key: config.downloadKey,
            label: 'Download',
            isDestructive: false,
            action: tables.files.download,
            description: 'A copy of the file as it is, onto your own machine.',
            details: [
                ['Called', table.file_name],
                ['Size', tables.formatSize(table.size)]
            ]
        });

        out.push({
            key: config.deleteKey,
            label: 'Delete',
            isDestructive: true,
            action: tables.files.remove,
            description: 'The file is removed.',
            details: [
                ['File', table.path],
                ['Holds', holds]
            ]
        });

        out.push(null);
    }

    out.push({
        key: config.addKey,
        label: 'New file',
        isDestructive: false,
        action: tables.files.add,
        description: 'An empty file, opened for editing right away.',
        details: [
            ['Goes into', tables.state.userConfDirectory]
        ]
    });

    out.push({
        key: config.uploadKey,
        label: 'Upload file',
        isDestructive: false,
        action: tables.upload.open,
        description: 'A file from your own machine, checked before it is put in place.',
        details: [
            ['Goes into', tables.state.userConfDirectory]
        ]
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The action list on the left and the pane on the right that tells the story of
// whichever action the cursor is on, the first one from the start.
menu.fillList = function(list, info, itemList) {

    for(var itemIdx = 0; itemIdx < itemList.length; itemIdx++) {

        var item = itemList[itemIdx];

        if(item === null) {
            var separator = document.createElement('div');
            separator.className = 'grid-panel-separator';
            list.appendChild(separator);
            continue;
        }

        list.appendChild(menu.buildEntry(list, info, item));
    }

    var first = menu.getFirstItem(itemList);
    menu.highlight(list, info, first);
};

// ////////////////////////////////////////////////////////////////////////

menu.buildEntry = function(list, info, item) {

    var entry = document.createElement('div');
    entry.className = 'grid-panel-item';
    entry.dataset.key = item.key;

    if(item.isDestructive) {
        entry.className = 'grid-panel-item grid-panel-item-destructive';
    }

    var key = document.createElement('span');
    key.className = 'grid-panel-item-key';
    key.textContent = item.key;
    entry.appendChild(key);

    var label = document.createElement('span');
    label.className = 'grid-panel-item-label';
    label.textContent = item.label;
    entry.appendChild(label);

    entry.addEventListener('mouseenter', function() {
        menu.highlight(list, info, item);
    });

    entry.addEventListener('click', function() {
        menu.run(item);
    });

    return entry;
};

// ////////////////////////////////////////////////////////////////////////

// The action the cursor or a hotkey has landed on - the row it is on and the
// pane that describes it move together.
menu.highlight = function(list, info, item) {

    var entryList = list.querySelectorAll('.grid-panel-item');

    for(var entryIdx = 0; entryIdx < entryList.length; entryIdx++) {

        var entry = entryList[entryIdx];
        var isCurrent = entry.dataset.key === item.key;

        entry.classList.toggle('current', isCurrent);
    }

    info.textContent = '';

    var title = document.createElement('div');
    title.className = 'grid-panel-info-title';
    title.textContent = item.label;
    info.appendChild(title);

    var description = document.createElement('div');
    description.className = 'grid-panel-info-desc';
    description.textContent = item.description;
    info.appendChild(description);

    for(var detailIdx = 0; detailIdx < item.details.length; detailIdx++) {

        var detail = item.details[detailIdx];

        var row = document.createElement('div');
        row.className = 'grid-panel-detail';

        var name = document.createElement('span');
        name.className = 'grid-panel-detail-name';
        name.textContent = detail[0];
        row.appendChild(name);

        var value = document.createElement('span');
        value.className = 'grid-panel-detail-value';
        value.textContent = detail[1];
        row.appendChild(value);

        info.appendChild(row);
    }
};

// ////////////////////////////////////////////////////////////////////////

menu.getFirstItem = function(itemList) {

    var out = null;

    for(var itemIdx = 0; itemIdx < itemList.length; itemIdx++) {

        var item = itemList[itemIdx];

        if(item !== null) {
            out = item;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// An action closes the menu before it runs, so whatever it opens on the page is
// what is left on screen.
menu.run = function(item) {

    menu.close();
    item.action();
};

// ////////////////////////////////////////////////////////////////////////

// The menu opens at the cursor, pulled back from whichever edge it would
// otherwise run past.
menu.place = function(elem, x, y) {

    var edgeGap = menu.config.edgeGap;

    var viewportLeft = window.scrollX;
    var viewportTop = window.scrollY;
    var viewportRight = viewportLeft + window.innerWidth;
    var viewportBottom = viewportTop + window.innerHeight;

    if(x + elem.offsetWidth > viewportRight) {
        x = viewportRight - elem.offsetWidth - edgeGap;
    }

    if(y + elem.offsetHeight > viewportBottom) {
        y = viewportBottom - elem.offsetHeight - edgeGap;
    }

    if(x < viewportLeft) {
        x = viewportLeft + edgeGap;
    }

    if(y < viewportTop) {
        y = viewportTop + edgeGap;
    }

    elem.style.left = x + 'px';
    elem.style.top = y + 'px';
};

// ////////////////////////////////////////////////////////////////////////

// Any of the menu's own surface drags it, the actions keep their own behaviour.
menu.installDrag = function(elem) {

    $.fn.zato.popup.install_drag(elem, {

        should_ignore: function(target) {
            var out = Boolean(target.closest('.grid-panel-item'));
            return out;
        },

        on_start: function() {
            var out = {x: elem.offsetLeft, y: elem.offsetTop};
            return out;
        },

        on_move: function(x, y) {
            elem.style.left = x + 'px';
            elem.style.top = y + 'px';
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// A press anywhere else, Escape, or an action's own key - the hotkeys work for
// as long as the menu is open and nothing else does.
menu.installDismiss = function(elem, itemList) {

    $(document).on('mousedown.config-tables-menu', function(event) {

        var isInside = Boolean(event.target.closest('#' + menu.config.elemId));

        if(!isInside) {
            menu.close();
        }
    });

    $(document).on('keydown.config-tables-menu', function(event) {

        if(event.key === 'Escape') {
            menu.close();
            return;
        }

        var pressed = event.key.toUpperCase();

        for(var itemIdx = 0; itemIdx < itemList.length; itemIdx++) {

            var item = itemList[itemIdx];

            if(item !== null && item.key === pressed) {

                // The key belongs to the menu, not to whatever the action
                // brings up and focuses next
                event.preventDefault();

                menu.run(item);
                return;
            }
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

menu.close = function() {

    var elem = document.getElementById(menu.config.elemId);

    if(elem) {
        elem.remove();
    }

    $(document).off('mousedown.config-tables-menu');
    $(document).off('keydown.config-tables-menu');
    $(document).off('mousemove.zato-popup-drag');
    $(document).off('mouseup.zato-popup-drag');
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
