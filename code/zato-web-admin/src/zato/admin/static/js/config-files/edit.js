// Config files kit - the keys an editor is worked with, and what each file remembers of being
// worked on.
//
// Typing into a file is one more thing the page did, so it goes onto the row of events in
// stream.js, where it stands among the files added, renamed and deleted and is taken back by the
// same Ctrl-Z. What a run of typing amounts to is worked out here - a step is a word rather than
// a letter and rather than everything typed since the file was opened - and so is putting one
// side of such a step back on screen.
//
// A file also keeps where its caret was, so a file opened again opens where it was left. And the
// files with something unsaved in them are one row of stops, which Alt-Left and Alt-Right walk,
// so a change made in one file and a change made in another are one keypress apart. Alt with an
// arrow is the browser's own way back and forward through its history, which is turned down
// here, the page being the one page either way.
//
// Every key that reaches any of this is logged, whether it is acted on or not - see log.js.
//
// The row of events is kept for as long as the page is open, the way an editor keeps one. Where
// the caret was outlives the page, since it is one number a file is opened at rather than a
// history of anything.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var edit = tables.edit;
var stream = tables.stream;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

edit.config = {

    // What holds a run of typing together as one event, so Ctrl-Z takes back a word rather than
    // a letter and rather than everything typed since the file was opened. The run is broken by
    // a pause, by as many characters as a long word, by the caret moving off where it was, by
    // typing turning into deleting, by anything that is not part of a word, whitespace included -
    // which is why a word is what a step usually holds - and by anything else the page did in
    // the meantime, a file added or renamed included.
    coalesceMS: 500,
    runLength: 24,

    // What follows the screen's own storage prefix in the key the carets are kept under
    // between one visit and the next, and how long after the last move they are written there
    caretSuffix: '.caret',
    writeMS: 200,

    // What is said when the keys that walk the unsaved files have nowhere to walk to
    noEditMessage: 'Nothing unsaved'
};

// ////////////////////////////////////////////////////////////////////////

edit.state = {

    // What each file that has been opened held, by path, as of the last thing the page did to
    // it - the typing that comes next is the step from there, which is what an event is made of
    screenByPath: {},

    // Where the caret was in each file, by path, as the two ends of what was selected
    caretByPath: {},

    // The write of the carets waiting to happen, 0 while there is none
    timer: 0
};

// ////////////////////////////////////////////////////////////////////////

edit.init = function() {

    edit.state.caretByPath = edit.readCaret();

    var content = tables.get('content');

    // Wherever the caret has been left, by a key, by the mouse or by the typing itself
    content.addEventListener('keyup', edit.rememberCaret);
    content.addEventListener('mouseup', edit.rememberCaret);
    content.addEventListener('input', edit.rememberCaret);

    // The files with something unsaved in them are walked from anywhere on the page
    document.addEventListener('keydown', edit.onPageKeyDown);

    log.say('edit.init', {
        caretCount: Object.keys(edit.state.caretByPath).length,
        caretByPath: JSON.stringify(edit.state.caretByPath),
        contentFound: content !== null
    });
};

// ////////////////////////////////////////////////////////////////////////

// The file is on screen, holding whatever was last left in it, and its caret is where it was.
edit.open = function(table) {

    var isNew = edit.state.screenByPath[table.path] === undefined;

    if(isNew) {
        edit.openFirst(table);
    }

    var wasActiveId = document.activeElement === null ? '' : document.activeElement.id;

    // The file is what the page is about, so it is what the keyboard is on. Without this the
    // caret is put back where it was and shows nowhere, the cursor being on the listing the
    // file was picked from, and the first press in the file moves it somewhere else.
    tables.get('content').focus({preventScroll: true});

    edit.applyCaret(table);

    var data = log.buildTable(table);

    data.wasActiveId = wasActiveId;
    data.activeId = document.activeElement.id;
    data.isFirstOpen = isNew;
    data.eventIdx = stream.state.eventIdx;
    data.eventCount = stream.state.eventList.length;
    data.screenLength = tables.get('content').value.length;
    data.caret = JSON.stringify(edit.state.caretByPath[table.path]);
    data.selectionStart = tables.get('content').selectionStart;
    data.selectionEnd = tables.get('content').selectionEnd;

    log.say('edit.open', data);
};

// ////////////////////////////////////////////////////////////////////////

// The file is being read for the first time since the page was opened. A file left with something
// unsaved from an earlier visit is on screen holding that, and the file on disk is what it was
// typed into from, so that typing goes on the row of events as the step it was - going back all
// the way is then going back to what a service reading the file would get.
edit.openFirst = function(table) {

    var disk = table.content;
    var screen = tables.draft.get(table);

    edit.state.screenByPath[table.path] = screen;

    // A file brought back by going back through the row is opened in the middle of that walk, and
    // what it holds is what the walk put there rather than anything the page has just done
    var isWalking = stream.state.isWalking;

    log.say('edit.openFirst', {
        path: table.path,
        diskLength: disk.length,
        screenLength: screen.length,
        hasDraft: screen !== disk,
        isWalking: isWalking
    });

    if(screen === disk || isWalking) {
        return;
    }

    stream.push(edit.buildEvent(table, disk, screen, disk.length, disk.length));
};

// ////////////////////////////////////////////////////////////////////////

// One more thing the page did, taken as the file is typed into. A run of typing goes onto the
// event at the end of the row for as long as it reads as one word being written, and anything
// that had been taken back is gone by then, the file having gone another way from there.
edit.remember = function(table, content) {

    var config = edit.config;
    var now = Date.now();
    var box = tables.get('content');

    var previousContent = edit.getScreen(table);
    var delta = content.length - previousContent.length;

    // A run is only ever joined onto the typing right before it, so anything else the page did
    // in the meantime - another file added, renamed or deleted - ends it
    var tail = stream.getTail();
    var isSameFile = tail !== null && tail.kind === 'edit' && tail.path === table.path;
    var sinceMS = isSameFile ? now - tail.time : -1;

    // Every one of these has to hold for the keystroke to join the run at the end
    var isSoonEnough = isSameFile && tail.time !== 0 && sinceMS < config.coalesceMS;
    var isSameWay = isSameFile && delta !== 0 && (delta > 0) === (tail.runDelta > 0);
    var isAdjacent = isSameFile && box.selectionStart === tail.to.start + delta;
    var isShortEnough = isSameFile && tail.runCount + Math.abs(delta) <= config.runLength;

    var isRun = isSoonEnough && isSameWay && isAdjacent && isShortEnough;

    if(isRun) {

        tail.to = {content: content, start: box.selectionStart, end: box.selectionEnd};
        tail.time = now;
        tail.runDelta = delta;
        tail.runCount = tail.runCount + Math.abs(delta);
    }
    else {

        var event = edit.buildEvent(table, previousContent, content, box.selectionStart, box.selectionEnd);

        event.time = now;
        event.runDelta = delta;
        event.runCount = Math.abs(delta);

        stream.push(event);
    }

    // A word just ended, so the run ends with it and the next keystroke is an event of its own
    var isWordEnd = delta > 0 && edit.isBreak(content.charAt(box.selectionStart - 1));

    if(isWordEnd) {
        stream.getTail().time = 0;
    }

    edit.state.screenByPath[table.path] = content;

    log.say('edit.remember', {
        path: table.path,
        isRun: isRun,
        isSameFile: isSameFile,
        isSoonEnough: isSoonEnough,
        isSameWay: isSameWay,
        isAdjacent: isAdjacent,
        isShortEnough: isShortEnough,
        isWordEnd: isWordEnd,
        sinceMS: sinceMS,
        delta: delta,
        runCount: stream.getTail().runCount,
        eventIdx: stream.state.eventIdx,
        eventCount: stream.state.eventList.length,
        length: content.length,
        diskLength: table.content.length,
        selectionStart: box.selectionStart,
        selectionEnd: box.selectionEnd
    });
};

// ////////////////////////////////////////////////////////////////////////

// The run of typing at the end of the row ends here, so what comes next is an event of its own.
// What the page puts in the editor whole - the file as it was opened, an ini file made of a csv
// one - is not a keystroke to be joined onto the typing before it.
edit.breakRun = function() {

    var tail = stream.getTail();

    if(tail !== null) {
        tail.time = 0;
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the file held as of the last thing the page did to it, which is where the typing that
// comes next starts from. A file the browser does not edit in place is read rather than opened,
// so what it holds is what a service reading it gets.
edit.getScreen = function(table) {

    var out = edit.state.screenByPath[table.path];

    if(out === undefined) {
        out = table.content;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The typing of one file as one thing the page did - the file on either side of it, and where the
// caret was left once it was done.
edit.buildEvent = function(table, previousContent, content, start, end) {

    var out = {
        kind: 'edit',
        name: table.name,
        path: table.path,
        from: {content: previousContent, start: previousContent.length, end: previousContent.length},
        to: {content: content, start: start, end: end},

        // When the typing was last added to, how much of it there is and which way it went, all
        // three of which say whether the next keystroke joins it
        time: 0,
        runCount: 0,
        runDelta: 0
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the character ends a word, which is where one step of the history ends and the
// next one starts.
edit.isBreak = function(character) {

    var out = /\s/.test(character);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One side of a step, on screen. The file is put there whole, so what is on screen after this is
// the file as it stood then, and the caret is at the change rather than where it was left.
edit.applyContent = function(table, wanted) {

    var content = tables.get('content');
    var previousContent = content.value;

    // The caret goes to the end of what this step changed rather than to where it stood when the
    // step was taken - a step taken back is read at the change it took back, and the end of the
    // file, which is where the caret of a step out of storage stands, is nowhere near it
    var at = edit.getChangeEnd(previousContent, wanted);

    content.value = wanted;
    content.setSelectionRange(at, at);

    edit.state.screenByPath[table.path] = wanted;

    log.say('edit.applyContent', {
        path: table.path,
        lengthFrom: previousContent.length,
        lengthTo: wanted.length,
        changeEnd: at,
        isDraft: wanted !== table.content
    });

    // Nothing typed it, so the colors, the numbers down the left, what is unsaved and the star
    // that says so are all brought up to date by hand
    $.fn.zato.highlight.refresh(content);
    tables.gutter.refresh();
    tables.draft.remember(table, wanted);
    tables.renderModified();

    // A step taken back somewhere else in the file is one the reader is brought to, since a
    // change that cannot be seen reads as no change at all
    tables.wash.showLine(edit.getLineIdx(wanted, at));

    edit.rememberCaret();
};

// ////////////////////////////////////////////////////////////////////////

// Where the change between two states of the file ends - what the two have in common at the
// start and at the end is not the change, so what is left between the two is, and the end of it
// is where the caret belongs. Two states that say the same thing have no change and no end to
// it, so the caret stays where the two part company, which is the end of the file.
edit.getChangeEnd = function(previousContent, content) {

    var shortest = Math.min(previousContent.length, content.length);
    var prefix = 0;

    while(prefix < shortest && previousContent.charAt(prefix) === content.charAt(prefix)) {
        prefix++;
    }

    var suffix = 0;
    var room = shortest - prefix;

    while(suffix < room &&
        previousContent.charAt(previousContent.length - 1 - suffix) ===
        content.charAt(content.length - 1 - suffix)) {

        suffix++;
    }

    var out = content.length - suffix;

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Where the caret was
// ////////////////////////////////////////////////////////////////////////

edit.rememberCaret = function() {

    var table = tables.getCurrent();

    if(table === null) {
        return;
    }

    var content = tables.get('content');
    var caret = [content.selectionStart, content.selectionEnd];
    var previous = edit.state.caretByPath[table.path];
    var isSame = previous !== undefined && previous[0] === caret[0] && previous[1] === caret[1];

    // The caret is asked about on every key and every press, and most of those leave it where
    // it was, which is not a fact worth a line of its own
    if(isSame) {
        return;
    }

    edit.state.caretByPath[table.path] = caret;
    edit.writeCaretSoon();

    log.say('edit.rememberCaret', {
        path: table.path,
        selectionStart: caret[0],
        selectionEnd: caret[1],
        previous: JSON.stringify(previous),
        length: content.value.length
    });
};

// ////////////////////////////////////////////////////////////////////////

// The caret of the file, back where it was - at the end of the file the first time it is
// opened, which is where a file is left off at.
edit.applyCaret = function(table) {

    var caret = edit.state.caretByPath[table.path];
    var content = tables.get('content');

    if(caret === undefined) {
        log.say('edit.applyCaret', {path: table.path, hasCaret: false});
        return;
    }

    var last = content.value.length;
    var start = Math.min(caret[0], last);
    var end = Math.min(caret[1], last);

    content.setSelectionRange(start, end);

    // Setting the caret does not bring it on screen, and a caret off screen is a caret that
    // has not come back as far as the reader is concerned. The line lands in the middle of the
    // view rather than at its edge, since a line at the bottom of the view is a line with no
    // file under it to read.
    var lineIdx = edit.getLineIdx(content.value, start);

    tables.wash.showLine(lineIdx);

    log.say('edit.applyCaret', {
        path: table.path,
        hasCaret: true,
        wanted: JSON.stringify(caret),
        selectionStart: start,
        selectionEnd: end,
        length: last,
        lineIdx: lineIdx,
        scrollTop: content.scrollTop
    });
};

// ////////////////////////////////////////////////////////////////////////

// Where the caret of the file is, as the two ends of what is selected, and the end of the file
// for one that has not been opened yet. This is what a file takes with it when it is deleted, so
// that bringing it back opens it where it was left.
edit.getCaret = function(table) {

    var out = edit.state.caretByPath[table.path];

    if(out === undefined) {
        out = [table.content.length, table.content.length];
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

edit.setCaret = function(table, caret) {

    edit.state.caretByPath[table.path] = caret;
    edit.writeCaretSoon();

    log.say('edit.setCaret', {path: table.path, caret: JSON.stringify(caret)});
};

// ////////////////////////////////////////////////////////////////////////

// Which line of the file an offset into it is on, counted from the first.
edit.getLineIdx = function(content, offset) {

    var before = content.substring(0, offset);
    var out = before.split('\n').length - 1;

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// Walking the files with something unsaved in them
// ////////////////////////////////////////////////////////////////////////

edit.onPageKeyDown = function(event) {

    var isArrow = event.key === 'ArrowLeft' || event.key === 'ArrowRight';

    // Only the arrows are worth a line here, since every other key on the page comes through
    // this listener as well
    if(!isArrow) {
        return;
    }

    var isWanted = event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;
    var isBack = event.key === 'ArrowLeft';

    var data = log.buildKey(event);

    data.isWanted = isWanted;
    data.isBack = isBack;

    log.say('edit.onPageKeyDown', data);

    if(!isWanted) {
        return;
    }

    // Alt with an arrow is the browser's way back through its own history, which would take
    // the whole page away
    event.preventDefault();

    if(isBack) {
        edit.goToEdit(-1);
    }
    else {
        edit.goToEdit(1);
    }
};

// ////////////////////////////////////////////////////////////////////////

// The next file with something unsaved in it, or the one before it, in the order the listing
// has them. The row of them is walked round, so the last one leads back to the first.
edit.goToEdit = function(direction) {

    var nameList = edit.getEditedNameList();

    if(!nameList.length) {

        log.say('edit.goToEdit', {
            direction: direction,
            currentName: tables.state.currentName,
            editedCount: 0
        });

        tables.setStatus(edit.config.noEditMessage);
        return;
    }

    var nameIdx = nameList.indexOf(tables.state.currentName);
    var wanted = 0;

    if(nameIdx === -1) {

        // The file being read has nothing unsaved in it, so the walk starts at the end it is
        // being walked towards
        wanted = direction > 0 ? 0 : nameList.length - 1;
    }
    else {
        wanted = (nameIdx + direction + nameList.length) % nameList.length;
    }

    log.say('edit.goToEdit', {
        direction: direction,
        currentName: tables.state.currentName,
        editedCount: nameList.length,
        editedNameList: JSON.stringify(nameList),
        nameIdxFrom: nameIdx,
        nameIdxTo: wanted,
        wantedName: nameList[wanted]
    });

    tables.select(nameList[wanted]);
    tables.get('content').focus();
};

// ////////////////////////////////////////////////////////////////////////

edit.getEditedNameList = function() {

    var out = [];
    var tableList = tables.state.tableList;

    for(var tableIdx = 0; tableIdx < tableList.length; tableIdx++) {

        var table = tableList[tableIdx];

        if(tables.draft.has(table)) {
            out.push(table.name);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// What a file no longer at that path leaves behind
// ////////////////////////////////////////////////////////////////////////

edit.rename = function(previousPath, table) {

    var state = edit.state;

    log.say('edit.rename', {
        previousPath: previousPath,
        path: table.path,
        hasScreen: state.screenByPath[previousPath] !== undefined,
        caret: JSON.stringify(state.caretByPath[previousPath])
    });

    var screen = state.screenByPath[previousPath];

    delete state.screenByPath[previousPath];

    if(screen !== undefined) {
        state.screenByPath[table.path] = screen;
    }

    var caret = state.caretByPath[previousPath];

    delete state.caretByPath[previousPath];

    if(caret !== undefined) {
        state.caretByPath[table.path] = caret;
    }

    edit.writeCaretSoon();
};

// ////////////////////////////////////////////////////////////////////////

edit.forget = function(table) {

    log.say('edit.forget', {
        path: table.path,
        hasScreen: edit.state.screenByPath[table.path] !== undefined,
        caret: JSON.stringify(edit.state.caretByPath[table.path])
    });

    delete edit.state.screenByPath[table.path];
    delete edit.state.caretByPath[table.path];

    edit.writeCaretSoon();
};

// ////////////////////////////////////////////////////////////////////////
// The carets between one visit and the next
// ////////////////////////////////////////////////////////////////////////

// Where this screen's carets are kept, under the screen's own storage prefix, so two screens
// built on the kit never open each other's files at each other's places.
edit.buildCaretKey = function() {

    var out = tables.config.storagePrefix + edit.config.caretSuffix;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The caret moves with every keystroke, so it is written once the moving has stopped rather
// than once per key.
edit.writeCaretSoon = function() {

    var state = edit.state;

    if(state.timer) {
        window.clearTimeout(state.timer);
    }

    state.timer = window.setTimeout(edit.writeCaret, edit.config.writeMS);
};

// ////////////////////////////////////////////////////////////////////////

edit.writeCaret = function() {

    edit.state.timer = 0;

    var text = JSON.stringify(edit.state.caretByPath);

    window.localStorage.setItem(edit.buildCaretKey(), text);
};

// ////////////////////////////////////////////////////////////////////////

edit.readCaret = function() {

    var out = {};
    var stored = window.localStorage.getItem(edit.buildCaretKey());

    // Nothing has been kept in this browser yet, or what was kept is no longer readable, and
    // either way every file opens at the end of itself
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

})(jQuery);
