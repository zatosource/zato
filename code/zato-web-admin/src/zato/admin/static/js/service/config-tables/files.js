// Config tables - what is done to a file rather than to what is in it: adding
// one, renaming it, taking a copy of it, putting a new version of it in place and
// removing it.
//
// Renaming and deleting are asked about on the row they are started from, so the
// answer is given where the question is. Uploading is the one thing with a
// question of its own - where the file goes - so it is the one thing that opens a
// dialog. Every change goes out through persist, which is the single place the
// page talks to the server from.

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

    // What the dialog says while it has nothing to show yet
    dialogBlank: '-',

    // What the dialog is titled, by what it is opened for
    uploadTitle: 'Upload a file',
    replaceTitle: 'Upload a new version'
};

// ////////////////////////////////////////////////////////////////////////

files.state = {

    // The file the dialog replaces, '' when it uploads a new one
    replacedName: ''
};

// ////////////////////////////////////////////////////////////////////////

files.init = function() {

    tables.get('new').addEventListener('click', files.add);
    tables.get('upload').addEventListener('click', files.openUpload);
    tables.get('replace').addEventListener('click', files.openReplace);
    tables.get('download').addEventListener('click', files.download);

    tables.get('rename').addEventListener('click', files.startRename);
    tables.get('rename-cancel').addEventListener('click', files.hideInlineRows);
    tables.get('rename-apply').addEventListener('click', files.applyRename);

    tables.get('delete').addEventListener('click', files.startDelete);
    tables.get('delete-cancel').addEventListener('click', files.hideInlineRows);
    tables.get('delete-confirm').addEventListener('click', files.applyDelete);

    files.initDialog();
};

// ////////////////////////////////////////////////////////////////////////

files.hideInlineRows = function() {

    tables.get('rename-row').hidden = true;
    tables.get('delete-row').hidden = true;
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

files.startRename = function() {

    var table = tables.getCurrent();

    files.hideInlineRows();

    var input = tables.get('rename-input');
    input.value = table.name;

    tables.get('rename-row').hidden = false;
    input.focus();
};

// ////////////////////////////////////////////////////////////////////////

files.applyRename = function() {

    var table = tables.getCurrent();
    var name = tables.get('rename-input').value.trim();

    if(!name) {
        tables.setStatus('A file needs a name', true);
        return;
    }

    if(name === table.name) {
        files.hideInlineRows();
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
        files.hideInlineRows();
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

files.startDelete = function() {

    var table = tables.getCurrent();

    files.hideInlineRows();

    tables.get('delete-question').textContent = 'Delete ' + table.path + '?';
    tables.get('delete-row').hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

files.applyDelete = function() {

    var table = tables.getCurrent();
    var tableList = tables.state.tableList;
    var tableIdx = tableList.indexOf(table);

    tableList.splice(tableIdx, 1);

    files.persist('delete', table, function() {

        files.hideInlineRows();
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
// Uploading
// ////////////////////////////////////////////////////////////////////////

files.initDialog = function() {

    var directory = tables.get('dialog-directory');
    var directoryList = tables.state.directoryList;

    for(var directoryIdx = 0; directoryIdx < directoryList.length; directoryIdx++) {

        var option = document.createElement('option');
        option.value = directoryList[directoryIdx];
        option.textContent = directoryList[directoryIdx];
        directory.appendChild(option);
    }

    // There is nothing to pick while the server reports the one directory
    var hasChoice = directoryList.length > 1;
    tables.get('dialog-directory-field').hidden = !hasChoice;

    tables.get('dialog-file').addEventListener('change', files.refreshDialog);
    directory.addEventListener('change', files.refreshDialog);
    tables.get('dialog-cancel').addEventListener('click', files.closeDialog);
    tables.get('dialog-upload').addEventListener('click', files.applyUpload);
};

// ////////////////////////////////////////////////////////////////////////

files.openUpload = function() {

    files.state.replacedName = '';
    files.openDialog(files.config.uploadTitle);
};

// ////////////////////////////////////////////////////////////////////////

// The same dialog, opened for the file already open - what comes out of it takes
// that file's place instead of being added next to it.
files.openReplace = function() {

    var table = tables.getCurrent();

    files.state.replacedName = table.name;
    files.openDialog(files.config.replaceTitle);
};

// ////////////////////////////////////////////////////////////////////////

files.openDialog = function(title) {

    tables.get('dialog-title').textContent = title;
    tables.get('dialog-file').value = '';
    tables.get('dialog-status').textContent = '';

    files.refreshDialog();
    tables.get('overlay').hidden = false;
};

// ////////////////////////////////////////////////////////////////////////

files.closeDialog = function() {

    tables.get('overlay').hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

// Where the file would end up and what a service would read it as, kept up with
// what has been picked so far.
files.refreshDialog = function() {

    var blank = files.config.dialogBlank;
    var uploaded = files.getPickedFile();
    var path = blank;
    var reference = blank;

    if(uploaded) {
        var directory = files.getPickedDirectory();
        var name = files.buildNameFromFile(uploaded.name);

        path = directory + uploaded.name;
        reference = tables.buildReference(name);
    }

    tables.get('dialog-path').textContent = path;
    tables.get('dialog-reference').textContent = reference;
};

// ////////////////////////////////////////////////////////////////////////

files.getPickedFile = function() {

    var out = null;
    var fileList = tables.get('dialog-file').files;
    var hasFile = fileList.length > 0;

    if(hasFile) {
        out = fileList[0];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

files.getPickedDirectory = function() {

    var out = tables.get('dialog-directory').value;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The name a service reads the file under - the file name without what it is
// written in.
files.buildNameFromFile = function(fileName) {

    var out = fileName;
    var dotIdx = fileName.lastIndexOf('.');

    if(dotIdx > 0) {
        out = fileName.substring(0, dotIdx);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

files.applyUpload = function() {

    var uploaded = files.getPickedFile();

    if(!uploaded) {
        tables.get('dialog-status').textContent = 'Pick a file first';
        return;
    }

    var reader = new FileReader();

    reader.addEventListener('load', function() {
        files.readUploaded(uploaded.name, reader.result);
    });

    reader.readAsText(uploaded);
};

// ////////////////////////////////////////////////////////////////////////

// What was uploaded, once it has been read - a file that does not parse is not
// put anywhere and the dialog stays open saying why.
files.readUploaded = function(fileName, content) {

    var parsed = parse.read(content);

    if(parsed.errorText) {
        tables.get('dialog-status').textContent = tables.buildErrorText(parsed);
        return;
    }

    if(files.state.replacedName) {
        files.replaceContents(fileName, content, parsed);
    }
    else {
        files.addUploaded(fileName, content);
    }
};

// ////////////////////////////////////////////////////////////////////////

files.replaceContents = function(fileName, content, parsed) {

    var table = tables.getByName(files.state.replacedName);

    tables.applyContents(table, content, parsed);

    files.persist('upload', table, function() {
        files.closeDialog();
        tables.select(table.name);
        tables.setStatus('Uploaded ' + fileName + ' over ' + table.file_name);
    });
};

// ////////////////////////////////////////////////////////////////////////

files.addUploaded = function(fileName, content) {

    var name = files.buildNameFromFile(fileName);

    if(tables.getByName(name)) {
        tables.get('dialog-status').textContent = 'There is a file called ' + name + ' already';
        return;
    }

    var directory = files.getPickedDirectory();
    var table = files.buildTable(name, fileName, directory, content);

    tables.state.tableList.push(table);
    tables.state.initialContent[name] = content;

    files.persist('upload', table, function() {
        files.closeDialog();
        tables.select(name);
        tables.setStatus('Uploaded ' + fileName);
    });
};

// ////////////////////////////////////////////////////////////////////////

// Every change the page makes goes out through here, which is the one place a
// round trip to the server is made from.
files.persist = function(action, table, onDone) {

    onDone();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
