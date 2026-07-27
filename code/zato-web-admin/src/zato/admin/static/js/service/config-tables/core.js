// Config tables - the page under Services, where the config files a service
// reads through self.config are browsed and changed.
//
// The page is rendered by zato/service/config-tables.html. The files are listed
// on the left, the one being looked at fills the rest of the page. This file
// holds the state, the list and the editor around the textarea. The reading of a
// file is in parse.js, the words the page puts on screen in text.js, the Try it
// strip in invoker.js and what is done to the file itself in files.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

tables.config = {

    // Every element id on the page starts with this
    idPrefix: 'config-tables-',

    // The section a code list keeps its codes under - a file having it is a
    // code list, a file with any other section is a mapping set
    codesSection: 'codes',

    // What a file of each kind is called on screen, and what one entry of it is
    kindLabel: {codes: 'code list', mappings: 'mapping set'},
    entryNoun: {codes: 'code', mappings: 'mapping'},

    // What the status line says once something went through
    savedMessage: 'Saved',
    checkedMessage: 'Reads fine',

    // What the right-hand side says while no file is open
    emptyMessage: 'Pick a file on the left, or add one.',

    // The class the status line wears - plain, once something went through, and
    // once something did not
    statusPlain: 'config-tables-status',
    statusOK: 'config-tables-status config-tables-status-ok',
    statusError: 'config-tables-status config-tables-status-error',

    // The units a file size is given in, smallest first, and what each step is
    sizeUnits: ['B', 'KB', 'MB', 'GB'],
    sizeStep: 1024
};

// ////////////////////////////////////////////////////////////////////////

tables.state = {

    // Every file on the server, in the order it reports them
    tableList: [],

    // The directories a file may be uploaded into
    directoryList: [],

    // Where the files live
    userConfDirectory: '',

    // The file the page is currently about, '' while none is open
    currentName: '',

    // How large a file may be before it is edited outside the browser
    maxEditableSize: 0,

    // What every file held when the page was opened, which is what Restore
    // goes back to
    initialContent: {}
};

// ////////////////////////////////////////////////////////////////////////

tables.init = function(inputConfig) {

    var state = tables.state;

    state.tableList = inputConfig.table_list;
    state.directoryList = inputConfig.directory_list;
    state.userConfDirectory = inputConfig.user_conf_directory;
    state.maxEditableSize = inputConfig.max_editable_size;

    tables.rememberInitialContent();

    tables.get('root').textContent = state.userConfDirectory;
    tables.get('empty').textContent = tables.config.emptyMessage;

    tables.wire();
    tables.files.init();
    tables.invoker.init();

    tables.renderList();

    // The page opens on something to read rather than on an empty right-hand side
    var hasTable = state.tableList.length > 0;

    if(hasTable) {
        var first = state.tableList[0];
        tables.select(first.name);
    }
    else {
        tables.renderEmpty();
    }
};

// ////////////////////////////////////////////////////////////////////////

tables.wire = function() {

    tables.get('check').addEventListener('click', tables.check);
    tables.get('save').addEventListener('click', tables.save);
    tables.get('restore').addEventListener('click', tables.restore);
};

// ////////////////////////////////////////////////////////////////////////

tables.rememberInitialContent = function() {

    var state = tables.state;

    for(var tableIdx = 0; tableIdx < state.tableList.length; tableIdx++) {

        var table = state.tableList[tableIdx];
        state.initialContent[table.name] = table.content;
    }
};

// ////////////////////////////////////////////////////////////////////////

// One element of the page by the part of its id that is its own.
tables.get = function(name) {

    var out = document.getElementById(tables.config.idPrefix + name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.getByName = function(name) {

    var out = null;
    var tableList = tables.state.tableList;

    for(var tableIdx = 0; tableIdx < tableList.length; tableIdx++) {

        var table = tableList[tableIdx];

        if(table.name === name) {
            out = table;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.getCurrent = function() {

    var out = tables.getByName(tables.state.currentName);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

tables.isMappingSet = function(table) {

    var out = table.kind === 'mappings';
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the file turns out to be, read off the file itself - the section the
// codes go under is what tells a code list from a mapping set.
tables.deriveKind = function(parsed) {

    var out = 'mappings';
    var section = parse.findSection(parsed, tables.config.codesSection);

    if(section) {
        out = 'codes';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The browser
// ////////////////////////////////////////////////////////////////////////

// Every file, in the order the server reports them, with the directory named
// above each run of them when they are not all in the same one.
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

    if(table.name === tables.state.currentName) {
        row.className = 'config-tables-file-row config-tables-file-selected';
    }

    var name = document.createElement('span');
    name.className = 'config-tables-file-name';
    name.textContent = table.file_name;
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
// The file being looked at
// ////////////////////////////////////////////////////////////////////////

tables.select = function(name) {

    tables.state.currentName = name;

    tables.files.hideInlineRows();
    tables.setStatus('');
    tables.renderList();
    tables.renderEditor();
};

// ////////////////////////////////////////////////////////////////////////

tables.renderEmpty = function() {

    tables.get('empty').hidden = false;
    tables.get('editor').hidden = true;
};

// ////////////////////////////////////////////////////////////////////////

tables.renderEditor = function() {

    var table = tables.getCurrent();

    tables.get('empty').hidden = true;
    tables.get('editor').hidden = false;

    tables.get('file-name').textContent = table.file_name;
    tables.renderInfo(table);

    var content = tables.get('content');
    content.value = table.content;
    content.readOnly = !table.is_editable;

    // A file too large for the browser is taken away, changed and brought back,
    // so it says so where the buttons that would save it are
    tables.get('outside-text').textContent = tables.buildOutsideText(table);
    tables.get('outside').hidden = table.is_editable;
    tables.get('editor-buttons').hidden = !table.is_editable;

    tables.invoker.render(table);
};

// ////////////////////////////////////////////////////////////////////////

// The three lines above the file - how a service reaches it, what it holds and
// where it is.
tables.renderInfo = function(table) {

    tables.get('kind').textContent = tables.config.kindLabel[table.kind];
    tables.get('reference').textContent = tables.buildReference(table.name);
    tables.get('holds').textContent = tables.buildHolds(table.kind, table.entry_count, table.section_count);
    tables.get('path').textContent = table.path + ', ' + tables.formatSize(table.size);
};

// ////////////////////////////////////////////////////////////////////////

// What the file on screen reads as, without saving it - the count of what is in
// it, or the first line that does not parse.
tables.check = function() {

    var content = tables.get('content').value;
    var parsed = parse.read(content);

    if(parsed.errorText) {
        tables.setStatus(tables.buildErrorText(parsed), true);
        return;
    }

    tables.setStatus(tables.config.checkedMessage + ', ' + tables.buildHoldsText(parsed));
};

// ////////////////////////////////////////////////////////////////////////

// The file on screen, saved. A file that does not parse is not written anywhere
// and the line says which line stopped it.
tables.save = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var parsed = parse.read(content);

    if(parsed.errorText) {
        tables.setStatus(tables.buildErrorText(parsed), true);
        return;
    }

    tables.applyContents(table, content, parsed);

    tables.files.persist('save', table, function() {
        tables.setStatus(tables.config.savedMessage);
        tables.renderInfo(table);
        tables.renderList();
        tables.invoker.refresh(table);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The file as it was when the page was opened, back in the editor. Nothing is
// saved by this - what is on the server stays as it is until Save is pressed.
tables.restore = function() {

    var table = tables.getCurrent();

    tables.get('content').value = tables.state.initialContent[table.name];
    tables.setStatus('');
};

// ////////////////////////////////////////////////////////////////////////

// What the file says about itself once it has changed - its size, what kind of
// table it is now and how much it holds all come off the file itself.
tables.applyContents = function(table, content, parsed) {

    table.content = content;
    table.size = content.length;
    table.is_editable = content.length <= tables.state.maxEditableSize;
    table.kind = tables.deriveKind(parsed);
    table.section_count = parsed.sectionList.length;
    table.entry_count = parsed.entryCount;
};

// ////////////////////////////////////////////////////////////////////////

// The line under the editor, which says what has just happened and nothing else.
tables.setStatus = function(text, isError) {

    var status = tables.get('status');
    var config = tables.config;

    status.textContent = text;

    if(isError) {
        status.className = config.statusError;
    }
    else {
        if(text) {
            status.className = config.statusOK;
        }
        else {
            status.className = config.statusPlain;
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
