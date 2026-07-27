// Config tables - the Try it strip.
//
// It runs against the file on screen rather than the one on the server, which is
// what makes the answer the one a service reading the same file would get, and
// what lets a change be tried before it is saved. The call is shown as a service
// writes it, so what is read here is the same thing that is written there.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var invoker = tables.invoker;
var parse = tables.parse;

var singleQuote = "'";

// ////////////////////////////////////////////////////////////////////////

invoker.config = {

    // The class the answer wears - one that was found, and one that was not
    resultFound: 'config-tables-result',
    resultMissing: 'config-tables-result config-tables-result-missing'
};

// ////////////////////////////////////////////////////////////////////////

invoker.init = function() {

    tables.get('try-from').addEventListener('input', invoker.refreshCall);
    tables.get('try-code').addEventListener('input', invoker.refreshCall);
    tables.get('try-run').addEventListener('click', invoker.run);
};

// ////////////////////////////////////////////////////////////////////////

// The strip as the file it belongs to has it - a code list has nothing to come
// from, so that field is not there for one, and the fields start on the first
// value the file holds.
invoker.render = function(table) {

    var first = parse.getFirstEntry(table.content);

    tables.get('try-from').value = first.sectionName;
    tables.get('try-code').value = first.key;
    tables.get('result').textContent = '';

    invoker.refresh(table);
};

// ////////////////////////////////////////////////////////////////////////

// The strip after the file itself has changed - what a code list has no field
// for and what the call reads follow the file, while what was typed into the
// fields stays as it is.
invoker.refresh = function(table) {

    var isMappingSet = tables.isMappingSet(table);

    tables.get('try-from-field').hidden = !isMappingSet;

    invoker.refreshCall();
};

// ////////////////////////////////////////////////////////////////////////

invoker.refreshCall = function() {

    var table = tables.getCurrent();
    var fromName = invoker.readFrom(table);
    var code = tables.get('try-code').value.trim();

    tables.get('call').textContent = tables.buildCallText(table, fromName, code);
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

// What the call answers - the value found, or the plain fact that there is none.
invoker.run = function() {

    var table = tables.getCurrent();
    var content = tables.get('content').value;
    var fromName = invoker.readFrom(table);
    var code = tables.get('try-code').value.trim();
    var found = parse.lookup(table, content, fromName, code);
    var result = tables.get('result');

    if(found === null) {
        result.className = invoker.config.resultMissing;
        result.textContent = tables.buildMissingText(table, fromName, code);
    }
    else {
        result.className = invoker.config.resultFound;
        result.textContent = singleQuote + found + singleQuote;
    }
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
