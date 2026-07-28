// Config tables - the Try it column.
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

    // The answer reads as lines of the kind of file it came out of. The value the file
    // holds is what it is and nothing more, so that is what its line is called, while
    // a target's lines are named by the target itself.
    valueKey: 'value',
    keySeparator: ' = ',
    commentPrefix: '# '
};

// ////////////////////////////////////////////////////////////////////////

invoker.init = function() {

    tables.get('translate').addEventListener('click', invoker.translate);

    // The answer reads as lines of the kind of file it came out of, so it is colored
    // the way that file is
    $.fn.zato.highlight.attach(tables.get('result'), $.fn.zato.highlight.ini_to_html);

    invoker.wireCopy('result-copy', 'result', invoker.config.resultCopyPlacement);
    invoker.wireCopy('try-from-copy', 'try-from', invoker.config.fieldCopyPlacement);
    invoker.wireCopy('try-code-copy', 'try-code', invoker.config.fieldCopyPlacement);
    invoker.wireCopy('try-target-copy', 'try-target', invoker.config.fieldCopyPlacement);

    tables.combo.init();
};

// ////////////////////////////////////////////////////////////////////////

// One copy button and what it takes a copy of.
invoker.wireCopy = function(buttonName, sourceName, placement) {

    var button = tables.get(buttonName);

    button.addEventListener('click', function() {
        $.fn.zato.copy.to_clipboard(button, tables.get(sourceName).value, placement);
    });
};

// ////////////////////////////////////////////////////////////////////////

// The column as the file it belongs to has it - a code list has neither a source nor
// a target, so those fields are not there for one, and the fields start on the first
// value the file holds. A target is asked for rather than assumed, so it starts empty.
invoker.render = function(table) {

    var first = parse.getFirstEntry(table.content);

    tables.get('try-from').value = first.sectionName;
    tables.get('try-code').value = first.key;
    tables.get('try-target').value = '';

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

    tables.get('try-from-field').hidden = !isMappingSet;
    tables.get('try-target-field').hidden = !isMappingSet;
};

// ////////////////////////////////////////////////////////////////////////

invoker.readFrom = function(table) {

    var out = '';

    if(tables.isMappingSet(table)) {
        out = tables.get('try-from').value.trim();
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
    var code = tables.get('try-code').value.trim();
    var found = parse.lookup(table, content, fromName, code);

    if(found === null) {
        var missingText = tables.buildMissingText(table, fromName, code);
        invoker.setResult(invoker.buildComment(missingText));
        tables.flow.clear();
        return;
    }

    var answer = invoker.buildAnswer(table, content, found);
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
    var targetName = tables.get('try-target').value.trim();

    var out = {
        sourceTable: fromName,
        code: code,
        value: found,
        sourceKeyList: invoker.readSpreadKeys(spread, fromName),
        targetTable: targetName,
        targetKeyList: [],
        targetNote: '',
        otherList: []
    };

    if(!targetName) {
        out.otherList = invoker.dropTable(spread, fromName);
        return out;
    }

    var keyList = parse.findTargetKeys(content, targetName, found);

    // A name that is no table of the file and a table with no code for the value are the
    // same thing to look at - there is no mapping to draw either way
    if(keyList === null) {
        out.targetNote = tables.config.flowNoMapMessage;
        return out;
    }

    if(!keyList.length) {
        out.targetNote = tables.config.flowNoMapMessage;
        return out;
    }

    out.targetKeyList = keyList;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The codes one table holds the value under, read off what the whole file holds it under.
// A table that holds it under none of them is not in there at all.
invoker.readSpreadKeys = function(spread, tableName) {

    var out = [];

    for(var spreadIdx = 0; spreadIdx < spread.length; spreadIdx++) {

        var entry = spread[spreadIdx];

        if(entry.name === tableName) {
            out = entry.keyList;
            break;
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The file's other tables - the one the value came from is where the drawing starts, so
// it is not also one of the places it reaches.
invoker.dropTable = function(spread, tableName) {

    var out = [];

    for(var spreadIdx = 0; spreadIdx < spread.length; spreadIdx++) {

        var entry = spread[spreadIdx];

        if(entry.name !== tableName) {
            out.push(entry);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The value that was found, and under it what the target maps it to when one was
// asked for.
invoker.buildAnswer = function(table, content, found) {

    var config = invoker.config;
    var lineList = [config.valueKey + config.keySeparator + found];

    // A code list has no system on either end, so there is no target to ask about
    if(!tables.isMappingSet(table)) {
        return lineList[0];
    }

    var targetName = tables.get('try-target').value.trim();

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
    var keyList = parse.findTargetKeys(content, targetName, found);

    if(keyList === null) {
        var unknownText = tables.buildUnknownTargetText(targetName);
        return [invoker.buildComment(unknownText)];
    }

    if(!keyList.length) {
        var missingText = tables.buildTargetMissingText(targetName, found);
        return [invoker.buildComment(missingText)];
    }

    var out = [];

    for(var keyIdx = 0; keyIdx < keyList.length; keyIdx++) {
        out.push(targetName + config.keySeparator + keyList[keyIdx]);
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

    // Nothing typed it, so the colors are repainted by hand
    $.fn.zato.highlight.refresh(result);
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
