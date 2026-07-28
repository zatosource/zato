// Config tables - what a file has been typed into but not saved yet.
//
// A change to a file stays a change until it is saved, whichever file is being looked at in
// the meantime and however the page is reloaded. What was typed is kept beside the file it
// belongs to, both in the page and in the browser's own storage, so going to another file and
// back brings the typing back with it, and so does opening the page again.
//
// A draft is only kept for as long as it says something the file on disk does not. Typing a
// file back to what it holds drops the draft, and so does saving it, since there is then
// nothing left unsaved. A file the server no longer reports, or one whose content on disk has
// caught up with what was typed, is dropped when the page starts.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var draft = tables.draft;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

draft.config = {

    // Where the drafts are kept between one visit and the next. Files are keyed by their
    // full path, so two environments served from one browser never read each other's typing.
    storageKey: 'zato.config-tables.draft'
};

// ////////////////////////////////////////////////////////////////////////

draft.state = {

    // The path of every file with something unsaved in it, against what was typed into it
    contentByPath: {}
};

// ////////////////////////////////////////////////////////////////////////

// The drafts of this browser, less the ones there is no longer anything to say about - a file
// that is gone, and a file that now holds on disk what was typed into it.
draft.init = function() {

    var stored = draft.read();
    var tableList = tables.state.tableList;

    for(var tableIdx = 0; tableIdx < tableList.length; tableIdx++) {

        var table = tableList[tableIdx];
        var content = stored[table.path];

        var isDraft = content !== undefined && content !== table.content;

        if(isDraft) {
            draft.state.contentByPath[table.path] = content;
        }

        if(content !== undefined) {

            log.say('draft.init file', {
                path: table.path,
                isDraft: isDraft,
                storedLength: content.length,
                diskLength: table.content.length
            });
        }
    }

    draft.write();

    log.say('draft.init', {
        storedCount: Object.keys(stored).length,
        keptCount: Object.keys(draft.state.contentByPath).length,
        storedPathList: JSON.stringify(Object.keys(stored)),
        keptPathList: JSON.stringify(Object.keys(draft.state.contentByPath))
    });
};

// ////////////////////////////////////////////////////////////////////////

// What the file holds on screen - what was typed into it while it was last open, or what it
// holds on disk when nothing was.
draft.get = function(table) {

    var out = draft.state.contentByPath[table.path];

    if(out === undefined) {
        out = table.content;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

draft.has = function(table) {

    var out = draft.state.contentByPath[table.path] !== undefined;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What has just been typed into the file, kept for as long as it is not what the file holds.
draft.remember = function(table, content) {

    if(content === table.content) {
        draft.forget(table);
        return;
    }

    draft.state.contentByPath[table.path] = content;
    draft.write();

    log.say('draft.remember', {
        path: table.path,
        length: content.length,
        diskLength: table.content.length,
        draftCount: Object.keys(draft.state.contentByPath).length
    });
};

// ////////////////////////////////////////////////////////////////////////

draft.forget = function(table) {

    var had = draft.state.contentByPath[table.path] !== undefined;

    delete draft.state.contentByPath[table.path];
    draft.write();

    if(had) {

        log.say('draft.forget', {
            path: table.path,
            diskLength: table.content.length,
            draftCount: Object.keys(draft.state.contentByPath).length
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

// The file has been renamed, so its draft goes by the new path, the old one being a path no
// file is at any more.
draft.rename = function(previousPath, table) {

    var content = draft.state.contentByPath[previousPath];

    delete draft.state.contentByPath[previousPath];

    if(content !== undefined) {
        draft.state.contentByPath[table.path] = content;
    }

    draft.write();

    log.say('draft.rename', {
        previousPath: previousPath,
        path: table.path,
        hasDraft: content !== undefined,
        draftCount: Object.keys(draft.state.contentByPath).length
    });
};

// ////////////////////////////////////////////////////////////////////////

draft.read = function() {

    var out = {};
    var stored = window.localStorage.getItem(draft.config.storageKey);

    // Nothing has been kept in this browser yet, or what was kept is no longer readable, and
    // either way the files on disk are what the page starts from
    if(stored === null) {
        return out;
    }

    try {
        out = JSON.parse(stored);
    }
    catch(error) {
        out = {};
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

draft.write = function() {

    var text = JSON.stringify(draft.state.contentByPath);

    window.localStorage.setItem(draft.config.storageKey, text);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
