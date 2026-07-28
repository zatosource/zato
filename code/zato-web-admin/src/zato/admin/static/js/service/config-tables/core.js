// Config tables - the page under Services, where the config files a service
// reads through self.config are browsed and changed.
//
// The page is rendered by zato/service/config-tables.html. The files are listed
// on the left, the one being looked at fills the rest of the page. This file holds
// the state and the editor around the textarea. The listing itself is in
// listing.js, the reading of a file in parse.js, the words the page puts on screen
// in text.js, the Try it strip in invoker.js, the listing's menu in menu.js, what
// is done to the file itself in files.js and the bringing in of one in upload.js.

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

    // What a file of each kind is called on screen, what its badge in the listing
    // says and which of the shared badge colors it wears, and what one entry of it is
    kindLabel: {codes: 'code list', mappings: 'mapping set'},
    kindBadge: {codes: 'codes', mappings: 'maps'},
    kindBadgeClass: {codes: 'zato-badge-blue', mappings: 'zato-badge-amber'},
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
    sizeStep: 1024,

    // The class the overlay behind the editor wears for a file the browser does
    // not edit in place
    backdropReadOnly: 'highlight-backdrop-readonly',

    // Where the listing ends and the file begins, as a share of the panel. It goes
    // anywhere between the two edges, and a drag that ends up this close to the
    // left one shuts the listing altogether. The rest is how far one arrow key
    // press moves the split, the class the handle wears mid-drag, the class the
    // listing wears while it is shut and where the split is kept between visits.
    splitMinPercent: 0,
    splitMaxPercent: 100,
    splitCollapseAtPercent: 8,
    splitKeyboardStepPercent: 2,
    splitActiveClass: 'config-tables-splitter-active',
    splitCollapsedClass: 'config-tables-browser-collapsed',
    splitStorageKey: 'zato.config-tables.split'
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
    tables.upload.init();
    tables.invoker.init();
    tables.menu.init();

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

    // The file is an ini file, so it is read on screen the way one is
    $.fn.zato.highlight.attach(tables.get('content'), $.fn.zato.highlight.ini_to_html);

    tables.wireSplit();
};

// ////////////////////////////////////////////////////////////////////////

// The line between the listing and the file, which is dragged to give either
// side more room. Where it was left is where it opens the next time.
tables.wireSplit = function() {

    var config = tables.config;

    $.fn.zato.resizer.init({

        container: tables.get('content-area'),
        first: tables.get('browser'),
        handles: [tables.get('splitter')],
        axis: 'x',

        minPercent: config.splitMinPercent,
        maxPercent: config.splitMaxPercent,
        keyboardStepPercent: config.splitKeyboardStepPercent,
        activeClass: config.splitActiveClass,

        // Browser storage is an external boundary, so an empty one is answered
        // explicitly - the listing then opens at the width its styles give it
        read: function() {

            var saved = localStorage.getItem(config.splitStorageKey);

            if(saved === null) {
                return null;
            }

            return parseFloat(saved);
        },

        write: function(percent) {
            localStorage.setItem(config.splitStorageKey, String(percent));
        },

        // A drag that comes near the left edge is pulled the rest of the way, so
        // the listing shuts on its own rather than being left as a sliver. Keys
        // step where they are told, which is how the listing is opened again.
        snap: function(percent, isDragging) {

            if(isDragging && percent < config.splitCollapseAtPercent) {
                return 0;
            }

            return percent;
        },

        applied: function(percent) {

            var isCollapsed = percent === 0;
            tables.get('browser').classList.toggle(config.splitCollapsedClass, isCollapsed);
        }
    });
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
// The file being looked at
// ////////////////////////////////////////////////////////////////////////

tables.select = function(name) {

    tables.state.currentName = name;

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

    var content = tables.get('content');

    // A file too large for the browser is worked on the other way round - taken
    // away, changed and uploaded again - so what stands in for it on screen is the
    // line that says as much, and neither Check nor Save has anything to work on
    if(table.is_editable) {
        content.value = table.content;
    }
    else {
        content.value = tables.buildOutsideText(table);
    }

    content.readOnly = !table.is_editable;

    tables.get('check').disabled = !table.is_editable;
    tables.get('save').disabled = !table.is_editable;

    // Setting the value from here fires no input event, so the colors are
    // repainted by hand
    $.fn.zato.highlight.refresh(content);
    content.previousElementSibling.classList.toggle(tables.config.backdropReadOnly, content.readOnly);

    tables.invoker.render(table);
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
