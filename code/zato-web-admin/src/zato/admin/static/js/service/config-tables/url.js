// Config tables - where the reader is, kept in the address of the page.
//
// The file being read, what is being translated and how far each column is scrolled all go
// into the fragment of the address, so the page is the same page after a reload, however
// hard that reload is, and the address itself is worth sending to somebody else. The
// fragment is used rather than the query, since none of it is the server's business - the
// page is asked for the same way whatever the reader is looking at.
//
// A name out of an address is not trusted with anything. The file named in a fragment is
// only ever looked up among the files the server itself reported, and nothing is built into
// a path here, so a fragment cannot reach a file outside the directory the server reads
// its config files from.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var tables = $.fn.zato.service.config_tables;
var url = tables.url;

// ////////////////////////////////////////////////////////////////////////

url.config = {

    // What the fragment says - the file, the three fields of the Translate column, whether the
    // answer was asked for, and how far down each box that scrolls is
    fileKey: 'file',
    sourceKey: 'source',
    codeKey: 'code',
    targetKey: 'target',
    answeredKey: 'answered',
    listScrollKey: 'list-at',
    fileScrollKey: 'file-at',
    translateScrollKey: 'translate-at',
    flowScrollKey: 'flow-at',

    // What says that the answer was asked for, since a fragment carries words rather than
    // anything else
    answeredValue: '1',

    // The address is rewritten this long after the last thing that changed it, so a column
    // being scrolled is one rewrite rather than one per line
    writeMs: 200,

    // How the fragment is put together
    pairSeparator: '&',
    valueSeparator: '='
};

// ////////////////////////////////////////////////////////////////////////

url.state = {

    // The fragment as it stands, every value of it a string
    current: {},

    // The rewrite waiting to happen, 0 while there is none
    timer: 0
};

// ////////////////////////////////////////////////////////////////////////

url.init = function() {

    url.state.current = url.read();

    // Everything the reader does to a field is worth keeping, whether or not the answer is
    // then asked for
    url.wireField('translate-source', url.config.sourceKey);
    url.wireField('translate-value', url.config.codeKey);
    url.wireField('translate-target', url.config.targetKey);

    // Every box on the page that scrolls inside itself, since where a column is scrolled to
    // is as much a part of where the reader is as which file is open
    url.wireScroll('browser', url.config.listScrollKey);
    url.wireScroll('content', url.config.fileScrollKey);
    url.wireScroll('translate-panel', url.config.translateScrollKey);
    url.wireScroll('flow', url.config.flowScrollKey);
};

// ////////////////////////////////////////////////////////////////////////

url.wireField = function(name, key) {

    var element = tables.get(name);

    element.addEventListener('input', function() {
        url.write(key, element.value.trim());
    });
};

// ////////////////////////////////////////////////////////////////////////

url.wireScroll = function(name, key) {

    var element = tables.get(name);

    element.addEventListener('scroll', function() {
        url.write(key, String(Math.round(element.scrollTop)));
    });
};

// ////////////////////////////////////////////////////////////////////////

// The fragment as it was arrived with. Anything in it that the page does not know about is
// left out, since the page only ever writes back what it reads.
url.read = function() {

    var config = url.config;
    var text = window.location.hash.slice(1);
    var out = {};

    if(!text) {
        return out;
    }

    var pairList = text.split(config.pairSeparator);

    for(var pairIdx = 0; pairIdx < pairList.length; pairIdx++) {

        var pair = pairList[pairIdx];
        var separatorIdx = pair.indexOf(config.valueSeparator);

        if(separatorIdx === -1) {
            continue;
        }

        var key = decodeURIComponent(pair.slice(0, separatorIdx));
        var value = decodeURIComponent(pair.slice(separatorIdx + 1));

        out[key] = value;
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One thing about where the reader is. An empty value is dropped rather than written as an
// empty one, so the address says no more than it has to.
url.write = function(key, value) {

    if(value) {
        url.state.current[key] = value;
    }
    else {
        delete url.state.current[key];
    }

    url.schedule();
};

// ////////////////////////////////////////////////////////////////////////

// The file that is open, which is also the end of whatever was being translated in the one
// before it - another file has its own values, its own answer and its own place to be
// scrolled to.
url.writeFile = function(name) {

    var config = url.config;
    var current = url.state.current;

    // Opening the very file the address already names is the page arriving at it rather than
    // the reader moving on, so what the address remembers about it is left alone - it is
    // what is about to be put back on screen
    if(current[config.fileKey] === name) {
        return;
    }

    current[config.fileKey] = name;

    delete current[config.sourceKey];
    delete current[config.codeKey];
    delete current[config.targetKey];
    delete current[config.answeredKey];
    delete current[config.fileScrollKey];
    delete current[config.flowScrollKey];

    url.schedule();
};

// ////////////////////////////////////////////////////////////////////////

// What was translated, so the same thing is translated again on the way back. The fields are
// read off the page rather than taken as already written, since one of them may have been
// filled in from what it offers rather than typed into.
url.writeAnswered = function() {

    var config = url.config;

    url.write(config.sourceKey, tables.get('translate-source').value.trim());
    url.write(config.codeKey, tables.get('translate-value').value.trim());
    url.write(config.targetKey, tables.get('translate-target').value.trim());
    url.write(config.answeredKey, config.answeredValue);
};

// ////////////////////////////////////////////////////////////////////////

// The address is rewritten once things have settled, and in place rather than as another
// page, so the back button still goes back to wherever the reader came from.
url.schedule = function() {

    if(url.state.timer) {
        window.clearTimeout(url.state.timer);
    }

    url.state.timer = window.setTimeout(url.flush, url.config.writeMs);
};

// ////////////////////////////////////////////////////////////////////////

url.flush = function() {

    var config = url.config;
    var current = url.state.current;
    var pairList = [];

    url.state.timer = 0;

    for(var key in current) {
        pairList.push(encodeURIComponent(key) + config.valueSeparator + encodeURIComponent(current[key]));
    }

    var fragment = pairList.join(config.pairSeparator);
    var out = window.location.pathname + window.location.search;

    if(fragment) {
        out = out + '#' + fragment;
    }

    window.history.replaceState(null, '', out);
};

// ////////////////////////////////////////////////////////////////////////

// The file the fragment names, and '' when it names none or names one this server knows
// nothing about - a file is picked out of what the server reported and never built out of
// what an address says.
url.readFileName = function() {

    var name = url.state.current[url.config.fileKey];

    if(!name) {
        return '';
    }

    var table = tables.getByName(name);

    if(table === null) {
        return '';
    }

    return table.name;
};

// ////////////////////////////////////////////////////////////////////////

// The Translate column as it was left. The file itself decides what the fields start at, so
// only what the fragment actually says is put back over that.
url.applyTranslate = function() {

    var config = url.config;
    var current = url.state.current;

    url.applyField('translate-source', current[config.sourceKey]);
    url.applyField('translate-value', current[config.codeKey]);
    url.applyField('translate-target', current[config.targetKey]);

    // The answer is worked out again rather than kept in the address, so what is on screen
    // is what the file on screen says right now
    if(current[config.answeredKey] === config.answeredValue) {
        tables.invoker.translate();
    }
};

// ////////////////////////////////////////////////////////////////////////

url.applyField = function(name, value) {

    if(value === undefined) {
        return;
    }

    tables.get(name).value = value;
};

// ////////////////////////////////////////////////////////////////////////

// How far each column was scrolled, put back once everything that scrolls is on screen and
// as tall as it is going to be.
url.applyScroll = function() {

    var config = url.config;

    window.requestAnimationFrame(function() {
        url.applyScrollOne('browser', config.listScrollKey);
        url.applyScrollOne('content', config.fileScrollKey);
        url.applyScrollOne('translate-panel', config.translateScrollKey);
        url.applyScrollOne('flow', config.flowScrollKey);
    });
};

// ////////////////////////////////////////////////////////////////////////

url.applyScrollOne = function(name, key) {

    var value = url.state.current[key];

    if(value === undefined) {
        return;
    }

    var top = parseInt(value, 10);

    if(isNaN(top)) {
        return;
    }

    tables.get(name).scrollTop = top;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
