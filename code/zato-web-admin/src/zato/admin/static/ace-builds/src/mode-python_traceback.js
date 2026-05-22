define("ace/mode/python_traceback_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var PythonTracebackHighlightRules = function() {

    var excSuffix = "Error|Exception|Warning|Fault|Exit|Interrupt|Stop|KeyboardInterrupt";
    var excName = "[a-zA-Z_][\\w.]*(?:" + excSuffix + ")";

    this.$rules = {
        "start": [

            {
                token: "keyword",
                regex: "^\\u00b7\\u00b7\\u00b7 .+ \\u00b7\\u00b7\\u00b7$"
            },

            {
                token: ["support.function", "support.function", "string", "support.function", "constant.numeric", "support.function", "entity.name.function"],
                regex: "^(>>> )(File \")([^\"]+)(\", line )(\\d+)(, in )(.+)$"
            },
            {
                token: ["support.function", "support.function", "string", "support.function", "constant.numeric"],
                regex: "^(>>> )(File \")([^\"]+)(\", line )(\\d+)$"
            },
            {
                token: ["support.function", "invalid", "text", "string"],
                regex: "^(>>> )(" + excName + ")(: )(.+)$"
            },
            {
                token: ["support.function", "invalid"],
                regex: "^(>>> )(" + excName + "):?$"
            },
            {
                token: ["support.function", "string.unquoted"],
                regex: "^(>>>   )(.+)$"
            },

            {
                token: "keyword",
                regex: "^(?:\\^C)?Traceback \\(most recent call last\\):$"
            },
            {
                token: "keyword",
                regex: "^During handling of the above exception, another exception occurred:$"
            },
            {
                token: "keyword",
                regex: "^The above exception was the direct cause of the following exception:$"
            },

            {
                token: ["support.function", "string", "support.function", "constant.numeric", "support.function", "entity.name.function"],
                regex: "^(  File \")([^\"]+)(\", line )(\\d+)(, in )(.+)$"
            },
            {
                token: ["support.function", "string", "support.function", "constant.numeric"],
                regex: "^(  File \")([^\"]+)(\", line )(\\d+)$"
            },

            {
                token: ["invalid", "text", "string"],
                regex: "^(" + excName + ")(: )(.+)$"
            },
            {
                token: "invalid",
                regex: "^" + excName + ":?$"
            },

            {
                token: "keyword.operator",
                regex: "^\\s+[~^]+$"
            },
            {
                token: "string.unquoted",
                regex: "^    .+$"
            },

            {
                token: "comment",
                regex: "^\\s*\\.\\.\\.$"
            },

            {
                token: "string",
                regex: "^\\d{8}-\\d{6}-\\d{4}-[0-9a-f]+$"
            },
            {
                token: "string",
                regex: "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d+[+-]\\d{2}:\\d{2} \\(.+\\)$"
            },
            {
                token: "string",
                regex: "^Zato \\d+\\.\\d+\\.\\d+\\.\\d+\\..+$"
            },
            {
                token: "text",
                regex: ".+"
            }
        ]
    };

    this.normalizeRules();
};

oop.inherits(PythonTracebackHighlightRules, TextHighlightRules);

exports.PythonTracebackHighlightRules = PythonTracebackHighlightRules;
});

define("ace/mode/python_traceback",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/python_traceback_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var PythonTracebackHighlightRules = require("./python_traceback_highlight_rules").PythonTracebackHighlightRules;

var Mode = function() {
    this.HighlightRules = PythonTracebackHighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/python_traceback";
}).call(Mode.prototype);

exports.Mode = Mode;
});                (function() {
                    window.require(["ace/mode/python_traceback"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
