// Config tables - the page under Services, where the config files a service
// reads through self.config are browsed and changed.
//
// The page is rendered by zato/service/config-tables.html - the files on the left,
// the one being looked at in the middle, the column that runs a value through it on
// the right. This file holds the state and the editor around the textarea. The
// listing itself is in listing.js, the two lines that size the columns in split.js,
// the reading of a file in parse.js, the words the page puts on screen in text.js,
// the Translate column in invoker.js, the drawing it answers a mapping set with in
// flow.js, the line of the file a part of that drawing stands for in trace.js, where
// the reader is in url.js, the listing's menu in menu.js, what is done to the file
// itself in files.js and the bringing in of one in upload.js.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

tables.config = {

    // Every element id on the page starts with this
    idPrefix: 'config-tables-',

    // The table a code list keeps its codes under - a file that holds codes under it is a
    // code list, and every other file is a mapping set
    codesSection: 'codes',

    // What a file of each kind is called on screen, what its badge in the listing
    // says and which of the shared badge colors it wears, and what one entry of it is
    kindLabel: {codes: 'code list', mappings: 'mapping set'},
    kindBadge: {codes: 'codes', mappings: 'maps'},
    kindBadgeClass: {codes: 'zato-badge-green', mappings: 'zato-badge-amber'},
    entryNoun: {codes: 'code', mappings: 'mapping'},

    // What the status line says once something went through, and how long it says it for -
    // what went through is done with, while what did not stays until it is cleared
    savedMessage: 'Saved',
    checkedMessage: 'OK',
    statusShownMS: 2600,

    // What the drawing says where the codes of a table would be when there is no mapping
    // to draw - the few words a chip has room for, while the answer as text says which
    // of the two ways it came about
    flowNoMapMessage: 'No such map in this file',

    // The words that go with the two drops of the drawing - the file maps what came in to
    // the value it holds, and the tables on the other side are the ones using that value
    flowMapsToLabel: 'maps to',
    flowUsedByLabel: 'used by',

    // The class the status line wears - plain, once something went through, and
    // once something did not
    statusPlain: 'config-tables-status',
    statusOK: 'config-tables-status config-tables-status-ok',
    statusError: 'config-tables-status config-tables-status-error',

    // The units a file size is given in, smallest first, and what each step is
    sizeUnits: ['B', 'KB', 'MB', 'GB'],
    sizeStep: 1024,

    // The class the overlay behind the editor wears for a file the browser does
    // not edit in place
    backdropReadOnly: 'highlight-backdrop-readonly'
};

// ////////////////////////////////////////////////////////////////////////

tables.state = {

    // Every file on the server, in the order it reports them
    tableList: [],

    // The directories a file may be uploaded into
    directoryList: [],

    // Where the files live
    userConfDirectory: '',

    // Where a change to a file is sent
    persistUrl: '',

    // The file the page is currently about, '' while none is open
    currentName: '',

    // How large a file may be before it is edited outside the browser
    maxEditableSize: 0,

    // What every file held when the page was opened, which is what Restore
    // goes back to
    initialContent: {},

    // What takes the status line away again, 0 while there is nothing on it to take away
    statusTimer: 0
};

// ////////////////////////////////////////////////////////////////////////

tables.init = function(inputConfig) {

    var state = tables.state;

    state.tableList = inputConfig.table_list;
    state.directoryList = inputConfig.directory_list;
    state.userConfDirectory = inputConfig.user_conf_directory;
    state.maxEditableSize = inputConfig.max_editable_size;
    state.persistUrl = inputConfig.persist_url;

    tables.rememberInitialContent();

    // Only ever says why the files could not be read, and says nothing at all when they could
    tables.get('empty').textContent = inputConfig.error;

    tables.wire();
    tables.files.init();
    tables.upload.init();
    tables.invoker.init();
    tables.menu.init();
    tables.url.init();

    tables.renderList();
    tables.open();
};

// ////////////////////////////////////////////////////////////////////////

// The file the page opens on - the one the address names, so a reload lands where the
// reader left off, and otherwise the first one there is. What was being translated and how
// far each column was scrolled come back with it.
tables.open = function() {

    var state = tables.state;
    var name = tables.url.readFileName();

    if(!name && state.tableList.length) {
        name = state.tableList[0].name;
    }

    if(!name) {
        tables.renderEmpty();
        return;
    }

    tables.select(name);
    tables.url.applyTranslate();
    tables.url.applyScroll();
};

// ////////////////////////////////////////////////////////////////////////

tables.wire = function() {

    tables.get('check').addEventListener('click', tables.check);
    tables.get('save').addEventListener('click', tables.save);
    tables.get('restore').addEventListener('click', tables.restore);

    // What did not go through stays on screen until it is read, so a press on it is
    // what takes it away
    tables.get('status').addEventListener('click', tables.clearStatus);

    // The star that says the file on screen is not the file on disk follows the typing
    tables.get('content').addEventListener('input', tables.renderModified);

    // The keys an editor is saved with anywhere else save this file too
    document.addEventListener('keydown', tables.onKeyDown);

    // The file is an ini file, so it is read on screen the way one is
    $.fn.zato.highlight.attach(tables.get('content'), $.fn.zato.highlight.ini_to_html);

    tables.split.init();
    tables.gutter.init();
    tables.flow.init();
    tables.trace.init();
};

// ////////////////////////////////////////////////////////////////////////

// Ctrl-S and Cmd-S save the file on screen, which is what those keys do in an editor. The
// browser's own answer to them is to save the page, so it is turned down.
tables.onKeyDown = function(event) {

    var isSave = event.key === 's' && (event.ctrlKey || event.metaKey);

    if(!isSave) {
        return;
    }

    event.preventDefault();

    // Nothing is open, so there is nothing to save
    if(!tables.state.currentName) {
        return;
    }

    tables.save();
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

// What the file turns out to be, read off the file itself - a code list is a file whose
// codes table holds the codes themselves, so a file that only groups other tables under
// that name, as a file of settings may well do, is not one.
tables.deriveKind = function(parsed) {

    var out = 'mappings';
    var section = parse.findSection(parsed, tables.config.codesSection);

    if(section && section.entryList.length) {
        out = 'codes';
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The file being looked at
// ////////////////////////////////////////////////////////////////////////

tables.select = function(name) {

    tables.state.currentName = name;

    tables.url.writeFile(name);
    tables.setStatus('');
    tables.renderList();
    tables.renderEditor();
};

// ////////////////////////////////////////////////////////////////////////

// Where the file being read is, said in full in the heading - the file's own path while one
// is open, and the directory the files come from while none is.
tables.renderRoot = function(path) {

    tables.get('root-path').textContent = path;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the file on screen says something other than the file on disk does, which is what
// the star after its name stands for. Only the file being looked at is typed into, so it is
// the only one there can be anything to say about.
tables.isModified = function() {

    var table = tables.getCurrent();

    if(table === null) {
        return false;
    }

    var out = tables.get('content').value !== table.content;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The star after the file's name, in the heading and on the file's own row.
tables.renderModified = function() {

    var isModified = tables.isModified();

    tables.get('root-modified').hidden = !isModified;

    var star = tables.get('file-list').querySelector('.config-tables-file-selected .config-tables-file-modified');

    // The listing has no row of a file being looked at while there is no file open
    if(star) {
        star.hidden = !isModified;
    }
};

// ////////////////////////////////////////////////////////////////////////

tables.renderEmpty = function() {

    tables.renderRoot(tables.state.userConfDirectory);

    tables.get('empty').hidden = false;
    tables.get('editor').hidden = true;

    // With no file open there is nothing to run a value through
    tables.showTranslate(false);
    tables.invoker.refreshTranslate();
};

// ////////////////////////////////////////////////////////////////////////

// The Translate column and the line that sizes it, which come and go together.
tables.showTranslate = function(isShown) {

    tables.get('translate-panel').hidden = !isShown;
    tables.get('translate-splitter').hidden = !isShown;
};

// ////////////////////////////////////////////////////////////////////////

tables.renderEditor = function() {

    var table = tables.getCurrent();

    tables.renderRoot(table.path);

    tables.get('empty').hidden = true;
    tables.get('editor').hidden = false;
    tables.showTranslate(true);

    var content = tables.get('content');

    // A file too large for the browser is worked on elsewhere - taken away and changed
    // in your own tools - so what stands in for it on screen is the line that says as
    // much, and neither Check nor Save has anything to work on
    if(table.is_editable) {
        content.value = table.content;
    }
    else {
        content.value = tables.buildOutsideText(table);
    }

    content.readOnly = !table.is_editable;

    tables.get('check').disabled = !table.is_editable;
    tables.get('save').disabled = !table.is_editable;

    // Setting the value from here fires no input event, so the colors and the
    // numbers down the left are brought up to date by hand
    $.fn.zato.highlight.refresh(content);
    tables.gutter.refresh();
    tables.renderModified();
    content.previousElementSibling.classList.toggle(tables.config.backdropReadOnly, content.readOnly);

    tables.invoker.render(table);
};

// ////////////////////////////////////////////////////////////////////////

// Whether the file on screen reads at all, without saving it - a file that does says so
// in a word, and one that does not says which line stopped it.
tables.check = function() {

    var content = tables.get('content').value;
    var parsed = parse.read(content);

    if(parsed.errorText) {
        tables.setStatus(tables.buildErrorText(parsed), true);
        return;
    }

    tables.setStatus(tables.config.checkedMessage);
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
        tables.renderList();
        tables.invoker.refresh(table);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The file as it was when the page was opened, back in the editor. Nothing is
// saved by this - what is on the server stays as it is until Save is pressed.
tables.restore = function() {

    var table = tables.getCurrent();
    var content = tables.get('content');

    content.value = tables.state.initialContent[table.name];

    $.fn.zato.highlight.refresh(content);
    tables.gutter.refresh();
    tables.renderModified();
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

// The line under the editor, which says what has just happened and nothing else. What went
// through says so for a moment and is then gone, while what did not stays until it is read
// and cleared, since a line that goes away on its own is a line that is missed.
tables.setStatus = function(text, isError) {

    var status = tables.get('status');
    var config = tables.config;
    var state = tables.state;

    // A message from a moment ago is not left to go away on the new one's time
    if(state.statusTimer) {
        window.clearTimeout(state.statusTimer);
        state.statusTimer = 0;
    }

    status.textContent = text;

    if(isError) {
        status.className = config.statusError;
        return;
    }

    if(!text) {
        status.className = config.statusPlain;
        return;
    }

    status.className = config.statusOK;
    state.statusTimer = window.setTimeout(tables.clearStatus, config.statusShownMS);
};

// ////////////////////////////////////////////////////////////////////////

tables.clearStatus = function() {

    tables.setStatus('');
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
