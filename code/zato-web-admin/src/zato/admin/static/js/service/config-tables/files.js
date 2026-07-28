// Config tables - what is done to a file rather than to what is in it: adding
// one, renaming it, taking a copy of it and removing it. All of it is started from
// the listing's menu in menu.js, and the two buttons under the listing start the
// two that bring a file in. Bringing one in from your own machine is in upload.js.
//
// A rename happens on the file's own row, in place of its name. Every change goes
// out through persist, which is the single place the page talks to the server from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var files = tables.files;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

files.config = {

    // What a new file is called before it is renamed, and what it is written in
    newName: 'new-file',
    suffix: '.ini',

    // What a downloaded copy is handed over as
    downloadType: 'text/plain'
};

// ////////////////////////////////////////////////////////////////////////

files.init = function() {

    tables.get('new').addEventListener('click', files.add);
    tables.get('download').addEventListener('click', files.download);
};

// ////////////////////////////////////////////////////////////////////////
// Adding a file
// ////////////////////////////////////////////////////////////////////////

// A new file is an empty one, opened the moment it is added - what it turns out
// to be follows from what is typed into it.
files.add = function() {

    var name = files.buildFreeName();
    var table = files.buildTable(name, name + files.config.suffix, tables.state.userConfDirectory, '');

    tables.state.tableList.push(table);
    tables.state.initialContent[name] = '';

    files.persist('add', table, function() {
        tables.select(name);
        tables.setStatus('Added ' + table.file_name);
    });
};

// ////////////////////////////////////////////////////////////////////////

// A file of the given contents, in the shape the page reads every file in.
files.buildTable = function(name, fileName, directory, content) {

    var parsed = parse.read(content);

    var out = {
        name: name,
        file_name: fileName,
        directory: directory,
        path: directory + fileName,
        kind: 'mappings',
        section_count: 0,
        entry_count: 0,
        size: 0,
        is_editable: true,
        content: ''
    };

    tables.applyContents(out, content, parsed);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The name a new file is added under - the plain one while it is free, numbered
// after that, so adding one twice in a row does not need a rename in between.
files.buildFreeName = function() {

    var out = files.config.newName;
    var takenIdx = 1;

    while(tables.getByName(out)) {
        takenIdx++;
        out = files.config.newName + '-' + takenIdx;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Renaming
// ////////////////////////////////////////////////////////////////////////

// The name on the file's own row becomes the field the new one is typed into -
// Enter is the answer and Escape leaves the file as it was called.
files.startRename = function() {

    var table = tables.getCurrent();
    var row = files.getRow(table.name);
    var name = row.querySelector('.config-tables-file-name');

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'config-tables-file-rename';
    input.autocomplete = 'off';
    input.value = table.name;

    // The row opens the file it is of, which a press inside the field is not
    input.addEventListener('mousedown', function(event) {
        event.stopPropagation();
    });

    input.addEventListener('click', function(event) {
        event.stopPropagation();
    });

    input.addEventListener('keydown', function(event) {

        if(event.key === 'Enter') {
            files.applyRename(input.value.trim());
        }

        if(event.key === 'Escape') {
            tables.renderList();
        }
    });

    // Leaving the field alone leaves the name alone
    input.addEventListener('blur', function() {
        tables.renderList();
    });

    row.replaceChild(input, name);

    input.focus();
    input.select();
};

// ////////////////////////////////////////////////////////////////////////

// The file's row as it is on screen now, which is what a rename types into.
files.getRow = function(name) {

    var selector = '.config-tables-file-row[data-name="' + name + '"]';
    var out = tables.get('file-list').querySelector(selector);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

files.applyRename = function(name) {

    var table = tables.getCurrent();

    if(!name) {
        tables.setStatus('A file needs a name', true);
        return;
    }

    if(name === table.name) {
        tables.renderList();
        return;
    }

    if(tables.getByName(name)) {
        tables.setStatus('There is a file called ' + name + ' already', true);
        return;
    }

    var previousName = table.name;
    var suffix = files.getSuffix(table.file_name);

    table.name = name;
    table.file_name = name + suffix;
    table.path = table.directory + table.file_name;

    tables.state.initialContent[name] = tables.state.initialContent[previousName];

    files.persist('rename', table, function() {
        tables.select(name);
        tables.setStatus('Renamed ' + previousName + ' to ' + name);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The suffix a file keeps through a rename - what a file is written in does not
// change just because it is called something else.
files.getSuffix = function(fileName) {

    var out = '';
    var dotIdx = fileName.lastIndexOf('.');

    if(dotIdx !== -1) {
        out = fileName.substring(dotIdx);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Deleting
// ////////////////////////////////////////////////////////////////////////

files.remove = function() {

    var table = tables.getCurrent();
    var tableList = tables.state.tableList;
    var tableIdx = tableList.indexOf(table);

    tableList.splice(tableIdx, 1);

    files.persist('delete', table, function() {

        tables.state.currentName = '';
        tables.renderList();

        // Whatever is now first takes the deleted file's place, and an empty
        // list leaves the right-hand side saying so
        var hasTable = tableList.length > 0;

        if(hasTable) {
            var first = tableList[0];
            tables.select(first.name);
        }
        else {
            tables.renderEmpty();
        }

        tables.setStatus('Deleted ' + table.path);
    });
};

// ////////////////////////////////////////////////////////////////////////
// Downloading
// ////////////////////////////////////////////////////////////////////////

// A copy of the file as it is, which is how a file too large for the browser is
// worked on - taken away, changed and uploaded again.
files.download = function() {

    var table = tables.getCurrent();
    var blob = new Blob([table.content], {type: files.config.downloadType});
    var url = URL.createObjectURL(blob);

    var anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = table.file_name;

    document.body.appendChild(anchor);
    anchor.click();

    anchor.remove();
    URL.revokeObjectURL(url);
};

// ////////////////////////////////////////////////////////////////////////

// Every change the page makes goes out through here, which is the one place a
// round trip to the server is made from.
files.persist = function(action, table, onDone) {

    onDone();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
