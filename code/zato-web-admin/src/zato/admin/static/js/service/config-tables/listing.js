// Config tables - the listing on the left.
//
// Every file the server reports, on a line of its own with what it is in front of
// its name and how much it holds after it. The directory is named above each run
// of files when they are not all in the same one. A click on a line opens the
// file, a right click on it opens the menu in menu.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;

// ////////////////////////////////////////////////////////////////////////

tables.renderList = function() {

    var list = tables.get('file-list');
    var tableList = tables.state.tableList;
    var showDirectories = tables.hasSeveralDirectories();
    var lastDirectory = '';

    list.textContent = '';

    for(var tableIdx = 0; tableIdx < tableList.length; tableIdx++) {

        var table = tableList[tableIdx];

        if(showDirectories) {

            if(table.directory !== lastDirectory) {
                list.appendChild(tables.buildGroupRow(table.directory));
                lastDirectory = table.directory;
            }
        }

        list.appendChild(tables.buildFileRow(table));
    }

    // The rows are new, so what the previous ones said about the file being looked at
    // is said again
    tables.renderModified();
};

// ////////////////////////////////////////////////////////////////////////

tables.hasSeveralDirectories = function() {

    var out = false;
    var tableList = tables.state.tableList;
    var hasTable = tableList.length > 0;

    if(hasTable) {

        var first = tableList[0];

        for(var tableIdx = 1; tableIdx < tableList.length; tableIdx++) {

            var table = tableList[tableIdx];

            if(table.directory !== first.directory) {
                out = true;
                break;
            }
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.buildGroupRow = function(directory) {

    var row = document.createElement('li');
    row.className = 'config-tables-file-group';
    row.textContent = directory;

    return row;
};

// ////////////////////////////////////////////////////////////////////////

tables.buildFileRow = function(table) {

    var row = document.createElement('li');
    row.className = 'config-tables-file-row';
    row.dataset.name = table.name;

    if(table.name === tables.state.currentName) {
        row.className = 'config-tables-file-row config-tables-file-selected';
    }

    // What the file is, badged in front of what it is called - in as many letters
    // as the column has room for, and in full under the cursor
    var badge = document.createElement('span');
    badge.className = 'zato-badge config-tables-file-badge ' + tables.config.kindBadgeClass[table.kind];
    badge.textContent = tables.config.kindBadge[table.kind];
    badge.title = tables.config.kindLabel[table.kind];
    row.appendChild(badge);

    var name = document.createElement('span');
    name.className = 'config-tables-file-name';
    name.textContent = table.file_name;

    // The star that says the file on screen is not the file on disk. It reads as part of
    // the name, so it goes inside it rather than beside it, and core.js is what brings it
    // out once the file has been typed into.
    var modified = document.createElement('span');
    modified.className = 'config-tables-file-modified';
    modified.textContent = '*';
    modified.hidden = true;
    name.appendChild(modified);

    row.appendChild(name);

    var count = document.createElement('span');
    count.className = 'config-tables-file-count';
    count.textContent = table.entry_count;
    row.appendChild(count);

    row.addEventListener('click', function() {
        tables.select(table.name);
    });

    return row;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
