// Config files kit - what a part of the drawing stands for in the file itself.
//
// Every code and the value in the drawing carries the lines of the file it was drawn off,
// so resting on one washes those lines over in the file - the answer and the file it was
// read out of are then read as the one thing. A code carries the one line it came off, so
// a table that holds the same key twice is drawn as two codes that point at a line each,
// while the value carries every line that holds it.
//
// A group of the drawing is a table of the file, so resting on the box or on the name over
// it washes the whole of that table over, exactly as resting on the number of the line its
// name is on does.
//
// Several lines are washed one at a time, each in its turn, since one wash over half a
// file says nothing about which line is which. Whatever is washed is brought on screen
// first, so a line further down the file is seen rather than only counted.
//
// The drawing is also the box it is drawn in, and a drawing of a file that most systems
// agree on is taller than that box, so it is taken hold of and moved as well - anywhere
// but on a shape, which is there to be pointed at.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var trace = tables.trace;
var gutter = tables.gutter;
var wash = tables.wash;

// ////////////////////////////////////////////////////////////////////////

trace.config = {

    // How long one of several lines is washed for before the next one has its turn
    stepMs: 900,

    // What a whole table being pointed at is remembered as, so that it is never taken for
    // the lines of a code
    tablePrefix: 'table '
};

// ////////////////////////////////////////////////////////////////////////

trace.state = {

    // What the cursor is resting on, as the shape itself says it, and '' while the cursor
    // is resting on nothing
    mark: '',

    // The lines of the file that shape stands for, and which of them is washed right now
    lineList: [],
    lineIdx: 0,

    // What gives each of them its turn, 0 while there is only one line to wash
    timer: 0
};

// ////////////////////////////////////////////////////////////////////////

trace.init = function() {

    var host = tables.get('flow');

    // The shapes of the drawing come and go with every answer, so the drawing itself is
    // what listens rather than each shape of it
    host.addEventListener('mouseover', trace.enter);
    host.addEventListener('mouseleave', trace.stop);

    // A drawing taller than the room it has is taken hold of and moved, and what stands for
    // a line of the file is left to be pointed at rather than grabbed
    $.fn.zato.drag_scroll.attach({
        element: host,
        skip: trace.isShape
    });
};

// ////////////////////////////////////////////////////////////////////////

trace.isShape = function(event) {

    var out = event.target.getAttribute(tables.flow.config.lineMark) !== null;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

trace.enter = function(event) {

    var config = tables.flow.config;
    var element = event.target;

    var tableMark = element.getAttribute(config.tableMark);
    var lineMark = element.getAttribute(config.lineMark);
    var isTable = tableMark !== null;

    // The words beside a drop and the drawing's own air stand for nothing in the file, so
    // resting on either of them is resting on nothing
    if(!isTable && lineMark === null) {
        trace.stop();
        return;
    }

    // A chip is a box with a name on it, and a group is a box with a name over it - the
    // cursor crossing from the one to the other is still the cursor on the same thing
    var mark = isTable ? trace.config.tablePrefix + tableMark : lineMark;

    if(mark === trace.state.mark) {
        return;
    }

    trace.stop();

    if(isTable) {
        trace.startTable(mark, tableMark);
    }
    else {
        trace.start(mark);
    }
};

// ////////////////////////////////////////////////////////////////////////

// A whole table washed over at once, which is the block of the file that a copy taken from
// the number of its own line would take.
trace.startTable = function(mark, tableMark) {

    var lineIdx = parseInt(tableMark, 10);
    var lineList = gutter.getLineList();

    // The file on screen may have been cut short since the answer was drawn, and then there
    // is no table left to point at
    if(lineIdx >= lineList.length) {
        return;
    }

    trace.state.mark = mark;

    var block = gutter.getBlock(lineList, lineIdx);

    wash.scrollToBlock(block);
    wash.show(block, true);
};

// ////////////////////////////////////////////////////////////////////////

trace.start = function(mark) {

    var state = trace.state;
    var lineList = trace.readLines(mark);

    // The file on screen may have been cut short since the answer was drawn, and then there
    // is nothing left to point at
    if(!lineList.length) {
        return;
    }

    state.mark = mark;
    state.lineList = lineList;
    state.lineIdx = 0;

    trace.show();

    // One line is simply washed, several take it in turns
    if(lineList.length > 1) {
        state.timer = window.setInterval(trace.step, trace.config.stepMs);
    }
};

// ////////////////////////////////////////////////////////////////////////

trace.stop = function() {

    var state = trace.state;

    // Nothing was being pointed at, so nothing has to be taken back
    if(!state.mark) {
        return;
    }

    if(state.timer) {
        window.clearInterval(state.timer);
        state.timer = 0;
    }

    state.mark = '';
    state.lineList = [];
    state.lineIdx = 0;

    wash.hide();
};

// ////////////////////////////////////////////////////////////////////////

// The line whose turn it is, brought on screen and washed over. The wash is held, so the
// file being scrolled to it carries it along instead of taking it away.
trace.show = function() {

    var state = trace.state;
    var lineIdx = state.lineList[state.lineIdx];

    wash.scrollToLine(lineIdx);
    wash.show({start: lineIdx, count: 1}, true);
};

// ////////////////////////////////////////////////////////////////////////

trace.step = function() {

    var state = trace.state;

    state.lineIdx = (state.lineIdx + 1) % state.lineList.length;
    trace.show();
};

// ////////////////////////////////////////////////////////////////////////

// The lines a shape stands for, as the drawing wrote them onto it, and only those of them
// the file on screen still has - it may have been typed in since the answer was drawn.
trace.readLines = function(mark) {

    var partList = mark.split(tables.flow.config.lineMarkSeparator);
    var lineCount = gutter.getLineList().length;
    var out = [];

    for(var partIdx = 0; partIdx < partList.length; partIdx++) {

        var lineIdx = parseInt(partList[partIdx], 10);

        if(lineIdx < lineCount) {
            out.push(lineIdx);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
