// Config tables - the answer for a mapping set, drawn rather than written.
//
// A mapping set holds a table per party, so its answer reads as a story down the middle of
// the column: the table the value came in from, what that table maps it to, and what the
// table on the other side sends it as. The codes of one table stand together inside a
// dashed group of its own, so a value that several codes of the same table map to is seen
// as exactly that, and every table the value reaches is drawn rather than counted.
//
// The drawing is laid out in units of its own and only ever scaled down to the column it
// sits in, so what is below reads as a plan of it rather than as pixels on a screen.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var flow = tables.flow;

var svgNamespace = 'http://www.w3.org/2000/svg';

// ////////////////////////////////////////////////////////////////////////

flow.config = {

    // How wide the drawing is, how much of that is kept clear around it, and the line
    // everything stands on
    width: 240,
    padding: 10,
    center: 120,

    // A group of codes - the box they stand in, the room it keeps inside itself, and
    // where the name of the table goes
    groupX: 8,
    groupWidth: 224,
    groupInset: 10,
    captionHeight: 22,
    captionBaseline: 15,

    // How far apart two groups stand when the value reaches more than one table
    groupGap: 8,

    // One code of a table
    chipHeight: 20,
    chipGap: 6,
    chipInset: 9,
    chipBaseline: 14,
    rowGap: 6,

    // The value the whole drawing turns on
    valueHeight: 24,
    valueInset: 11,
    valueBaseline: 17,

    // The drop from one part of the story to the next, and where the words that go with
    // that drop stand
    connectorLength: 26,
    labelOffset: 8,
    labelBaseline: 4,
    arrowLength: 6,
    arrowWidth: 4,

    // How wide one character of each face is, which is what says how much of a long name
    // fits into a chip
    charWidth: 6.7,
    valueCharWidth: 7.3,
    ellipsis: '\u2026',

    // The corners are kept as tight as the ones the badges in the listing wear
    corner: 2,

    // The classes the parts of the drawing wear, so what they look like stays in the
    // stylesheet
    groupClass: 'config-tables-flow-group',
    captionClass: 'config-tables-flow-caption',
    chipClass: 'config-tables-flow-chip',
    chipMarkedClass: 'config-tables-flow-chip config-tables-flow-chip-marked',
    chipNoteClass: 'config-tables-flow-chip-note',
    chipTextClass: 'config-tables-flow-chip-text',
    noteTextClass: 'config-tables-flow-note-text',
    valueClass: 'config-tables-flow-value',
    valueTextClass: 'config-tables-flow-value-text',
    labelClass: 'config-tables-flow-label',
    lineClass: 'config-tables-flow-line',
    arrowClass: 'config-tables-flow-arrow',
    drawnClass: 'config-tables-result-drawn'
};

// ////////////////////////////////////////////////////////////////////////

// The whole story, from the top down. Nothing goes on screen until the last part of it
// is laid out, since that is what says how tall the drawing turned out to be.
flow.render = function(model) {

    var config = flow.config;
    var words = tables.config;
    var svg = flow.createElement('svg');
    var cursor = {y: config.padding, svg: svg};

    // The table the value came in from, with every code of it that maps to the same
    // value and the one that was asked about marked out among them ..
    flow.addGroup(cursor, {
        caption: tables.buildGroupCaption(model.sourceTable, model.sourceKeyList.length),
        chipList: model.sourceKeyList,
        marked: model.code,
        note: ''
    });

    // .. what the file maps it to ..
    flow.addConnector(cursor, words.flowMapsToLabel);
    flow.addValue(cursor, model.value);

    // .. and where it goes from there.
    flow.addTargetGroups(cursor, model);

    var height = cursor.y + config.padding;

    svg.setAttribute('viewBox', '0 0 ' + config.width + ' ' + height);
    svg.setAttribute('width', config.width);
    svg.setAttribute('height', height);

    var host = tables.get('flow');

    host.textContent = '';
    host.appendChild(svg);

    tables.get('result-area').classList.add(config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// The answer as text again, which is what a code list gets and what anything the file
// has nothing for gets.
flow.clear = function() {

    tables.get('flow').textContent = '';
    tables.get('result-area').classList.remove(flow.config.drawnClass);
};

// ////////////////////////////////////////////////////////////////////////

// Where the value goes - the table that was asked about, and otherwise every other table
// of the file that maps to the same value.
flow.addTargetGroups = function(cursor, model) {

    var words = tables.config;

    if(model.targetTable) {

        flow.addConnector(cursor, words.flowSentAsLabel);

        flow.addGroup(cursor, {
            caption: tables.buildGroupCaption(model.targetTable, model.targetKeyList.length),
            chipList: model.targetKeyList,
            marked: '',
            note: model.targetNote
        });

        return;
    }

    if(!model.otherList.length) {
        return;
    }

    flow.addConnector(cursor, words.flowAlsoInLabel);

    for(var otherIdx = 0; otherIdx < model.otherList.length; otherIdx++) {

        var other = model.otherList[otherIdx];

        // The drop leads into the first group, and the rest stand under it
        if(otherIdx) {
            cursor.y = cursor.y + flow.config.groupGap;
        }

        flow.addGroup(cursor, {
            caption: tables.buildGroupCaption(other.name, other.keyList.length),
            chipList: other.keyList,
            marked: '',
            note: ''
        });
    }
};

// ////////////////////////////////////////////////////////////////////////

// One table - its name over the codes it holds the value under, all of them inside a box
// of its own.
flow.addGroup = function(cursor, group) {

    var config = flow.config;
    var top = cursor.y;
    var rowList = flow.buildRows(group);
    var height = flow.getGroupHeight(rowList);

    flow.addRect(cursor.svg, config.groupX, top, config.groupWidth, height, config.groupClass);

    var captionRoom = config.groupWidth - config.groupInset * 2;
    var caption = flow.fit(group.caption, captionRoom, config.charWidth);

    flow.addText(cursor.svg, config.center, top + config.captionBaseline, caption, config.captionClass, 'middle');

    var rowTop = top + config.captionHeight;

    for(var rowIdx = 0; rowIdx < rowList.length; rowIdx++) {
        flow.addRow(cursor.svg, rowList[rowIdx], rowTop);
        rowTop = rowTop + config.chipHeight + config.rowGap;
    }

    cursor.y = top + height;
};

// ////////////////////////////////////////////////////////////////////////

flow.getGroupHeight = function(rowList) {

    var config = flow.config;
    var rowCount = rowList.length;
    var rows = rowCount * config.chipHeight + (rowCount - 1) * config.rowGap;

    var out = config.captionHeight + rows + config.groupInset;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The codes of one table, in as many rows as they take - a table of a dozen codes reads
// as a block of them rather than as a column running off the screen.
flow.buildRows = function(group) {

    var config = flow.config;
    var chipList = flow.buildChips(group);
    var room = config.groupWidth - config.groupInset * 2;

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
    // has room for
    if(group.note) {
        out.push(flow.buildChip(group.note, config.chipNoteClass, config.noteTextClass));
        return out;
    }

    for(var textIdx = 0; textIdx < group.chipList.length; textIdx++) {

        var text = group.chipList[textIdx];
        var className = config.chipClass;

        // The code that was asked about wears a line around it, so it is found again among
        // the ones that came along with it
        if(text === group.marked) {
            className = config.chipMarkedClass;
        }

        out.push(flow.buildChip(text, className, config.chipTextClass));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.buildChip = function(text, className, textClass) {

    var config = flow.config;
    var room = config.groupWidth - config.groupInset * 2 - config.chipInset * 2;

    text = flow.fit(text, room, config.charWidth);

    var out = {
        text: text,
        width: text.length * config.charWidth + config.chipInset * 2,
        className: className,
        textClass: textClass
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

    var left = config.center - total / 2;

    for(var chipIdx = 0; chipIdx < row.length; chipIdx++) {

        var chip = row[chipIdx];
        var middle = left + chip.width / 2;

        flow.addRect(svg, left, top, chip.width, config.chipHeight, chip.className);
        flow.addText(svg, middle, top + config.chipBaseline, chip.text, chip.textClass, 'middle');

        left = left + chip.width + config.chipGap;
    }
};

// ////////////////////////////////////////////////////////////////////////

// What the file holds for the code, which is the one thing in the drawing that stands on
// its own rather than inside a table.
flow.addValue = function(cursor, value) {

    var config = flow.config;
    var top = cursor.y;
    var room = config.groupWidth - config.valueInset * 2;
    var text = flow.fit(value, room, config.valueCharWidth);

    var width = text.length * config.valueCharWidth + config.valueInset * 2;
    var left = config.center - width / 2;

    flow.addRect(cursor.svg, left, top, width, config.valueHeight, config.valueClass);
    flow.addText(cursor.svg, config.center, top + config.valueBaseline, text, config.valueTextClass, 'middle');

    cursor.y = top + config.valueHeight;
};

// ////////////////////////////////////////////////////////////////////////

// The drop from one part of the story to the next, with the words that say what it is.
flow.addConnector = function(cursor, labelText) {

    var config = flow.config;
    var top = cursor.y;
    var bottom = top + config.connectorLength;
    var middle = top + config.connectorLength / 2 + config.labelBaseline;
    var labelX = config.center + config.labelOffset;

    flow.addLine(cursor.svg, config.center, top, config.center, bottom);
    flow.addArrow(cursor.svg, config.center, bottom);
    flow.addText(cursor.svg, labelX, middle, labelText, config.labelClass, 'start');

    cursor.y = bottom;
};

// ////////////////////////////////////////////////////////////////////////
// The shapes
// ////////////////////////////////////////////////////////////////////////

flow.createElement = function(name) {

    var out = document.createElementNS(svgNamespace, name);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

flow.addRect = function(svg, x, y, width, height, className) {

    var rect = flow.createElement('rect');

    rect.setAttribute('x', x);
    rect.setAttribute('y', y);
    rect.setAttribute('width', width);
    rect.setAttribute('height', height);
    rect.setAttribute('rx', flow.config.corner);
    rect.setAttribute('class', className);

    svg.appendChild(rect);
};

// ////////////////////////////////////////////////////////////////////////

flow.addText = function(svg, x, y, text, className, anchor) {

    var element = flow.createElement('text');

    element.setAttribute('x', x);
    element.setAttribute('y', y);
    element.setAttribute('text-anchor', anchor);
    element.setAttribute('class', className);
    element.textContent = text;

    svg.appendChild(element);
};

// ////////////////////////////////////////////////////////////////////////

flow.addLine = function(svg, x1, y1, x2, y2) {

    var line = flow.createElement('line');

    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('class', flow.config.lineClass);

    svg.appendChild(line);
};

// ////////////////////////////////////////////////////////////////////////

// The head the drop arrives with.
flow.addArrow = function(svg, x, y) {

    var config = flow.config;
    var top = y - config.arrowLength;
    var arrow = flow.createElement('polygon');

    var points = (x - config.arrowWidth) + ',' + top + ' ' +
        (x + config.arrowWidth) + ',' + top + ' ' + x + ',' + y;

    arrow.setAttribute('points', points);
    arrow.setAttribute('class', config.arrowClass);

    svg.appendChild(arrow);
};

// ////////////////////////////////////////////////////////////////////////

// A name too long for the room it goes into is cut where that room ends, since a drawing
// that grows with the longest name in a file is no drawing at all.
flow.fit = function(text, room, charWidth) {

    var maxLength = Math.floor(room / charWidth);

    if(text.length <= maxLength) {
        return text;
    }

    var out = text.slice(0, maxLength - 1) + flow.config.ellipsis;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
