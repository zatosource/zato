// Config tables - the keys an editor is worked with, and what each file remembers of being
// worked on.
//
// A file keeps three things beyond what is typed into it, which draft.js holds. It keeps the
// steps it went through, so Ctrl-Z goes back through them and Ctrl-Y forward again. It keeps
// where the caret was, so a file opened again opens where it was left. And the files with
// something unsaved in them are one row of stops, which Alt-Left and Alt-Right walk, so a
// change made in one file and a change made in another are one keypress apart. Alt with an
// arrow is the browser's own way back and forward through its history, which is turned down
// here, the page being the one page either way.
//
// Every key that reaches any of this is logged, whether it is acted on or not - see log.js.
//
// The steps are kept for as long as the page is open, the way an editor keeps them. Where the
// caret was outlives the page, since it is one number a file is opened at rather than a
// history of anything.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var edit = tables.edit;
var log = tables.log;

// ////////////////////////////////////////////////////////////////////////

edit.config = {

    // What holds a run of typing together as one step of the history, so Ctrl-Z takes back a
    // word rather than a letter and rather than everything typed since the file was opened.
    // The run is broken by a pause, by as many characters as a long word, by the caret moving
    // off where it was, by typing turning into deleting, and by anything that is not part of a
    // word, whitespace included - which is why a word is what a step usually holds.
    coalesceMS: 500,
    runLength: 24,

    // How many steps back a file keeps
    depth: 200,

    // Where the caret of each file is kept between one visit and the next, and how long after
    // the last move it is written there
    caretKey: 'zato.config-tables.caret',
    writeMS: 200,

    // What is said when the keys that walk the unsaved files have nowhere to walk to
    noEditMessage: 'Nothing unsaved'
};

// ////////////////////////////////////////////////////////////////////////

edit.state = {

    // Every file that has been opened, by path, against the steps it went through and which
    // of them it stands at
    historyByPath: {},

    // Where the caret was in each file, by path, as the two ends of what was selected
    caretByPath: {},

    // The write of the carets waiting to happen, 0 while there is none
    timer: 0
};

// ////////////////////////////////////////////////////////////////////////

edit.init = function() {

    edit.state.caretByPath = edit.readCaret();

    var content = tables.get('content');

    // The keys belong to the file being typed into, so they are listened for there rather
    // than on the page
    content.addEventListener('keydown', edit.onKeyDown);

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

// The file is on screen - it stands at a step of its own history, at the step it was left at,
// and its caret is where it was.
edit.open = function(table) {

    var history = edit.state.historyByPath[table.path];
    var isNew = history === undefined;

    if(isNew) {
        history = edit.buildHistory(table);
        edit.state.historyByPath[table.path] = history;
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
    data.isNewHistory = isNew;
    data.stepCount = history.stepList.length;
    data.stepIdx = history.stepIdx;
    data.screenLength = tables.get('content').value.length;
    data.caret = JSON.stringify(edit.state.caretByPath[table.path]);
    data.selectionStart = tables.get('content').selectionStart;
    data.selectionEnd = tables.get('content').selectionEnd;

    log.say('edit.open', data);
};

// ////////////////////////////////////////////////////////////////////////

// A file starts at the file on disk, which is the one step there always is - going back all
// the way is going back to what a service reading it would get. A file left with something
// unsaved from an earlier visit starts one step on from that, so the typing of that visit is
// still a step that can be taken back.
edit.buildHistory = function(table) {

    var disk = table.content;
    var screen = tables.draft.get(table);

    var out = {
        stepList: [{content: disk, start: disk.length, end: disk.length}],
        stepIdx: 0,
        stepTime: 0,

        // What the run of typing at the top of the history stands at - how much of it there is
        // and which way it went, both of which say whether the next keystroke joins it
        runCount: 0,
        runDelta: 0
    };

    if(screen !== disk) {
        out.stepList.push({content: screen, start: screen.length, end: screen.length});
        out.stepIdx = 1;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One more step of the file, taken as it is typed into. A run of typing goes into the step at
// the top for as long as it reads as one word being written, and anything that had been taken
// back is now gone, since the file has gone another way from here.
edit.remember = function(table, content) {

    var config = edit.config;
    var history = edit.state.historyByPath[table.path];
    var now = Date.now();
    var box = tables.get('content');

    var step = {
        content: content,
        start: box.selectionStart,
        end: box.selectionEnd
    };

    var previous = history.stepList[history.stepIdx];
    var delta = content.length - previous.content.length;
    var sinceMS = history.stepTime === 0 ? -1 : now - history.stepTime;

    // Every one of these has to hold for the keystroke to join the run at the top
    var isSoonEnough = history.stepTime !== 0 && now - history.stepTime < config.coalesceMS;
    var isSameWay = delta !== 0 && (delta > 0) === (history.runDelta > 0);
    var isAdjacent = step.start === previous.start + delta;
    var isShortEnough = history.runCount + Math.abs(delta) <= config.runLength;

    var isRun = isSoonEnough && isSameWay && isAdjacent && isShortEnough;
    var droppedCount = history.stepList.length - (history.stepIdx + 1);

    history.stepTime = now;
    history.runDelta = delta;

    if(isRun) {

        history.stepList[history.stepIdx] = step;
        history.runCount = history.runCount + Math.abs(delta);
    }
    else {

        history.stepList.length = history.stepIdx + 1;
        history.stepList.push(step);
        history.runCount = Math.abs(delta);

        // The oldest step goes once the file has more of them than it keeps
        if(history.stepList.length > config.depth) {
            history.stepList.shift();
        }

        history.stepIdx = history.stepList.length - 1;
    }

    // A word just ended, so the run ends with it and the next keystroke is a step of its own
    var isWordEnd = delta > 0 && edit.isBreak(content.charAt(step.start - 1));

    if(isWordEnd) {
        history.stepTime = 0;
    }

    log.say('edit.remember', {
        path: table.path,
        isRun: isRun,
        isSoonEnough: isSoonEnough,
        isSameWay: isSameWay,
        isAdjacent: isAdjacent,
        isShortEnough: isShortEnough,
        isWordEnd: isWordEnd,
        sinceMS: sinceMS,
        delta: delta,
        runCount: history.runCount,
        stepIdx: history.stepIdx,
        stepCount: history.stepList.length,
        droppedCount: isRun ? 0 : droppedCount,
        length: content.length,
        diskLength: table.content.length,
        selectionStart: step.start,
        selectionEnd: step.end
    });
};

// ////////////////////////////////////////////////////////////////////////

// Whether the character ends a word, which is where one step of the history ends and the
// next one starts.
edit.isBreak = function(character) {

    var out = /\s/.test(character);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

edit.onKeyDown = function(event) {

    var isCommand = event.ctrlKey || event.metaKey;
    var key = event.key.toLowerCase();
    var isUndo = isCommand && key === 'z' && !event.shiftKey;
    var isRedo = isCommand && (key === 'y' || (key === 'z' && event.shiftKey));

    // Only what is meant for the history is worth a line, the rest of the typing being the
    // steps themselves, which are logged as they are taken
    if(isCommand) {

        var data = log.buildKey(event);

        data.isUndo = isUndo;
        data.isRedo = isRedo;

        log.say('edit.onKeyDown', data);
    }

    if(!isUndo && !isRedo) {
        return;
    }

    // The browser keeps a history of its own, which is not the one the file went through -
    // ours is the one that outlives a look at another file
    event.preventDefault();

    if(isUndo) {
        edit.step(-1);
    }
    else {
        edit.step(1);
    }
};

// ////////////////////////////////////////////////////////////////////////

// One step back through the file, or one forward. The step the file lands on is put on screen
// whole, caret and all, which is what makes it the file as it stood then.
edit.step = function(direction) {

    var table = tables.getCurrent();
    var history = edit.state.historyByPath[table.path];

    // A file the browser does not edit in place is read rather than worked on, so it went
    // through nothing there is to go back through
    if(history === undefined) {
        log.say('edit.step', {direction: direction, path: table.path, hasHistory: false});
        return;
    }

    var stepIdx = history.stepIdx + direction;
    var isWithin = stepIdx >= 0 && stepIdx < history.stepList.length;

    log.say('edit.step', {
        direction: direction,
        path: table.path,
        hasHistory: true,
        stepIdxFrom: history.stepIdx,
        stepIdxTo: stepIdx,
        stepCount: history.stepList.length,
        isWithin: isWithin
    });

    // The file is at one end of what it went through
    if(!isWithin) {
        return;
    }

    var step = history.stepList[stepIdx];

    history.stepIdx = stepIdx;

    // A step landed on is not a step taken, so the next keystroke starts a run of its own
    history.stepTime = 0;
    history.runCount = 0;
    history.runDelta = 0;

    edit.apply(table, step);
};

// ////////////////////////////////////////////////////////////////////////

edit.apply = function(table, step) {

    var content = tables.get('content');
    var previousContent = content.value;

    // The caret goes to the end of what this step changed rather than to where it stood when the
    // step was taken - a step taken back is read at the change it took back, and the end of the
    // file, which is where the caret of a step out of storage stands, is nowhere near it
    var at = edit.getChangeEnd(previousContent, step.content);

    content.value = step.content;
    content.setSelectionRange(at, at);

    log.say('edit.apply', {
        path: table.path,
        lengthFrom: previousContent.length,
        lengthTo: step.content.length,
        stepStart: step.start,
        changeEnd: at,
        isDraft: step.content !== table.content
    });

    // Nothing typed it, so the colors, the numbers down the left, what is unsaved and the star
    // that says so are all brought up to date by hand
    $.fn.zato.highlight.refresh(content);
    tables.gutter.refresh();
    tables.draft.remember(table, step.content);
    tables.renderModified();

    // A step taken back somewhere else in the file is one the reader is brought to, since a
    // change that cannot be seen reads as no change at all
    tables.wash.showLine(edit.getLineIdx(step.content, at));

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
        hasHistory: state.historyByPath[previousPath] !== undefined,
        caret: JSON.stringify(state.caretByPath[previousPath])
    });

    state.historyByPath[table.path] = state.historyByPath[previousPath];
    delete state.historyByPath[previousPath];

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
        hasHistory: edit.state.historyByPath[table.path] !== undefined,
        caret: JSON.stringify(edit.state.caretByPath[table.path])
    });

    delete edit.state.historyByPath[table.path];
    delete edit.state.caretByPath[table.path];

    edit.writeCaretSoon();
};

// ////////////////////////////////////////////////////////////////////////
// The carets between one visit and the next
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

    window.localStorage.setItem(edit.config.caretKey, text);
};

// ////////////////////////////////////////////////////////////////////////

edit.readCaret = function() {

    var out = {};
    var stored = window.localStorage.getItem(edit.config.caretKey);

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
