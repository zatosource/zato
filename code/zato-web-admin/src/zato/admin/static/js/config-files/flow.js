// Config files kit - the answer for a mapping set, drawn rather than written.
//
// A mapping set holds a table per party, so its answer reads as a story down the middle of
// the column: the table the value came in from maps it to what the file holds, and that
// maps on to the codes of the table on the other side - the same thing happening twice,
// which is why every drop of it says the one word. The codes of one table stand together
// inside a dashed group of its own, so a value that several codes of the same table map to
// is seen as exactly that, and every table the value reaches is drawn rather than counted.
//
// The drawing is drawn at the size it is laid out at rather than shrunk to the column it
// sits in, since a name is there to be read. It is as wide as the longest name in it asks
// for, up to the limit it may grow to, and a column too narrow for that is scrolled.
//
// Nothing in it is ever cut short. A name or a value longer than the room the drawing grew
// to runs on over as many lines as it takes, so a file of long values is read in full, and
// a press on any of them takes a copy of the whole of it rather than of what is on screen.
//
// The drawing is laid out here and drawn at whatever size it is being looked at, which is
// zoom.js - Ctrl and the wheel over the room the answer has is what says that size.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.config_files;
var flow = tables.flow;

// ////////////////////////////////////////////////////////////////////////

flow.config = {

    // The width a drawing of short names comes to, which is about what the column it goes
    // into holds, and how much of it is kept clear around the drawing. A longer name than
    // that width holds grows the whole drawing, up to as many times the room it started
    // with as the limit says.
    width: 210,
    padding: 10,
    roomLimit: 3,

    // A group of codes - where the box they stand in starts, how wide it is before any
    // name grows it, the room it keeps inside itself, and where the name of the table goes
    groupX: 6,
    groupWidth: 198,
    groupInset: 10,
    captionHeight: 25,
    captionBaseline: 17,
    captionLineHeight: 13,

    // How far apart two groups stand when the value reaches more than one table
    groupGap: 9,

    // One code of a table, and how much taller it stands for every line its name runs on to
    chipHeight: 24,
    chipGap: 8,
    chipInset: 11,
    chipBaseline: 17,
    chipLineHeight: 16,
    rowGap: 8,

    // The value the whole drawing turns on
    valueHeight: 28,
    valueInset: 13,
    valueBaseline: 20,
    valueLineHeight: 18,

    // The drop from one part of the story to the next, and where the words that go with
    // that drop stand
    connectorLength: 30,
    labelOffset: 8,
    labelBaseline: 4,
    arrowLength: 6,
    arrowWidth: 4,

    // How wide one character of each face is, which is what says how much room a name
    // asks for. The words about the drawing are set in a face of their own, and a narrower
    // one, so they are measured against a width of their own as well.
    charWidth: 7.8,
    valueCharWidth: 9,
    wordCharWidth: 5.5,

    // The corners are kept as tight as the ones the badges in the listing wear
    corner: 2,

    // What a shape of the drawing says about the lines of the file it stands for, which is
    // what trace.js reads it by - a code and the value stand for lines of their own, while
    // a group stands for the whole table, said as the line its name is on
    lineMark: 'data-flow-lines',
    lineMarkSeparator: ',',
    tableMark: 'data-flow-table',

    // What a shape says it stands for, in full, which is what a press on it copies, which of the
    // drawing's boxes the shape belongs to, and the id the box being copied from wears while it
    // says that it was copied
    textMark: 'data-flow-text',
    boxMark: 'data-flow-box',
    copyAnchorId: 'config-files-flow-copy-anchor',

    // Where the words that say so stand - beside the shape, close enough to be reading off it
    // rather than off the drawing. The distance is measured to the box the words are in, and the
    // point they wear pokes seven of it back towards the shape, so eight leaves the point just
    // short of the shape's own edge rather than inside it
    copyPlacement: 'left',
    copyOffset: [0, 8],

    // The classes the parts of the drawing wear, so what they look like stays in the
    // stylesheet
    groupClass: 'config-files-flow-group',
    captionClass: 'config-files-flow-caption',
    chipClass: 'config-files-flow-chip',
    chipNoteClass: 'config-files-flow-chip-note',
    chipTextClass: 'config-files-flow-chip-text',
    noteTextClass: 'config-files-flow-note-text',
    valueClass: 'config-files-flow-value',
    valueTextClass: 'config-files-flow-value-text',
    labelClass: 'config-files-flow-label',
    lineClass: 'config-files-flow-line',
    arrowClass: 'config-files-flow-arrow',
    drawnClass: 'config-files-result-drawn'
};

// ////////////////////////////////////////////////////////////////////////

// How wide this drawing is, and everything worked out off that - the line it all stands
// on and the box a group of codes goes into. It is read once per drawing and then held,
// since every part of the drawing is laid out about the same middle.
flow.layout = {
    width: 0,
    center: 0,
    groupWidth: 0
};

// ////////////////////////////////////////////////////////////////////////

flow.state = {

    // The shape the last copy was taken from, which wears the id the words are anchored by
    // until another shape is pressed
    anchor: null,

    // The box of every code and of the value, in the order they were drawn, which is what the
    // parts of a shape name themselves by
    boxList: []
};

// ////////////////////////////////////////////////////////////////////////

flow.init = function() {

    // The shapes come and go with every answer, so the drawing itself is what listens
    tables.get('flow').addEventListener('click', flow.copy);

    // How closely the drawing is looked at is its own affair, and the room it is in is what
    // answers to the wheel
    tables.zoom.init();
};

// ////////////////////////////////////////////////////////////////////////

// A press on a code or on the value takes a copy of what it stands for, whole, and says so
// beside the very shape that was pressed.
flow.copy = function(event) {

    var config = flow.config;
    var element = event.target;
    var text = element.getAttribute(config.textMark);

    // The box a group stands in, the words beside a drop, the drawing's own air - a press
    // on any of them is a press on nothing to copy
    if(text === null) {
        return;
    }

    // The words go beside the box the shape is drawn as, whether the press landed on the box or
    // on the letters inside it - the letters stand well in from the edges, and words hung on them
    // would read as being inside the shape rather than beside it
    var box = flow.state.boxList[Number(element.getAttribute(config.boxMark))];

    // The words are anchored by an id, and one id belongs to one shape, so the shape that
    // held it before hands it over
    if(flow.state.anchor) {
        flow.state.anchor.removeAttribute('id');
    }

    box.id = config.copyAnchorId;
    flow.state.anchor = box;

    $.fn.zato.copy.to_clipboard(box, text, config.copyPlacement, config.copyOffset);
};

// ////////////////////////////////////////////////////////////////////////

// The whole story, from the top down. Nothing goes on screen until the last part of it
// is laid out, since that is what says how tall the drawing turned out to be.
flow.render = function(model) {

    var config = flow.config;
    var words = tables.config;
    var svg = flow.createElement('svg');
    var cursor = {y: config.padding, svg: svg};

    // The shapes of the drawing before this one are gone, and so are the boxes they were hung on
    flow.state.boxList = [];
    flow.state.anchor = null;

    flow.measure(model);

    // The table the value came in from, with every code of it that maps to the same
    // value ..
    flow.addGroup(cursor, {
        caption: tables.buildGroupCaption(model.sourceTable, model.sourceEntryList.length),
        entryList: model.sourceEntryList,
        tableLine: model.sourceTableLine,
        note: ''
    });

    // .. what the file maps it to ..
    flow.addConnector(cursor, words.flowMapsToLabel);
    flow.addValue(cursor, model.value, model.valueLineList);

    // .. and where it goes from there.
    flow.addTargetGroups(cursor, model);

    var height = cursor.y + config.padding;
    var width = flow.layout.width;

    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);

    // The size it was laid out at, which is what how closely it is looked at is measured off
    tables.zoom.remember(width, height);

    var host = tables.get('flow');

    // The shapes that were being pointed at are about to be gone
    tables.trace.stop();

    host.textContent = '';
    host.appendChild(svg);

    // A drawing comes up as large as the last one was left
    tables.zoom.apply();

    tables.get('result-area').classList.add(config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// The answer as text again, which is what a code list gets and what anything the file
// has nothing for gets.
flow.clear = function() {

    tables.trace.stop();

    flow.state.boxList = [];
    flow.state.anchor = null;

    tables.get('flow').textContent = '';
    tables.get('result-area').classList.remove(flow.config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// How wide this drawing has to be for the longest name in it to be read whole. A name
// longer than the room a chip started with grows every box of the drawing by what it is
// short of, and only a name past the limit is cut - a file of long keys is then read at
// the width it asks for rather than as a column of dots.
flow.measure = function(model) {

    var config = flow.config;
    var base = flow.getChipRoom(config.groupWidth);
    var wanted = Math.max(flow.getNeeded(model), base);
    var extra = Math.min(wanted, base * config.roomLimit) - base;
    var width = config.width + extra;

    flow.layout = {
        width: width,
        center: width / 2,
        groupWidth: config.groupWidth + extra
    };
};

// ////////////////////////////////////////////////////////////////////////

// The room the longest thing in the drawing asks for, said as the room a chip has for its
// text - the one width every other part of the drawing is worked out from.
flow.getNeeded = function(model) {

    var config = flow.config;
    var valueRoom = model.value.length * config.valueCharWidth + (config.valueInset - config.chipInset) * 2;

    var out = Math.max(
        flow.getCaptionNeeded(model.sourceTable, model.sourceEntryList.length),
        flow.getEntryListNeeded(model.sourceEntryList),
        valueRoom
    );

    if(model.targetTable) {

        var noteRoom = model.targetNote.length * config.wordCharWidth;

        out = Math.max(
            out,
            flow.getCaptionNeeded(model.targetTable, model.targetEntryList.length),
            flow.getEntryListNeeded(model.targetEntryList),
            noteRoom
        );
    }

    for(var otherIdx = 0; otherIdx < model.otherList.length; otherIdx++) {

        var other = model.otherList[otherIdx];

        out = Math.max(
            out,
            flow.getCaptionNeeded(other.name, other.entryList.length),
            flow.getEntryListNeeded(other.entryList)
        );
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A name over a group has the room a chip has plus the room a chip keeps around its own
// text, so what it asks for is that much less than its own width
flow.getCaptionNeeded = function(tableName, keyCount) {

    var config = flow.config;
    var caption = tables.buildGroupCaption(tableName, keyCount);

    var out = caption.length * config.wordCharWidth - config.chipInset * 2;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.getEntryListNeeded = function(entryList) {

    var config = flow.config;
    var out = 0;

    for(var entryIdx = 0; entryIdx < entryList.length; entryIdx++) {
        out = Math.max(out, entryList[entryIdx].key.length * config.charWidth);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The room a chip has for its own text, out of the width of the box it stands in.
flow.getChipRoom = function(groupWidth) {

    var config = flow.config;
    var out = groupWidth - config.groupInset * 2 - config.chipInset * 2;

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Where the value goes - the table that was asked about, and otherwise every other table
// of the file that maps to the same value.
flow.addTargetGroups = function(cursor, model) {

    var words = tables.config;

    if(model.targetTable) {

        flow.addConnector(cursor, words.flowUsedByLabel);

        flow.addGroup(cursor, {
            caption: tables.buildGroupCaption(model.targetTable, model.targetEntryList.length),
            entryList: model.targetEntryList,
            tableLine: model.targetTableLine,
            note: model.targetNote
        });

        return;
    }

    if(!model.otherList.length) {
        return;
    }

    flow.addConnector(cursor, words.flowUsedByLabel);

    for(var otherIdx = 0; otherIdx < model.otherList.length; otherIdx++) {

        var other = model.otherList[otherIdx];

        // The drop leads into the first group, and the rest stand under it
        if(otherIdx) {
            cursor.y = cursor.y + flow.config.groupGap;
        }

        flow.addGroup(cursor, {
            caption: tables.buildGroupCaption(other.name, other.entryList.length),
            entryList: other.entryList,
            tableLine: other.lineIdx,
            note: ''
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

// One table - its name over the codes it holds the value under, all of them inside a box
// of its own.
flow.addGroup = function(cursor, group) {

    var config = flow.config;
    var layout = flow.layout;
    var top = cursor.y;

    var captionRoom = layout.groupWidth - config.groupInset * 2;
    var captionLineList = flow.wrap(group.caption, captionRoom, config.wordCharWidth);
    var captionHeight = config.captionHeight + (captionLineList.length - 1) * config.captionLineHeight;

    var rowList = flow.buildRows(group);
    var height = flow.getGroupHeight(captionHeight, rowList);

    var box = flow.addRect(cursor.svg, config.groupX, top, layout.groupWidth, height, config.groupClass);

    var captionList = flow.addTextLines(cursor.svg, layout.center, top + config.captionBaseline, captionLineList,
        config.captionClass, config.captionLineHeight);

    // The box and the name on it are the table itself, so resting on either of them points
    // at the whole of that table in the file
    flow.markTable([box].concat(captionList), group.tableLine);

    var rowTop = top + captionHeight;

    for(var rowIdx = 0; rowIdx < rowList.length; rowIdx++) {

        var row = rowList[rowIdx];

        flow.addRow(cursor.svg, row, rowTop);
        rowTop = rowTop + flow.getRowHeight(row) + config.rowGap;
    }

    cursor.y = top + height;
};

// ////////////////////////////////////////////////////////////////////////

// A row is as tall as the code in it whose name runs on over the most lines.
flow.getRowHeight = function(row) {

    var out = 0;

    for(var chipIdx = 0; chipIdx < row.length; chipIdx++) {
        out = Math.max(out, row[chipIdx].height);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.getGroupHeight = function(captionHeight, rowList) {

    var config = flow.config;
    var rows = (rowList.length - 1) * config.rowGap;

    for(var rowIdx = 0; rowIdx < rowList.length; rowIdx++) {
        rows = rows + flow.getRowHeight(rowList[rowIdx]);
    }

    var out = captionHeight + rows + config.groupInset;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The codes of one table, in as many rows as they take - a table of a dozen codes reads
// as a block of them rather than as a column running off the screen.
flow.buildRows = function(group) {

    var config = flow.config;
    var chipList = flow.buildChips(group);
    var room = flow.layout.groupWidth - config.groupInset * 2;

    var out = [];
    var row = [];
    var used = 0;

    for(var chipIdx = 0; chipIdx < chipList.length; chipIdx++) {

        var chip = chipList[chipIdx];
        var needed = chip.width;

        if(row.length) {
            needed = needed + config.chipGap;
        }

        // A row with no room left for the next code hands over to another one
        if(used + needed > room) {
            out.push(row);
            row = [];
            used = 0;
            needed = chip.width;
        }

        row.push(chip);
        used = used + needed;
    }

    if(row.length) {
        out.push(row);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.buildChips = function(group) {

    var config = flow.config;
    var out = [];

    // A table with nothing for the value stands for itself, said in the few words a chip
    // has room for. There is no line of its own behind it, so it points at the table it is
    // said about, the same way the box around it does.
    if(group.note) {

        var note = flow.buildChip(group.note, config.chipNoteClass, config.noteTextClass, config.wordCharWidth, []);

        note.tableLine = group.tableLine;
        out.push(note);

        return out;
    }

    // One chip per line the table holds the value on, each of them pointing back at its own
    // line - two lines that say the same thing are two chips that point at one line each
    for(var entryIdx = 0; entryIdx < group.entryList.length; entryIdx++) {

        var entry = group.entryList[entryIdx];

        out.push(flow.buildChip(entry.key, config.chipClass, config.chipTextClass, config.charWidth, [entry.lineIdx]));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A chip is as wide as the text it ends up carrying and as tall as the lines that text runs
// on to, and it carries both the lines of the file it stands for and the whole of what it
// says - a name that runs on over several lines is still copied as the one name.
flow.buildChip = function(text, className, textClass, charWidth, lineList) {

    var config = flow.config;
    var room = flow.getChipRoom(flow.layout.groupWidth);
    var textLineList = flow.wrap(text, room, charWidth);

    var out = {
        text: text,
        textLineList: textLineList,
        width: flow.getLongest(textLineList) * charWidth + config.chipInset * 2,
        height: config.chipHeight + (textLineList.length - 1) * config.chipLineHeight,
        lineHeight: config.chipLineHeight,
        className: className,
        textClass: textClass,
        lineList: lineList,

        // A code stands for a line of its own rather than for the whole table it is in
        tableLine: tables.parse.config.noSectionLine
    };

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One row of codes, laid out about the line everything else stands on.
flow.addRow = function(svg, row, top) {

    var config = flow.config;
    var total = (row.length - 1) * config.chipGap;

    for(var widthIdx = 0; widthIdx < row.length; widthIdx++) {
        total = total + row[widthIdx].width;
    }

    var left = flow.layout.center - total / 2;

    for(var chipIdx = 0; chipIdx < row.length; chipIdx++) {

        var chip = row[chipIdx];
        var middle = left + chip.width / 2;

        var rect = flow.addRect(svg, left, top, chip.width, chip.height, chip.className);

        var textList = flow.addTextLines(svg, middle, top + config.chipBaseline, chip.textLineList,
            chip.textClass, chip.lineHeight);

        // Every part of a chip says the same thing, so the same line is pointed at and the
        // same text is copied wherever on it the cursor is
        var partList = [rect].concat(textList);

        flow.markAll(partList, chip.lineList, chip.text);
        flow.markTable(partList, chip.tableLine);

        left = left + chip.width + config.chipGap;
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the file holds for the code, which is the one thing in the drawing that stands on
// its own rather than inside a table - and it stands for every line of the file that holds
// it rather than for one of them.
flow.addValue = function(cursor, value, lineList) {

    var config = flow.config;
    var layout = flow.layout;
    var top = cursor.y;
    var room = layout.groupWidth - config.valueInset * 2;
    var textLineList = flow.wrap(value, room, config.valueCharWidth);

    var width = flow.getLongest(textLineList) * config.valueCharWidth + config.valueInset * 2;
    var height = config.valueHeight + (textLineList.length - 1) * config.valueLineHeight;
    var left = layout.center - width / 2;

    var rect = flow.addRect(cursor.svg, left, top, width, height, config.valueClass);

    var textList = flow.addTextLines(cursor.svg, layout.center, top + config.valueBaseline, textLineList,
        config.valueTextClass, config.valueLineHeight);

    flow.markAll([rect].concat(textList), lineList, value);

    cursor.y = top + height;
};

// ////////////////////////////////////////////////////////////////////////

// The drop from one part of the story to the next, with the words that say what it is.
flow.addConnector = function(cursor, labelText) {

    var config = flow.config;
    var center = flow.layout.center;
    var top = cursor.y;
    var bottom = top + config.connectorLength;
    var middle = top + config.connectorLength / 2 + config.labelBaseline;
    var labelX = center + config.labelOffset;

    flow.addLine(cursor.svg, center, top, center, bottom);
    flow.addArrow(cursor.svg, center, bottom);
    flow.addText(cursor.svg, labelX, middle, labelText, config.labelClass, 'start');

    cursor.y = bottom;
};

// ////////////////////////////////////////////////////////////////////////
// The shapes - the kit's SVG primitives, called with this drawing's own
// corners, classes and arrowhead measures
// ////////////////////////////////////////////////////////////////////////

flow.createElement = function(name) {

    var out = $.fn.zato.dashboard_kit.draw.createElement(name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.addRect = function(svg, x, y, width, height, className) {

    var out = $.fn.zato.dashboard_kit.draw.addRect(svg, x, y, width, height, className, flow.config.corner);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.addText = function(svg, x, y, text, className, anchor) {

    var out = $.fn.zato.dashboard_kit.draw.addText(svg, x, y, text, className, anchor);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.addTextLines = function(svg, x, baseline, textLineList, className, lineHeight) {

    var out = $.fn.zato.dashboard_kit.draw.addTextLines(svg, x, baseline, textLineList, className, lineHeight);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The lines of the file a shape of the drawing stands for, put onto the shape itself - one
// for a code, every line that holds the value for the value. That is all trace.js has to
// read to point at them, so what is pointed at is the very thing that was drawn.
flow.mark = function(element, lineList) {

    // A shape that stands for nothing in the file, which is what a note is
    if(!lineList.length) {
        return;
    }

    element.setAttribute(flow.config.lineMark, lineList.join(flow.config.lineMarkSeparator));
};

// ////////////////////////////////////////////////////////////////////////

// The shapes a group is drawn out of, told which table they are of, said as the line that
// table's name is on. A group of a name that is no table of the file stands for nothing in
// it, so it is told nothing.
flow.markTable = function(elementList, tableLine) {

    if(tableLine === tables.parse.config.noSectionLine) {
        return;
    }

    for(var elementIdx = 0; elementIdx < elementList.length; elementIdx++) {
        elementList[elementIdx].setAttribute(flow.config.tableMark, tableLine);
    }
};

// ////////////////////////////////////////////////////////////////////////

// Every shape one code or the value is drawn out of, told what it stands for - the lines of
// the file it came off and the whole of what it says, which is what a press on it copies.
flow.markAll = function(elementList, lineList, text) {

    var config = flow.config;

    // A note stands for nothing in the file, so there is nothing to copy off it either
    if(!lineList.length) {
        return;
    }

    // The box is the first of the parts, the letters inside it following, and every part of the
    // shape names it, so that a press anywhere on the shape leads back to the box
    var boxIdx = flow.state.boxList.length;
    flow.state.boxList.push(elementList[0]);

    for(var elementIdx = 0; elementIdx < elementList.length; elementIdx++) {

        var element = elementList[elementIdx];

        flow.mark(element, lineList);
        element.setAttribute(config.textMark, text);
        element.setAttribute(config.boxMark, boxIdx);
    }
};

// ////////////////////////////////////////////////////////////////////////

flow.addLine = function(svg, x1, y1, x2, y2) {

    var out = $.fn.zato.dashboard_kit.draw.addLine(svg, x1, y1, x2, y2, flow.config.lineClass);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The head the drop arrives with.
flow.addArrow = function(svg, x, y) {

    var config = flow.config;

    var out = $.fn.zato.dashboard_kit.draw.addArrow(svg, x, y, config.arrowLength, config.arrowWidth,
        config.arrowClass);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.wrap = function(text, room, charWidth) {

    var out = $.fn.zato.dashboard_kit.draw.wrap(text, room, charWidth);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.getLongest = function(textLineList) {

    var out = $.fn.zato.dashboard_kit.draw.getLongest(textLineList);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
