// Config tables - the numbers down the left of the file, and the copy they turn into.
//
// The column is only as wide as the numbers in it, so it is measured from the count
// of lines the file has rather than set to a width that would fit any file. The copy
// button is one button that follows the cursor down the column, wider than the column
// itself and reaching into the room the file leaves before its first character, which
// is what lets the numbers stay narrow.
//
// The cursor anywhere in a row of the column is the cursor on the line that row counts,
// the number itself and the room around it alike, so a line is copied without the number
// being aimed at. Which line that is comes off the row the cursor is over rather than off
// where the cursor is, so it is the very row that answers for itself.
//
// A line that names a section is a line that holds others, so copying it takes the
// whole section - its name and everything under it down to the next name of the same
// depth or above it. What that comes to is washed over in the file itself while the
// cursor is on the number, so what a press would take is read before it is taken.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var gutter = tables.gutter;

// ////////////////////////////////////////////////////////////////////////

gutter.config = {

    // What the button says, and where it says that it copied
    copyLabel: 'Copy',
    copyPlacement: 'left',

    // The classes the parts of the column wear
    rowClass: 'config-tables-gutter-line',
    numberClass: 'config-tables-gutter-number',
    buttonClass: 'zato-badge zato-badge-blue config-tables-copy config-tables-copy-small config-tables-gutter-copy',
    buttonVisibleClass: 'config-tables-gutter-copy-visible',

    // The wash over what a press would take, and the class that brings it on
    washClass: 'config-tables-copy-target',
    washVisibleClass: 'config-tables-copy-target-visible',

    // The button is the one thing here that a tooltip is anchored by, so it is the
    // one thing here with an id
    buttonId: 'config-tables-gutter-copy',

    // How wide the column is - one digit's worth per digit the last line number has,
    // plus the room its own padding takes
    widthPerDigit: 7,
    widthExtra: 8,

    // The name of the width the stylesheet lays the column out by
    widthProperty: '--config-tables-gutter-width',

    // The name of the room the file keeps before its first character, which is what the
    // button reaches over and how far past the numbers the cursor is still on a line
    fileInsetProperty: '--config-tables-file-inset',

    // What a row says about the line it counts
    lineAttribute: 'data-line'
};

// ////////////////////////////////////////////////////////////////////////

gutter.state = {

    // How many numbers are on screen, which is what says whether they are still the
    // right ones
    lineCount: 0,

    // The line the button is currently on, 0 while it is off screen
    lineNumber: 0,

    // What a press on that line would take, and the line it was worked out for - both
    // kept so that the file is only read again once the cursor reaches another line.
    // A block of null means the line has nothing on it to copy.
    block: null,
    blockLine: 0,

    // What the wash is over, so it can be put back where it belongs once the file is
    // scrolled, and whether something other than the cursor on a number is holding it
    // there - the drawing points at lines of the file with it as well
    washBlock: null,
    washHeld: false,

    // The geometry of the file and of the column beside it, read off them once per build
    // rather than per movement of the cursor
    lineHeight: 0,
    contentPadding: 0,
    paddingTop: 0,
    fileInset: 0
};

// ////////////////////////////////////////////////////////////////////////

gutter.init = function() {

    var content = tables.get('content');

    gutter.buildButton();
    gutter.buildWash();

    // Typing adds and removes lines, and the numbers follow the file as it moves
    content.addEventListener('input', gutter.refresh);
    content.addEventListener('scroll', gutter.followScroll);

    // Which line the button is on comes off the row the cursor is over, and the button
    // itself stands over the row it is for
    var body = gutter.getBody();

    body.addEventListener('mousemove', gutter.point);
    body.addEventListener('mouseleave', gutter.hide);

    gutter.refresh();
};

// ////////////////////////////////////////////////////////////////////////

gutter.buildButton = function() {

    var config = gutter.config;

    var button = document.createElement('button');
    button.type = 'button';
    button.id = config.buttonId;
    button.className = config.buttonClass;
    button.textContent = config.copyLabel;

    button.addEventListener('click', gutter.copy);

    gutter.getBody().appendChild(button);
    gutter.button = button;
};

// ////////////////////////////////////////////////////////////////////////

// The wash is the first thing in the box the file is read in, which leaves the overlay
// the file is colored on where it was - the one right in front of the textarea, since
// that is the one the textarea is found by.
gutter.buildWash = function() {

    var wash = document.createElement('div');
    wash.className = gutter.config.washClass;

    var wrapper = tables.get('content').parentNode;
    wrapper.insertBefore(wash, wrapper.firstChild);

    gutter.wash = wash;
};

// ////////////////////////////////////////////////////////////////////////

// The numbers as many as the file has lines. Nothing is rebuilt while that count
// stays as it is, so typing inside a line costs nothing at all.
gutter.refresh = function() {

    var lineCount = gutter.getLineList().length;

    if(lineCount !== gutter.state.lineCount) {
        gutter.state.lineCount = lineCount;
        gutter.build(lineCount);
    }

    // The file reads differently now, so what was worked out off it no longer holds
    gutter.state.blockLine = 0;
    gutter.followScroll();
};

// ////////////////////////////////////////////////////////////////////////

gutter.build = function(lineCount) {

    var lines = document.createElement('div');
    lines.className = 'config-tables-gutter-lines';

    for(var lineIdx = 0; lineIdx < lineCount; lineIdx++) {
        lines.appendChild(gutter.buildRow(lineIdx + 1));
    }

    var element = tables.get('gutter');
    element.textContent = '';
    element.appendChild(lines);

    gutter.setWidth(lineCount);
    gutter.measure();
};

// ////////////////////////////////////////////////////////////////////////

gutter.buildRow = function(lineNumber) {

    var row = document.createElement('div');
    row.className = gutter.config.rowClass;

    // The row is what says which line it is for, so the cursor being anywhere on it is
    // enough - nothing is worked out from where the cursor is
    row.setAttribute(gutter.config.lineAttribute, lineNumber - 1);

    var number = document.createElement('span');
    number.className = gutter.config.numberClass;
    number.textContent = lineNumber;
    row.appendChild(number);

    return row;
};

// ////////////////////////////////////////////////////////////////////////

// As wide as the longest number it will hold, so a file of twenty lines is not given
// the column a file of thousands needs. The width goes onto the whole editor, since
// the row of buttons under the file steps in by it to line up with the file's own
// left-hand edge.
gutter.setWidth = function(lineCount) {

    var config = gutter.config;
    var digitCount = String(lineCount).length;
    var width = digitCount * config.widthPerDigit + config.widthExtra;

    tables.get('editor').style.setProperty(config.widthProperty, width + 'px');
};

// ////////////////////////////////////////////////////////////////////////

// How tall a line is, how much room the file keeps above its first one and how much it
// keeps before its first character - the file itself is asked for all of it, so what the
// wash is placed by is what the file is actually laid out as.
gutter.measure = function() {

    var state = gutter.state;
    var element = tables.get('gutter');
    var row = element.firstElementChild.firstElementChild;
    var elementStyle = window.getComputedStyle(element);
    var contentStyle = window.getComputedStyle(tables.get('content'));
    var fileInset = elementStyle.getPropertyValue(gutter.config.fileInsetProperty);

    state.lineHeight = row.offsetHeight;

    // The room above the first line as a scroll counts it, which is from the inside of the
    // file's box, and as the wash and the button are placed, which is from the outside of it
    state.contentPadding = parseFloat(contentStyle.paddingTop);
    state.paddingTop = state.contentPadding + parseFloat(contentStyle.borderTopWidth);

    state.fileInset = parseFloat(fileInset);
};

// ////////////////////////////////////////////////////////////////////////

// The numbers sit where the lines they belong to are, which means moving with the
// file rather than with the page.
gutter.followScroll = function() {

    var lines = tables.get('gutter').firstElementChild;
    var scrollTop = tables.get('content').scrollTop;

    lines.style.transform = 'translateY(' + (-scrollTop) + 'px)';

    // A wash the drawing put there is about a line rather than about where the cursor is,
    // so it travels with the file instead of going out
    if(gutter.state.washHeld) {
        gutter.positionWash();
        return;
    }

    // The line under the cursor is another one now, and where the cursor is will not
    // be known again until it moves
    gutter.hide();
};

// ////////////////////////////////////////////////////////////////////////

// What the cursor has reached - a row of the column, the button that stands on one, or the
// file itself, which is where the button is away.
gutter.point = function(event) {

    var button = gutter.button;
    var target = event.target;

    // The button covers the very row it is for, its point included, so reaching it is
    // reaching that row again
    if(target === button || button.contains(target)) {
        return;
    }

    var row = target.closest('.' + gutter.config.rowClass);

    if(row !== null) {
        gutter.follow(row);
        return;
    }

    // The point stops short of the first character of the file by a little air, and that air
    // is the button's own room rather than the file's, so the cursor in it holds the button
    // where it is
    if(gutter.state.lineNumber && event.clientX <= gutter.getReach()) {
        return;
    }

    gutter.hide();
};

// ////////////////////////////////////////////////////////////////////////

// How far to the right of the column the button still counts as being pointed at.
gutter.getReach = function() {

    var out = tables.get('gutter').getBoundingClientRect().right + gutter.state.fileInset;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The button onto the row the cursor is on, level with it, since that row is where the line
// it counts is on screen.
gutter.follow = function(row) {

    var state = gutter.state;
    var lineIdx = parseInt(row.getAttribute(gutter.config.lineAttribute), 10);

    // What a press would take is read off the file, so it is worked out again only once
    // the cursor has reached another line
    if(state.blockLine !== lineIdx + 1) {
        state.blockLine = lineIdx + 1;
        state.block = gutter.readBlock(lineIdx);
    }

    // A line with nothing on it at all is nothing to take a copy of - one with only
    // spaces on it is still something
    if(state.block === null) {
        gutter.hide();
        return;
    }

    var top = row.getBoundingClientRect().top - gutter.getBody().getBoundingClientRect().top;

    state.lineNumber = lineIdx + 1;

    gutter.button.style.top = top + 'px';
    gutter.button.classList.add(gutter.config.buttonVisibleClass);

    gutter.showWash(state.block, false);
};

// ////////////////////////////////////////////////////////////////////////

// What a press on one line would take, or null when that line holds nothing at all.
gutter.readBlock = function(lineIdx) {

    var lineList = gutter.getLineList();

    if(!lineList[lineIdx].length) {
        return null;
    }

    var out = gutter.getBlock(lineList, lineIdx);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The wash over a block of the file, level with the first line of it. Held, it stays until
// whoever put it there takes it away - that is the drawing pointing at a line rather than
// the cursor resting on a number, and the cursor is elsewhere on the page by then.
gutter.showWash = function(block, held) {

    var state = gutter.state;
    var height = block.count * state.lineHeight;

    state.washBlock = block;
    state.washHeld = held;

    gutter.wash.style.height = height + 'px';
    gutter.wash.classList.add(gutter.config.washVisibleClass);

    gutter.positionWash();
};

// ////////////////////////////////////////////////////////////////////////

// Where the wash goes is where the first line of its block is, which moves as the file is
// scrolled under it.
gutter.positionWash = function() {

    var state = gutter.state;
    var scrollTop = tables.get('content').scrollTop;
    var top = state.paddingTop + state.washBlock.start * state.lineHeight - scrollTop;

    gutter.wash.style.top = top + 'px';
};

// ////////////////////////////////////////////////////////////////////////

// The file is scrolled only as far as it takes for a line to be on screen, so a line that
// is there already is left where it is.
gutter.scrollToLine = function(lineIdx) {

    var state = gutter.state;
    var content = tables.get('content');

    // Where the line is inside the file's own box, the room it keeps above its first
    // line counted in
    var top = state.contentPadding + lineIdx * state.lineHeight;
    var bottom = top + state.lineHeight;

    if(top < content.scrollTop) {
        content.scrollTop = top;
        return;
    }

    if(bottom > content.scrollTop + content.clientHeight) {
        content.scrollTop = bottom - content.clientHeight;
    }
};

// ////////////////////////////////////////////////////////////////////////

// A block is brought on screen from its start, so a table taller than the room there is for
// it is read from its name down rather than from its last line up.
gutter.scrollToBlock = function(block) {

    gutter.scrollToLine(block.start + block.count - 1);
    gutter.scrollToLine(block.start);
};

// ////////////////////////////////////////////////////////////////////////

gutter.hideWash = function() {

    gutter.state.washBlock = null;
    gutter.state.washHeld = false;
    gutter.wash.classList.remove(gutter.config.washVisibleClass);
};

// ////////////////////////////////////////////////////////////////////////

gutter.hide = function() {

    gutter.state.lineNumber = 0;
    gutter.button.classList.remove(gutter.config.buttonVisibleClass);

    // What the drawing is pointing at is not the cursor's to take away
    if(gutter.state.washHeld) {
        return;
    }

    gutter.hideWash();
};

// ////////////////////////////////////////////////////////////////////////

// What the button copies is the very block the wash is over.
gutter.copy = function() {

    var lineList = gutter.getLineList();
    var block = gutter.state.block;
    var text = lineList.slice(block.start, block.start + block.count).join('\n');

    $.fn.zato.copy.to_clipboard(gutter.button, text, gutter.config.copyPlacement, $.fn.zato.copy.config.offset);
};

// ////////////////////////////////////////////////////////////////////////

// What one line stands for - itself, or the whole section when it is the name of one.
// A section runs from its name to the line before the next name of its own depth or
// above it, so anything nested inside it is part of it, and the blank lines it is
// separated from the next one by are left behind.
gutter.getBlock = function(lineList, lineIdx) {

    var depth = gutter.getSectionDepth(lineList[lineIdx]);

    // A line that names nothing stands for itself alone
    if(!depth) {
        return {start: lineIdx, count: 1};
    }

    var lastIdx = lineIdx;
    var readIdx = lineIdx + 1;

    while(readIdx < lineList.length) {

        var line = lineList[readIdx];
        var lineDepth = gutter.getSectionDepth(line);

        // A name at this depth or above it starts something else, which is where
        // this section ends
        if(lineDepth && lineDepth <= depth) {
            break;
        }

        // An empty line counts as part of the section only once something follows it
        if(line.trim()) {
            lastIdx = readIdx;
        }

        readIdx++;
    }

    var out = {start: lineIdx, count: lastIdx - lineIdx + 1};
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// How many brackets a name opens with, which is how deeply nested it is - zero for
// a line that is not a name at all.
gutter.getSectionDepth = function(line) {

    var match = line.match($.fn.zato.highlight.config.section_parts_pattern);
    var out = match === null ? 0 : match[2].length;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

gutter.getLineList = function() {

    var out = tables.get('content').value.split('\n');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

gutter.getBody = function() {

    var out = tables.get('gutter').parentNode;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
