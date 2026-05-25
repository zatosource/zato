define("ace/mode/hl7_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var HL7HighlightRules = function() {

    this.$rules = {
        "start" : [ {
            token : "keyword",
            regex : /^[A-Z][A-Z0-9]{1,2}(?=\|)/,
            next  : "fields"
        }, {
            defaultToken : "text"
        } ],
        "fields" : [ {
            token : "variable",
            regex : /\|/
        }, {
            token : "punctuation",
            regex : /[\^~&]/
        }, {
            token : "constant.language.escape",
            regex : /\\[^\\]*\\/
        }, {
            token : "text",
            regex : /[A-Za-z][A-Za-z0-9.]*/
        }, {
            token : "constant.numeric",
            regex : /\d+(?:\.\d+)?/
        }, {
            token : "text",
            regex : /$/,
            next  : "start"
        }, {
            defaultToken : "text"
        } ]
    };
    this.normalizeRules();
};

oop.inherits(HL7HighlightRules, TextHighlightRules);

exports.HL7HighlightRules = HL7HighlightRules;
});

define("ace/mode/hl7",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/hl7_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var HL7HighlightRules = require("./hl7_highlight_rules").HL7HighlightRules;

var Mode = function() {
    this.HighlightRules = HL7HighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/hl7";
}).call(Mode.prototype);

exports.Mode = Mode;
});                (function() {
                    window.require(["ace/mode/hl7"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
