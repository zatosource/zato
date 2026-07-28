// Config tables - what the page did, on the console.
//
// Everything the page does to a file is logged and stays logged - the keys pressed, the steps
// a file goes through, what is unsaved, where the caret is, which file is opened and what is
// written to the server. A key that does nothing and a key that does the wrong thing read
// differently here, which is what makes this worth having on all the time rather than
// something to be put back in once something has gone wrong.
//
// One fact per line, both sides of it in JSON, since a console cuts a long line short and a
// line that has been cut is a fact that has been lost.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

log.config = {

    // What every line of the log is headed by
    prefix: 'config-tables',

    // What the facts under a heading are set in from its left
    indent: '    '
};

// ////////////////////////////////////////////////////////////////////////

// What just happened, and the facts of it - the heading on its own line, then one line per
// fact under it.
log.say = function(topic, data) {

    var config = log.config;

    console.log(JSON.stringify(config.prefix + ' | ' + topic));

    for(var key in data) {
        console.log(config.indent + JSON.stringify(key) + ': ' + JSON.stringify(data[key]));
    }
};

// ////////////////////////////////////////////////////////////////////////

// A key as it was pressed, down to what else was held with it and what was under the cursor at
// the time - which is what says whether a shortcut was even seen by the page.
log.buildKey = function(event) {

    var out = {
        key: event.key,
        code: event.code,
        alt: event.altKey,
        ctrl: event.ctrlKey,
        meta: event.metaKey,
        shift: event.shiftKey,
        repeat: event.repeat,
        defaultPrevented: event.defaultPrevented,
        targetTag: event.target.tagName,
        targetId: event.target.id,
        activeId: document.activeElement === null ? '' : document.activeElement.id
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A file as much as the log ever needs of it - what it is called, where it is, and how much
// of it there is on disk and on screen.
log.buildTable = function(table) {

    var out = {};

    if(table === null) {
        out.table = null;
        return out;
    }

    out.name = table.name;
    out.path = table.path;
    out.diskLength = table.content.length;
    out.isEditable = table.is_editable;
    out.hasDraft = tables.draft.has(table);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
