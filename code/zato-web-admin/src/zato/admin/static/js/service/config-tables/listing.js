// Config tables - the listing on the left.
//
// Every file the server reports, on a line of its own with what it is in front of
// its name and how much it holds after it. The directory is named above each run
// of files when they are not all in the same one. A click on a line opens the
// file, a right click on it opens the menu in menu.js.
//
// A directory holds more than the files a service reads through self.config, so the listing keeps
// to those unless Show all is switched on in that menu. The file being looked at is on the list
// either way - a file just brought in from your own machine is one to rename, not one to lose
// sight of.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

tables.renderList = function() {

    var list = tables.get('file-list');
    var tableList = tables.getShownList();

    var showDirectories = tables.hasSeveralDirectories(tableList);
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

// The files the listing has a line for, in the order they are read in.
tables.getShownList = function() {

    tables.sortList();

    var tableList = tables.state.tableList;
    var out = [];

    for(var tableIdx = 0; tableIdx < tableList.length; tableIdx++) {

        var table = tableList[tableIdx];

        if(tables.isShown(table)) {
            out.push(table);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the file is on the list - the ones a service reads always are, everything else in the
// directory is while Show all is on, and so is the file being looked at whatever it is called.
tables.isShown = function(table) {

    if(tables.state.isShowingAll) {
        return true;
    }

    if(table.name === tables.state.currentName) {
        return true;
    }

    var suffix = tables.files.getSuffix(table.file_name).toLowerCase();
    var out = tables.config.configSuffixList.indexOf(suffix) !== -1;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the listing has a line for the other files in the directory, which is off for anyone
// opening the page for the first time and stays as it was left after that.
tables.readShowAll = function() {

    var out = window.localStorage.getItem(tables.config.showAllStorageKey) === '1';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.toggleShowAll = function() {

    var state = tables.state;

    state.isShowingAll = !state.isShowingAll;
    window.localStorage.setItem(tables.config.showAllStorageKey, state.isShowingAll ? '1' : '0');

    log.say('tables.toggleShowAll', {
        isShowingAll: state.isShowingAll,
        tableCount: state.tableList.length,
        shownCount: tables.getShownList().length
    });

    tables.renderList();
};

// ////////////////////////////////////////////////////////////////////////

// The files stand in the order a listing is read in - the directory they are in, then their own
// name - rather than in the order the server happened to report them. This is where the order is
// settled, so a file added, renamed, uploaded or brought back by going back through what the page
// did is on the line its name puts it on, without anything that moves a file having to say so.
tables.sortList = function() {

    tables.state.tableList.sort(function(left, right) {

        if(left.directory !== right.directory) {
            return left.directory.localeCompare(right.directory);
        }

        return left.file_name.localeCompare(right.file_name);
    });
};

// ////////////////////////////////////////////////////////////////////////

tables.hasSeveralDirectories = function(tableList) {

    var out = false;
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
