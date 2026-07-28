// Config tables - what a part of the drawing stands for in the file itself.
//
// Every code and the value in the drawing carries the lines of the file it was drawn off,
// so resting on one washes those lines over in the file - the answer and the file it was
// read out of are then read as the one thing. A code carries the one line it came off, so
// a table that holds the same key twice is drawn as two codes that point at a line each,
// while the value carries every line that holds it.
//
// Several lines are washed one at a time, each in its turn, since one wash over half a
// file says nothing about which line is which. Whatever is washed is brought on screen
// first, so a line further down the file is seen rather than only counted.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var trace = tables.trace;
var gutter = tables.gutter;

// ////////////////////////////////////////////////////////////////////////

trace.config = {

    // How long one of several lines is washed for before the next one has its turn
    stepMs: 900
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
};

// ////////////////////////////////////////////////////////////////////////

trace.enter = function(event) {

    var mark = event.target.getAttribute(tables.flow.config.lineMark);

    // The box a group of codes stands in, the words beside a drop, the drawing's own air -
    // none of them stands for a line of the file, so resting on one is resting on nothing
    if(mark === null) {
        trace.stop();
        return;
    }

    // A chip is a box with a name on it, and the cursor crossing from the one to the other
    // is still the cursor on the same code
    if(mark === trace.state.mark) {
        return;
    }

    trace.stop();
    trace.start(mark);
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

    gutter.hideWash();
};

// ////////////////////////////////////////////////////////////////////////

// The line whose turn it is, brought on screen and washed over. The wash is held, so the
// file being scrolled to it carries it along instead of taking it away.
trace.show = function() {

    var state = trace.state;
    var lineIdx = state.lineList[state.lineIdx];

    gutter.scrollToLine(lineIdx);
    gutter.showWash({start: lineIdx, count: 1}, true);
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
