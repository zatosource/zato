// Config tables - the Try it column.
//
// It runs against the file on screen rather than the one on the server, which is
// what makes the answer the one a service reading the same file would get, and
// what lets a change be tried before it is saved. What the two fields offer is the
// file as it is on disk, which is combo.js. The answer is text like the file's own,
// so it is colored the same way, edited the same way and copied the same way.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var invoker = tables.invoker;
var parse = tables.parse;

var singleQuote = "'";

// ////////////////////////////////////////////////////////////////////////

invoker.config = {

    // Where each copy button says that it copied - beside the one under the answer,
    // above the ones the fields hold
    resultCopyPlacement: 'left',
    fieldCopyPlacement: 'top'
};

// ////////////////////////////////////////////////////////////////////////

invoker.init = function() {

    tables.get('try-run').addEventListener('click', invoker.run);

    // The answer is a value like the ones in the file, so it is colored like one
    $.fn.zato.highlight.attach(tables.get('result'), $.fn.zato.highlight.ini_values_to_html);

    invoker.wireCopy('result-copy', 'result', invoker.config.resultCopyPlacement);
    invoker.wireCopy('try-from-copy', 'try-from', invoker.config.fieldCopyPlacement);
    invoker.wireCopy('try-code-copy', 'try-code', invoker.config.fieldCopyPlacement);

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

// The column as the file it belongs to has it - a code list has no source, so that
// field is not there for one, and the fields start on the first value the file
// holds.
invoker.render = function(table) {

    var first = parse.getFirstEntry(table.content);

    tables.get('try-from').value = first.sectionName;
    tables.get('try-code').value = first.key;

    invoker.setResult('');
    invoker.refresh(table);
};

// ////////////////////////////////////////////////////////////////////////

// The column after the file itself has changed - a code list has no source to
// give, so the field for one follows the file, while what was typed into the
// fields stays as it is.
invoker.refresh = function(table) {

    var isMappingSet = tables.isMappingSet(table);
    tables.get('try-from-field').hidden = !isMappingSet;
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

// What the call answers - the value found, or the plain fact that there is none,
// which is put down as a note about the value rather than as one.
invoker.run = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var fromName = invoker.readFrom(table);
    var code = tables.get('try-code').value.trim();
    var found = parse.lookup(table, content, fromName, code);

    if(found === null) {
        invoker.setResult('# ' + tables.buildMissingText(table, fromName, code));
        return;
    }

    invoker.setResult(singleQuote + found + singleQuote);
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
