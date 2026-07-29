// Config tables - the Translate column.
//
// It runs against the file on screen rather than the one on the server, which is
// what makes the answer the one a service reading the same file would get, and
// what lets a change be tried before it is saved. What the fields offer is the file
// as it is on disk, which is combo.js. The answer is text like the file's own, so it
// is colored the same way, edited the same way and copied the same way.
//
// A source names the system a value came from and a target the system it is going to.
// The value under the source is what the file maps it to, and the target maps that
// on to a key of its own, which is the same file read the other way round. A target
// may keep the value under several keys, and then the answer is all of them - a
// service asking for one of them is told to keep one instead.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var invoker = tables.invoker;
var parse = tables.parse;

// ////////////////////////////////////////////////////////////////////////

invoker.config = {

    // Where each copy button says that it copied - beside the one under the answer,
    // above the ones the fields hold
    resultCopyPlacement: 'left',
    fieldCopyPlacement: 'top',

    // The answer reads as lines of the kind of file it came out of - the value under the
    // very code it was looked up by, and a target's lines under the target's own name
    keySeparator: ' = ',
    commentPrefix: '# '
};

// ////////////////////////////////////////////////////////////////////////

// Every copy button of the column and the field or the answer it takes its copy from, which
// is what says whether there is anything to take
invoker.copyList = [];

// ////////////////////////////////////////////////////////////////////////

invoker.state = {

    // The table the value below it belongs to, so that naming another one is seen for what it is
    sourceName: ''
};

// ////////////////////////////////////////////////////////////////////////

invoker.init = function() {

    tables.get('translate').addEventListener('click', invoker.translate);

    // The answer reads as lines of the kind of file it came out of, so it is colored
    // the way that file is
    $.fn.zato.highlight.attach(tables.get('result'), $.fn.zato.highlight.ini_to_html);

    invoker.wireCopy('result-copy', 'result', invoker.config.resultCopyPlacement);
    invoker.wireCopy('translate-source-copy', 'translate-source', invoker.config.fieldCopyPlacement);
    invoker.wireCopy('translate-value-copy', 'translate-value', invoker.config.fieldCopyPlacement);
    invoker.wireCopy('translate-target-copy', 'translate-target', invoker.config.fieldCopyPlacement);

    invoker.refreshCopy();

    // There is nothing to translate until the fields say what, so the button says as much.
    // A value picked out of what a field offers arrives with the menu closing rather than
    // with a keypress, which is why that is listened for too.
    $('#config-tables-translate-source, #config-tables-translate-value')
        .on('input autocompleteclose', invoker.refreshTranslate);

    // A value is a key of the table above it, so naming another table is a question of its own.
    // A name settled on is what counts, not every letter of one being typed, so this is read once
    // the field is left or once something has been picked out of what it offers.
    $('#config-tables-translate-source').on('change autocompleteclose', invoker.readSource);

    tables.combo.init();
};

// ////////////////////////////////////////////////////////////////////////

// The table the value is looked up in, once it has been named. The value goes with the table it
// belonged to, unless the table now named holds a key of that name as well, and a target that
// has become the source itself goes too - a value going back where it came from is no
// translation at all.
invoker.readSource = function() {

    var sourceName = tables.get('translate-source').value.trim();

    if(sourceName === invoker.state.sourceName) {
        return;
    }

    invoker.state.sourceName = sourceName;

    var value = tables.get('translate-value');
    var target = tables.get('translate-target');
    var isStillThere = tables.combo.getValueList().indexOf(value.value.trim()) !== -1;

    if(!isStillThere) {
        value.value = '';
    }

    if(target.value.trim() === sourceName) {
        target.value = '';
    }

    tables.log.say('invoker.readSource', {
        sourceName: sourceName,
        isStillThere: isStillThere,
        value: value.value,
        target: target.value
    });

    tables.url.writeFields();
    invoker.refreshCopy();
    invoker.refreshTranslate();
};

// ////////////////////////////////////////////////////////////////////////

// One copy button and what it takes a copy of. An empty field or an empty answer is nothing
// to copy, so the button beside it says as much for as long as it stays empty.
invoker.wireCopy = function(buttonName, sourceName, placement) {

    var button = tables.get(buttonName);
    var source = tables.get(sourceName);

    button.addEventListener('click', function() {
        $.fn.zato.copy.to_clipboard(button, source.value, placement, $.fn.zato.copy.config.offset);
    });

    // A value picked out of what a field offers arrives with the menu closing rather than with
    // a keypress, so that is listened for as well
    $(source).on('input autocompleteclose', invoker.refreshCopy);

    invoker.copyList.push({button: button, source: source});
};

// ////////////////////////////////////////////////////////////////////////

invoker.refreshCopy = function() {

    for(var copyIdx = 0; copyIdx < invoker.copyList.length; copyIdx++) {

        var copy = invoker.copyList[copyIdx];
        copy.button.disabled = !copy.source.value;
    }
};

// ////////////////////////////////////////////////////////////////////////

// The column as the file it belongs to has it - a code list has neither a source nor
// a target, so those fields are not there for one, and the fields start on the first
// value the file holds. A target is asked for rather than assumed, so it starts empty.
invoker.render = function(table) {

    var first = parse.getFirstEntry(table.content);

    tables.get('translate-source').value = first.sectionName;
    tables.get('translate-value').value = first.key;
    tables.get('translate-target').value = '';

    // The two go together, the value being a key of that very table
    invoker.state.sourceName = first.sectionName;

    invoker.setResult('');
    tables.flow.clear();
    invoker.refresh(table);
};

// ////////////////////////////////////////////////////////////////////////

// The column after the file itself has changed - a code list has no system on either
// end, so those two fields follow the file, while what was typed into the fields
// stays as it is.
invoker.refresh = function(table) {

    var isMappingSet = tables.isMappingSet(table);

    tables.get('translate-source-field').hidden = !isMappingSet;
    tables.get('translate-target-field').hidden = !isMappingSet;

    invoker.refreshTranslate();
};

// ////////////////////////////////////////////////////////////////////////

// Whether there is anything to translate - a value to look up, and the system it comes from
// when the file keeps one table per system. Without those two there is no question to ask,
// so the button is not there to be pressed.
invoker.refreshTranslate = function() {

    var table = tables.getCurrent();
    var button = tables.get('translate');

    // No file is open, which is a state of its own - the whole column is away then
    if(table === null) {
        button.disabled = true;
        return;
    }

    var hasCode = Boolean(tables.get('translate-value').value.trim());
    var isReady = hasCode;

    if(tables.isMappingSet(table)) {
        var hasFrom = Boolean(tables.get('translate-source').value.trim());
        isReady = hasCode && hasFrom;
    }

    button.disabled = !isReady;
};

// ////////////////////////////////////////////////////////////////////////

invoker.readFrom = function(table) {

    var out = '';

    if(tables.isMappingSet(table)) {
        out = tables.get('translate-source').value.trim();
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What the call answers - the value the code maps to and what the target maps it to, or
// the plain fact that there is none, which is put down as a note about the value rather
// than as one. A mapping set is a file of tables, so its answer is also drawn as one,
// while the text stays underneath it as what Copy takes.
invoker.translate = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var fromName = invoker.readFrom(table);
    var code = tables.get('translate-value').value.trim();
    var found = parse.lookup(table, content, fromName, code);

    // Asking is part of where the reader is, so the address says as much and the answer is
    // there again after a reload
    tables.url.writeAnswered();

    if(found === null) {
        var missingText = tables.buildMissingText(table, fromName, code);
        invoker.setResult(invoker.buildComment(missingText));
        tables.flow.clear();
        return;
    }

    var answer = invoker.buildAnswer(table, content, code, found);
    invoker.setResult(answer);

    if(!tables.isMappingSet(table)) {
        tables.flow.clear();
        return;
    }

    var model = invoker.buildModel(content, fromName, code, found);
    tables.flow.render(model);
};

// ////////////////////////////////////////////////////////////////////////

// What the drawing is of - the table the value came in from, what the file holds for it,
// and what is on the other side, which is the target when one was asked about and every
// other table of the file when none was.
invoker.buildModel = function(content, fromName, code, found) {

    var spread = parse.findValueSpread(content, found);
    var targetName = tables.get('translate-target').value.trim();

    var out = {
        sourceTable: fromName,
        sourceTableLine: parse.findSectionLine(content, fromName),
        code: code,
        value: found,
        valueLineList: invoker.readSpreadLines(spread),
        sourceEntryList: invoker.readSourceEntries(content, fromName, code),
        targetTable: targetName,
        targetTableLine: parse.findSectionLine(content, targetName),
        targetEntryList: [],
        targetNote: '',
        otherList: []
    };

    if(!targetName) {
        out.otherList = invoker.dropTable(spread, fromName);
        return out;
    }

    var entryList = parse.findTargetEntries(content, targetName, found);

    // A name that is no table of the file and a table with no code for the value are the
    // same thing to look at - there is no mapping to draw either way
    if(entryList === null) {
        out.targetNote = tables.config.flowNoMapMessage;
        return out;
    }

    if(!entryList.length) {
        out.targetNote = tables.config.flowNoMapMessage;
        return out;
    }

    out.targetEntryList = entryList;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The code the question was about, and nothing else - a table may well map another code of
// its own to the same value, and that is no part of the answer to what this one code means.
// The same code written twice in the one table is two lines, so both of them are there.
invoker.readSourceEntries = function(content, fromName, code) {

    var parsed = parse.read(content);
    var section = parse.findSection(parsed, fromName);

    var out = parse.findKeyEntries(section, code);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every line of the file that holds the value, whichever table it is under - what the value
// itself stands for, as against one code standing for the one line it came off.
invoker.readSpreadLines = function(spread) {

    var out = [];

    for(var spreadIdx = 0; spreadIdx < spread.length; spreadIdx++) {

        var entryList = spread[spreadIdx].entryList;

        for(var entryIdx = 0; entryIdx < entryList.length; entryIdx++) {
            out.push(entryList[entryIdx].lineIdx);
        }
    }

    out.sort(invoker.byLine);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Down the file, since that is the order they are washed over in.
invoker.byLine = function(left, right) {

    var out = left - right;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The file's other tables - the one the value came from is where the drawing starts, so
// it is not also one of the places it reaches.
invoker.dropTable = function(spread, tableName) {

    var out = [];

    for(var spreadIdx = 0; spreadIdx < spread.length; spreadIdx++) {

        var table = spread[spreadIdx];

        if(table.name !== tableName) {
            out.push(table);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The value that was found, under the code it was looked up by, and under that what the
// target maps it to when one was asked for.
invoker.buildAnswer = function(table, content, code, found) {

    var config = invoker.config;
    var lineList = [code + config.keySeparator + found];

    // A code list has no system on either end, so there is no target to ask about
    if(!tables.isMappingSet(table)) {
        return lineList[0];
    }

    var targetName = tables.get('translate-target').value.trim();

    if(targetName) {
        var targetLineList = invoker.buildTargetLineList(content, targetName, found);
        lineList = lineList.concat(targetLineList);
    }

    var out = lineList.join('\n');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Every key the target keeps the value under, one line each, which is how a value under
// several of them is answered. A target that keeps it under none, and a name that is no
// target at all, are each said as the note that they are.
invoker.buildTargetLineList = function(content, targetName, found) {

    var config = invoker.config;
    var entryList = parse.findTargetEntries(content, targetName, found);

    if(entryList === null) {
        var unknownText = tables.buildUnknownTargetText(targetName);
        return [invoker.buildComment(unknownText)];
    }

    if(!entryList.length) {
        var missingText = tables.buildTargetMissingText(targetName, found);
        return [invoker.buildComment(missingText)];
    }

    var out = [];

    for(var entryIdx = 0; entryIdx < entryList.length; entryIdx++) {
        out.push(targetName + config.keySeparator + entryList[entryIdx].key);
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

invoker.buildComment = function(text) {

    var out = invoker.config.commentPrefix + text;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

invoker.setResult = function(text) {

    var result = tables.get('result');
    result.value = text;

    // Nothing typed it, so the colors are repainted by hand and the button under it is told
    // whether there is now an answer to copy
    $.fn.zato.highlight.refresh(result);
    invoker.refreshCopy();
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
