// Config tables - the Try it column.
//
// It runs against the file on screen rather than the one on the server, which is
// what makes the answer the one a service reading the same file would get, and
// what lets a change be tried before it is saved. What the fields offer is the file
// as it is on disk, which is combo.js. The answer is text like the file's own, so it
// is colored the same way, edited the same way and copied the same way.
//
// A source names the system a value came from and a target the system it is going to.
// The value under the source is what the file maps it to, and the target sends that
// under a key of its own, which is the same file read the other way round. A target
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

    // The answer reads as lines of the kind of file it came out of, and these name
    // what each line holds - what a code list keeps under a code, and what a mapping
    // set maps one to. A target names its own lines itself.
    nameKey: 'name',
    canonicalKey: 'canonical',
    keySeparator: ' = ',
    commentPrefix: '# '
};

// ////////////////////////////////////////////////////////////////////////

invoker.init = function() {

    tables.get('try-run').addEventListener('click', invoker.run);

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

// What the call answers - the value found and what a target sends it as, or the plain
// fact that there is none, which is put down as a note about the value rather than as one.
invoker.run = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var fromName = invoker.readFrom(table);
    var code = tables.get('try-code').value.trim();
    var found = parse.lookup(table, content, fromName, code);

    if(found === null) {
        var missingText = tables.buildMissingText(table, fromName, code);
        invoker.setResult(invoker.buildComment(missingText));
        return;
    }

    var answer = invoker.buildAnswer(table, content, found);
    invoker.setResult(answer);
};

// ////////////////////////////////////////////////////////////////////////

// The value that was found, and under it what the target sends it as when one was
// asked for.
invoker.buildAnswer = function(table, content, found) {

    var config = invoker.config;

    // A code list has no system on either end - what it keeps under a code is a name
    if(!tables.isMappingSet(table)) {
        return config.nameKey + config.keySeparator + found;
    }

    var lineList = [config.canonicalKey + config.keySeparator + found];
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
