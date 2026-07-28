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

    // Typing that goes on with no more than this long between two keystrokes is one step of
    // the history, so Ctrl-Z takes back a word or a line rather than a letter
    coalesceMS: 500,

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

    edit.applyCaret(table);

    var data = log.buildTable(table);

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

// A file starts with one step, which is what it says now - there is nothing before it to go
// back to and nothing after it to go forward to.
edit.buildHistory = function(table) {

    var content = tables.draft.get(table);

    var out = {
        stepList: [{content: content, start: content.length, end: content.length}],
        stepIdx: 0,
        stepTime: 0
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One more step of the file, taken as it is typed into. A run of typing is one step, so the
// step at the top grows for as long as the typing goes on, and anything that had been taken
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

    var isRun = now - history.stepTime < config.coalesceMS;
    var sinceMS = history.stepTime === 0 ? -1 : now - history.stepTime;
    var droppedCount = history.stepList.length - (history.stepIdx + 1);

    history.stepTime = now;

    if(isRun) {
        history.stepList[history.stepIdx] = step;
    }
    else {

        history.stepList.length = history.stepIdx + 1;
        history.stepList.push(step);

        // The oldest step goes once the file has more of them than it keeps
        if(history.stepList.length > config.depth) {
            history.stepList.shift();
        }

        history.stepIdx = history.stepList.length - 1;
    }

    log.say('edit.remember', {
        path: table.path,
        isRun: isRun,
        sinceMS: sinceMS,
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

    edit.apply(table, step);
};

// ////////////////////////////////////////////////////////////////////////

edit.apply = function(table, step) {

    var content = tables.get('content');
    var previousLength = content.value.length;

    content.value = step.content;
    content.setSelectionRange(step.start, step.end);

    log.say('edit.apply', {
        path: table.path,
        lengthFrom: previousLength,
        lengthTo: step.content.length,
        selectionStart: step.start,
        selectionEnd: step.end,
        isDraft: step.content !== table.content
    });

    // Nothing typed it, so the colors, the numbers down the left, what is unsaved and the star
    // that says so are all brought up to date by hand
    $.fn.zato.highlight.refresh(content);
    tables.gutter.refresh();
    tables.draft.remember(table, step.content);
    tables.renderModified();

    edit.rememberCaret();
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

    log.say('edit.applyCaret', {
        path: table.path,
        hasCaret: true,
        wanted: JSON.stringify(caret),
        selectionStart: start,
        selectionEnd: end,
        length: last,
        scrollTop: content.scrollTop
    });
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
