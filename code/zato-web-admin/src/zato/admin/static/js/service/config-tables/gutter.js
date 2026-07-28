// Config tables - the numbers down the left of the file, and the copy they turn into.
//
// The column is only as wide as the numbers in it, so it is measured from the count
// of lines the file has rather than set to a width that would fit any file. The copy
// button is one button that follows the cursor down the column, wider than the column
// itself and reaching into the room the file leaves before its first character, which
// is what lets the numbers stay narrow.
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

    // The name of the air the stylesheet keeps between the tip of the button's point and
    // the first character of the file
    pointGapProperty: '--config-tables-point-gap'
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

    // The geometry of the column and of the button on it, read off them once per build
    // rather than per movement of the cursor
    lineHeight: 0,
    paddingTop: 0,
    pointLength: 0,
    pointGap: 0
};

// ////////////////////////////////////////////////////////////////////////

gutter.init = function() {

    var content = tables.get('content');

    gutter.buildButton();
    gutter.buildWash();

    // Typing adds and removes lines, and the numbers follow the file as it moves
    content.addEventListener('input', gutter.refresh);
    content.addEventListener('scroll', gutter.followScroll);

    // Which line the button is on comes off where the cursor is rather than off what
    // it is over, since the button itself is over the numbers it stands in for
    var body = gutter.getBody();

    body.addEventListener('mousemove', gutter.follow);
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

// How tall a line is, where the first one starts, how far the button's point comes out of
// it and what that point keeps ahead of itself, all as the stylesheet has them - which is
// what a cursor's position is turned into a line number by.
gutter.measure = function() {

    var element = tables.get('gutter');
    var row = element.firstElementChild.firstElementChild;
    var elementStyle = window.getComputedStyle(element);
    var pointStyle = window.getComputedStyle(gutter.button, '::after');
    var pointGap = elementStyle.getPropertyValue(gutter.config.pointGapProperty);

    gutter.state.lineHeight = row.offsetHeight;
    gutter.state.paddingTop = parseFloat(elementStyle.paddingTop);
    gutter.state.pointLength = parseFloat(pointStyle.borderLeftWidth);
    gutter.state.pointGap = parseFloat(pointGap);
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

// The button onto the line the cursor is level with, or off screen once the cursor is
// past the button's own right-hand edge, which is where the text of the file starts.
gutter.follow = function(event) {

    var state = gutter.state;
    var bodyRect = gutter.getBody().getBoundingClientRect();
    var offsetY = event.clientY - bodyRect.top;

    // The file begins where the air ahead of the point ends. Both the point and that air
    // count as part of the button, otherwise the cursor resting on either would be taken
    // for a cursor in the file.
    var buttonRight = gutter.button.getBoundingClientRect().right + state.pointLength + state.pointGap;

    if(event.clientX > buttonRight) {
        gutter.hide();
        return;
    }

    var scrollTop = tables.get('content').scrollTop;
    var lineIdx = Math.floor((offsetY - state.paddingTop + scrollTop) / state.lineHeight);

    // Above the first line and below the last one there is no line to copy
    if(lineIdx < 0 || lineIdx >= state.lineCount) {
        gutter.hide();
        return;
    }

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

    var top = state.paddingTop + lineIdx * state.lineHeight - scrollTop;

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
    var top = lineIdx * state.lineHeight;
    var bottom = top + state.lineHeight;

    if(top < content.scrollTop) {
        content.scrollTop = top;
        return;
    }

    var room = content.clientHeight - state.paddingTop;

    if(bottom > content.scrollTop + room) {
        content.scrollTop = bottom - room;
    }
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
