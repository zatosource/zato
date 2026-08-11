// Config files kit - the row of everything the page has done, and going back and forward through it.
//
// Typing into a file, adding one, renaming one and deleting one are all one kind of thing here:
// something the page did, in the order it did it. Ctrl-Z takes back whatever the last of them was
// and Ctrl-Y does it again, so a file typed into, then renamed, then typed into again is walked
// back through in that order rather than each file being walked on its own.
//
// A file coming or going is a round trip to the server, since a file on screen is a file on disk -
// taking back an added file deletes it, taking back a deleted one writes it again with everything
// it held, and taking back a rename names it what it was called. Nothing else is walked while one
// of those is on its way there, the row of events standing at whatever the server last confirmed.
//
// What the file held when it went is kept on the event that took it away, so bringing it back
// brings back what was in it, what was unsaved in it and where its caret was.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var stream = tables.stream;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

stream.config = {

    // How many things back the page remembers
    depth: 200,

    // What is said when there is nothing left to take back or to do again, and what is said
    // while a file coming or going is still on its way to the server
    noUndoMessage: 'Nothing to undo',
    noRedoMessage: 'Nothing to redo',
    busyMessage: 'The last change is still going through',

    // What is said once a file has been taken away again or brought back
    undoneAddMessage: 'Undid adding ',
    undoneRemoveMessage: 'Brought back ',
    renameMessage: 'Renamed '
};

// ////////////////////////////////////////////////////////////////////////

stream.state = {

    // Everything the page has done, oldest first, and how many of those it stands at - the one
    // before that count is what Ctrl-Z takes back, the one at it is what Ctrl-Y does again
    eventList: [],
    eventIdx: 0,

    // Whether the page is going back or forward through the row right now. A file coming or going
    // waits on the server, so this outlasts the keypress, and nothing else is walked or put on
    // the row in the meantime - what the page stands at is not known until the server answers.
    isWalking: false
};

// ////////////////////////////////////////////////////////////////////////

stream.init = function() {

    // The keys reach the whole page, a file having been added, renamed or deleted from the
    // listing rather than from inside the file being typed into
    document.addEventListener('keydown', stream.onKeyDown);
};

// ////////////////////////////////////////////////////////////////////////

stream.onKeyDown = function(event) {

    var isCommand = event.ctrlKey || event.metaKey;
    var key = event.key.toLowerCase();
    var isUndo = isCommand && key === 'z' && !event.shiftKey;
    var isRedo = isCommand && (key === 'y' || (key === 'z' && event.shiftKey));

    if(!isUndo && !isRedo) {
        return;
    }

    var data = log.buildKey(event);

    data.isUndo = isUndo;
    data.isRedo = isRedo;
    data.eventIdx = stream.state.eventIdx;
    data.eventCount = stream.state.eventList.length;

    log.say('stream.onKeyDown', data);

    // The browser keeps a history of the field being typed into, which is not the one the page
    // went through - ours is the one that outlives a look at another file
    event.preventDefault();

    if(isUndo) {
        stream.walk(-1);
    }
    else {
        stream.walk(1);
    }
};

// ////////////////////////////////////////////////////////////////////////
// The row of events
// ////////////////////////////////////////////////////////////////////////

// One more thing the page did. Anything that had been taken back is gone by now, the page having
// gone another way from there, which is what makes this the row of what actually happened.
stream.push = function(event) {

    var state = stream.state;
    var droppedCount = state.eventList.length - state.eventIdx;

    state.eventList.length = state.eventIdx;
    state.eventList.push(event);

    // The oldest goes once the page has more of them than it remembers
    var isFull = state.eventList.length > stream.config.depth;

    if(isFull) {
        state.eventList.shift();
    }

    state.eventIdx = state.eventList.length;

    log.say('stream.push', {
        kind: event.kind,
        name: event.name,
        path: event.path,
        eventIdx: state.eventIdx,
        eventCount: state.eventList.length,
        droppedCount: droppedCount,
        isFull: isFull
    });
};

// ////////////////////////////////////////////////////////////////////////

// The last thing the page did, which is the one a run of typing joins onto rather than following.
stream.getTail = function() {

    var state = stream.state;
    var out = state.eventIdx === 0 ? null : state.eventList[state.eventIdx - 1];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One thing back through what the page did, or one forward.
stream.walk = function(direction) {

    var state = stream.state;
    var isBack = direction < 0;
    var config = stream.config;

    // A file on its way to or from the server has not landed yet, so what the page stands at is
    // not known and nothing is walked on top of it
    if(state.isWalking) {

        log.say('stream.walk', {direction: direction, isWalking: true});

        tables.setStatus(config.busyMessage, true);
        return;
    }

    var eventIdx = isBack ? state.eventIdx - 1 : state.eventIdx;
    var isWithin = eventIdx >= 0 && eventIdx < state.eventList.length;

    log.say('stream.walk', {
        direction: direction,
        isWalking: false,
        eventIdx: state.eventIdx,
        wantedIdx: eventIdx,
        eventCount: state.eventList.length,
        isWithin: isWithin,
        kind: isWithin ? state.eventList[eventIdx].kind : ''
    });

    // The page is at one end of what it did
    if(!isWithin) {
        tables.setStatus(isBack ? config.noUndoMessage : config.noRedoMessage);
        return;
    }

    state.isWalking = true;

    stream.apply(state.eventList[eventIdx], direction, function() {

        state.eventIdx = state.eventIdx + direction;
        state.isWalking = false;
    });
};

// ////////////////////////////////////////////////////////////////////////

// One event, walked the way it is being walked. What is on disk is only ever answered for by the
// server, so the row of events moves on once the change has actually gone through, which is what
// onDone is called for.
stream.apply = function(event, direction, onDone) {

    if(event.kind === 'edit') {
        stream.applyEdit(event, direction);
        onDone();
        return;
    }

    if(event.kind === 'rename') {
        stream.applyRename(event, direction, onDone);
        return;
    }

    // A file that was added is taken away by going back and brought back by going forward, and a
    // file that was deleted is the other way round
    var isBack = direction < 0;
    var isAdd = event.kind === 'add';

    if(isAdd === isBack) {
        stream.takeAway(event, onDone);
    }
    else {
        stream.bringBack(event, onDone);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The file as it stood on one side of the typing that this event was, which is the file it was
// typed into rather than whichever one is being read now.
stream.applyEdit = function(event, direction) {

    var table = tables.getByName(event.name);
    var isBack = direction < 0;
    var step = isBack ? event.from : event.to;

    log.say('stream.applyEdit', {
        direction: direction,
        name: event.name,
        path: event.path,
        hasTable: table !== null,
        currentName: tables.state.currentName,
        lengthTo: step.content.length
    });

    // Only a file that is no longer there, which the events that took it away are walked through
    // before this one is reached
    if(table === null) {
        return;
    }

    // The typing was done in a file that may not be the one on screen, and a change that cannot
    // be seen reads as no change at all
    if(tables.state.currentName !== event.name) {
        tables.select(event.name);
    }

    tables.edit.applyContent(table, step.content);
};

// ////////////////////////////////////////////////////////////////////////
// A file coming and going
// ////////////////////////////////////////////////////////////////////////

// The file off disk and out of the listing. What it holds goes onto the event first, so that
// bringing it back brings back the file as it stood rather than as it was first written.
stream.takeAway = function(event, onDone) {

    var table = tables.getByName(event.name);

    log.say('stream.takeAway', {
        name: event.name,
        path: event.path,
        hasTable: table !== null
    });

    if(table === null) {
        onDone();
        return;
    }

    event.content = table.content;
    event.draft = tables.draft.get(table);
    event.caret = tables.edit.getCaret(table);

    tables.files.persist('delete', table, function() {

        tables.files.dropTable(table);
        tables.setStatus(stream.config.undoneAddMessage + table.file_name);

        onDone();

    }, undefined, stream.release);
};

// ////////////////////////////////////////////////////////////////////////

// The file back on disk and back in the listing, holding what it held when it went - what was
// unsaved in it is unsaved in it again, and its caret is where it was left.
stream.bringBack = function(event, onDone) {

    var table = tables.files.buildTable(event.name, event.fileName, event.directory, event.content);

    log.say('stream.bringBack', {
        name: event.name,
        path: table.path,
        length: event.content.length,
        draftLength: event.draft.length,
        caret: JSON.stringify(event.caret)
    });

    tables.files.persist('add', table, function() {

        tables.state.tableList.push(table);
        tables.state.initialContent[event.name] = event.content;

        tables.draft.remember(table, event.draft);
        tables.edit.setCaret(table, event.caret);

        tables.select(event.name);
        tables.setStatus(stream.config.undoneRemoveMessage + table.file_name);

        onDone();

    }, undefined, stream.release);
};

// ////////////////////////////////////////////////////////////////////////

// The file named what it was called on the other side of the rename.
stream.applyRename = function(event, direction, onDone) {

    var isBack = direction < 0;
    var fromName = isBack ? event.name : event.previousName;
    var toName = isBack ? event.previousName : event.name;
    var toFileName = isBack ? event.previousFileName : event.fileName;

    var table = tables.getByName(fromName);

    log.say('stream.applyRename', {
        direction: direction,
        fromName: fromName,
        toName: toName,
        toFileName: toFileName,
        hasTable: table !== null
    });

    if(table === null) {
        onDone();
        return;
    }

    tables.files.moveTable(table, toName, toFileName, function() {

        tables.setStatus(stream.config.renameMessage + fromName + ' to ' + toName);

        onDone();

    }, stream.release);
};

// ////////////////////////////////////////////////////////////////////////

// The server did not do what it was asked, and it has said why on the line under the editor. The
// page is left where it was, so the row of events still stands at what is actually on disk.
stream.release = function() {

    stream.state.isWalking = false;

    log.say('stream.release', {
        eventIdx: stream.state.eventIdx,
        eventCount: stream.state.eventList.length
    });
};

// ////////////////////////////////////////////////////////////////////////
// What the rest of the page puts on the row
// ////////////////////////////////////////////////////////////////////////

// A file was added, either as an empty one or brought in from your own machine.
stream.rememberAdd = function(table) {

    var caret = tables.edit.getCaret(table);
    var event = stream.buildFileEvent('add', table, table.content, tables.draft.get(table), caret);

    stream.push(event);
};

// ////////////////////////////////////////////////////////////////////////

// A file was deleted, so what it held is kept here - it is all that is left of it, and it is read
// off the file before it goes rather than off the listing it is no longer in.
stream.rememberRemove = function(table, content, draft, caret) {

    stream.push(stream.buildFileEvent('remove', table, content, draft, caret));
};

// ////////////////////////////////////////////////////////////////////////

stream.buildFileEvent = function(kind, table, content, draft, caret) {

    var out = {
        kind: kind,
        name: table.name,
        fileName: table.file_name,
        directory: table.directory,
        path: table.path,

        // What the file holds, what is unsaved in it and where its caret is, all of it as of
        // whenever the file was last taken away
        content: content,
        draft: draft,
        caret: caret
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

stream.rememberRename = function(table, previousName, previousFileName) {

    var event = {
        kind: 'rename',
        name: table.name,
        fileName: table.file_name,
        directory: table.directory,
        path: table.path,
        previousName: previousName,
        previousFileName: previousFileName
    };

    stream.push(event);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
