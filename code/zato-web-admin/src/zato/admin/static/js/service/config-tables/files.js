// Config tables - what is done to a file rather than to what is in it: adding
// one, renaming it, taking a copy of it and removing it. All of it is started from
// the listing's menu in menu.js, and the two buttons under the listing start the
// two that bring a file in. Bringing one in from your own machine is in upload.js.
//
// A rename happens on the file's own row, in place of its name. Every change goes
// out through persist, which is the single place the page talks to the server from.
//
// Each of these goes onto the row of events in stream.js, so Ctrl-Z takes back a file added,
// renamed or deleted as readily as it takes back a word typed into one. The two moves a file
// makes - out of the listing and back into it - are here as well, since going back through the
// row of events makes those moves too.

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
    downloadType: 'text/plain',

    // What is said when the server could not be reached at all
    persistErrorText: 'The server could not be reached'
};

// ////////////////////////////////////////////////////////////////////////

files.init = function() {

    tables.get('new').addEventListener('click', files.add);
};

// ////////////////////////////////////////////////////////////////////////
// Adding a file
// ////////////////////////////////////////////////////////////////////////

// A new file is an empty one, opened the moment it is added - what it turns out
// to be follows from what is typed into it.
files.add = function() {

    var name = files.buildFreeName();
    var table = files.buildTable(name, name + files.config.suffix, tables.state.userConfDirectory, '');

    // The listing gets the file once the server has it, so a file on screen is a file on disk
    files.persist('add', table, function() {

        tables.state.tableList.push(table);
        tables.state.initialContent[name] = '';

        // Adding a file is one more thing the page did, so it is taken back by the same key
        // that takes back the typing that follows it
        tables.stream.rememberAdd(table);

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
// Enter is the answer and Escape leaves the file as it was called. The field carries what the file
// is called on disk, suffix included, so a file that came in as one kind of file is renamed into
// another by typing the suffix it should have had.
files.startRename = function() {

    var table = tables.getCurrent();
    var row = files.getRow(table.name);
    var name = row.querySelector('.config-tables-file-name');

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'config-tables-file-rename';
    input.autocomplete = 'off';
    input.value = table.file_name;

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

files.applyRename = function(typed) {

    var table = tables.getCurrent();

    if(!typed) {
        tables.setStatus('A file needs a name', true);
        return;
    }

    var previousName = table.name;
    var previousFileName = table.file_name;
    var fileName = files.buildFileName(typed, previousFileName);
    var name = files.getStem(fileName);

    if(fileName === previousFileName) {
        tables.renderList();
        return;
    }

    if(tables.getByName(name)) {
        tables.setStatus('There is a file called ' + name + ' already', true);
        return;
    }

    files.moveTable(table, name, fileName, function() {

        // Renaming a file is one more thing the page did, so it is taken back by the same key
        // the typing around it is
        tables.stream.rememberRename(table, previousName, previousFileName);

        tables.setStatus('Renamed ' + previousName + ' to ' + name);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The file under another name, on disk and in the listing. The name is checked over before this
// is reached, whether it was typed on the row or is the one the file was called before a rename
// that has been taken back.
files.moveTable = function(table, name, fileName, onDone, onFail) {

    var previousName = table.name;
    var previousPath = table.path;

    var extra = {
        file_name: table.file_name,
        new_file_name: fileName
    };

    // The file is renamed on disk first, so what the listing says a file is called is
    // what it is called there
    files.persist('rename', table, function() {

        table.name = name;
        table.file_name = fileName;
        table.path = table.directory + fileName;

        tables.state.initialContent[name] = tables.state.initialContent[previousName];

        // Anything unsaved in the file is still unsaved, and what it held and where its caret
        // was are still its own, all of it now under the name the file goes by
        tables.draft.rename(previousPath, table);
        tables.edit.rename(previousPath, table);

        tables.select(name);

        onDone();

    }, extra, onFail);
};

// ////////////////////////////////////////////////////////////////////////

// What the file is called on disk after a rename - the text as typed when it carries a suffix of
// its own, and the suffix the file already had when it does not.
files.buildFileName = function(typed, previousFileName) {

    if(files.getSuffix(typed)) {
        return typed;
    }

    return typed + files.getSuffix(previousFileName);
};

// ////////////////////////////////////////////////////////////////////////

// The suffix a file is written in, if it says one.
files.getSuffix = function(fileName) {

    var out = '';
    var dotIdx = fileName.lastIndexOf('.');

    // A name that begins with a dot says nothing about what is in the file
    if(dotIdx > 0) {
        out = fileName.substring(dotIdx);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a service reaches the file by, which is what the file is called up to its first dot,
// that being what the server reads the name as too.
files.getStem = function(fileName) {

    var dotIdx = fileName.indexOf('.');

    if(dotIdx < 1) {
        return fileName;
    }

    return fileName.substring(0, dotIdx);
};

// ////////////////////////////////////////////////////////////////////////
// Deleting
// ////////////////////////////////////////////////////////////////////////

files.remove = function() {

    var table = tables.getCurrent();

    // Everything the file amounts to, read before it goes - it is all that is left of the file
    // once it is off disk, and it is what brings the file back as it stood
    var content = table.content;
    var draft = tables.draft.get(table);
    var caret = tables.edit.getCaret(table);

    files.persist('delete', table, function() {

        files.dropTable(table);

        // Deleting a file is one more thing the page did, and the one thing on the row that
        // carries the whole file with it
        tables.stream.rememberRemove(table, content, draft, caret);

        tables.setStatus('Deleted ' + table.path);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The file out of the listing, whatever took it off disk. What was typed into it and where its
// caret was go with it, both of those being about a file at that path, and there is none now.
files.dropTable = function(table) {

    var tableList = tables.state.tableList;
    var tableIdx = tableList.indexOf(table);

    tableList.splice(tableIdx, 1);

    tables.draft.forget(table);
    tables.edit.forget(table);

    tables.state.currentName = '';
    tables.renderList();

    // Whatever is now first takes the deleted file's place, and an empty
    // list leaves the right-hand side saying so
    var hasTable = tableList.length > 0;

    if(hasTable) {
        tables.select(tableList[0].name);
    }
    else {
        tables.renderEmpty();
    }
};

// ////////////////////////////////////////////////////////////////////////
// Downloading
// ////////////////////////////////////////////////////////////////////////

// A copy of the file as it is, taken from the listing's own menu, which is how a
// file too large for the browser is worked on - taken away and changed elsewhere.
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
// round trip to the server is made from. The page catches up with the server only
// once the server says the change is on disk, so what is on screen after that is
// what a service reading the same file gets. A change that did not go through says
// so on the line under the editor, and onFail is for whoever asked for it to hear
// that too - going back through the row of events waits on the answer either way.
files.persist = function(action, table, onDone, extra, onFail) {

    var data = {
        directory: table.directory,
        file_name: table.file_name,
        data: table.content
    };

    if(extra) {
        for(var key in extra) {
            data[key] = extra[key];
        }
    }

    tables.log.say('files.persist', {
        action: action,
        directory: data.directory,
        file_name: data.file_name,
        length: data.data.length,
        extra: JSON.stringify(extra === undefined ? {} : extra)
    });

    $.ajax({
        url: tables.state.persistUrl,
        type: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        data: JSON.stringify({action: action, data: data}),
        contentType: 'application/json',

        success: function(response) {

            tables.log.say('files.persist answered', {
                action: action,
                file_name: data.file_name,
                success: response.success,
                error: response.error
            });

            if(response.success) {
                onDone();
                return;
            }

            tables.setStatus(response.error, true);
            files.reportFailure(onFail);
        },

        error: function(request) {

            tables.log.say('files.persist failed', {
                action: action,
                file_name: data.file_name,
                status: request.status,
                error: files.buildErrorText(request)
            });

            tables.setStatus(files.buildErrorText(request), true);
            files.reportFailure(onFail);
        }
    });
};

// ////////////////////////////////////////////////////////////////////////

// Most changes have nothing to say beyond the line the reader is shown, so a failure is only
// passed on to whoever asked to hear about it.
files.reportFailure = function(onFail) {

    if(onFail !== undefined) {
        onFail();
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the server said went wrong. It answers with what it has to say about it, and
// a request that never got that far is said as the plain fact that it did not.
files.buildErrorText = function(request) {

    var out = files.config.persistErrorText;

    if(request.responseJSON) {
        out = request.responseJSON.error;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
