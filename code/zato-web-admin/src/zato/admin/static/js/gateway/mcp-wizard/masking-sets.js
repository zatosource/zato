// MCP gateway wizard - the industry sets of data masking.
//
// The sets are defined in one configuration file each on the server, which
// the page embeds. Field names are compared without regard to case. The Data
// masking popover reads the sets through the functions below and never
// through the lists directly.

(function($) {

// ////////////////////////////////////////////////////////////////////////

var wizard = $.fn.zato.gateway.mcp.wizard;
var maskingSets = wizard.maskingSets;

// ////////////////////////////////////////////////////////////////////////

maskingSets.config = {

    // Where the page embeds the industry sets, each with its name, label and fields, in the order shown
    dataScriptId: 'mcp-wizard-masking-sets',

    // Filled in by init out of the embedded sets
    sets: []
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.init = function() {

    var dataScript = document.getElementById(maskingSets.config.dataScriptId);
    maskingSets.config.sets = JSON.parse(dataScript.textContent);
};

// ////////////////////////////////////////////////////////////////////////

// Every set, in the order the popover shows them.
maskingSets.all = function() {

    var out = maskingSets.config.sets;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.get = function(setName) {

    var sets = maskingSets.config.sets;

    for(var setIdx = 0; setIdx < sets.length; setIdx++) {
        if(sets[setIdx].name === setName) {
            var out = sets[setIdx];
            return out;
        }
    }
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.allFieldsOf = function(setName) {

    var out = maskingSets.get(setName).fields;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// Whether the list holds the name, in any case.
maskingSets.holds = function(fieldList, name) {

    var nameLower = name.toLowerCase();

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(fieldList[fieldIdx].toLowerCase() === nameLower) {
            return true;
        }
    }

    return false;
};

// ////////////////////////////////////////////////////////////////////////

// The list with every name it does not hold yet appended at its end.
maskingSets.merge = function(fieldList, names) {

    var out = fieldList.slice();

    for(var nameIdx = 0; nameIdx < names.length; nameIdx++) {
        if(!maskingSets.holds(out, names[nameIdx])) {
            out.push(names[nameIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

maskingSets.subtract = function(fieldList, names) {

    var out = [];

    for(var fieldIdx = 0; fieldIdx < fieldList.length; fieldIdx++) {
        if(!maskingSets.holds(names, fieldList[fieldIdx])) {
            out.push(fieldList[fieldIdx]);
        }
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// The fields of several sets, each field once.
maskingSets.union = function(setNames) {

    var out = [];

    for(var setIdx = 0; setIdx < setNames.length; setIdx++) {
        out = maskingSets.merge(out, maskingSets.allFieldsOf(setNames[setIdx]));
    }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
