define("ace/theme/zato-dark",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

exports.isDark = true;
exports.cssClass = "ace-zato-dark";
exports.cssText = ".ace-zato-dark .ace_gutter {\
background: #1a1a1a;\
color: #858585;\
border-right: 1px solid rgba(255, 255, 255, 0.06);\
min-width: 40px;\
}\
.ace-zato-dark .ace_gutter-active-line {\
background-color: transparent;\
color: #c6c6c6;\
}\
.ace-zato-dark .ace_print-margin {\
width: 1px;\
background: #333;\
}\
.ace-zato-dark {\
background-color: #1e1e1e;\
color: #d4d4d4;\
}\
.ace-zato-dark .ace_cursor {\
color: #aeafad;\
}\
.ace-zato-dark .ace_invisible {\
color: #404040;\
}\
.ace-zato-dark .ace_indent_dot {\
color: #404040;\
}\
.ace-zato-dark .ace_marker-layer .ace_selection {\
background: rgba(74, 158, 255, 0.3);\
}\
.ace-zato-dark .ace_marker-layer .ace_active-line {\
background: rgba(255, 255, 255, 0.04);\
}\
.ace-zato-dark .ace_marker-layer .ace_selected-word {\
background: rgba(74, 158, 255, 0.2);\
border: 1px solid rgba(74, 158, 255, 0.4);\
}\
.ace-zato-dark .ace_marker-layer .ace_bracket {\
margin: -1px 0 0 -1px;\
border: 1px solid #404040;\
}\
.ace-zato-dark .ace_fold {\
background-color: #2d2d2d;\
border: 1px solid #569cd6;\
color: #569cd6;\
}\
.ace-zato-dark .ace_keyword {\
color: #7cb3e8;\
}\
.ace-zato-dark .ace_keyword.ace_operator {\
color: #d4d4d4;\
}\
.ace-zato-dark .ace_constant.ace_language {\
color: #569cd6;\
}\
.ace-zato-dark .ace_constant.ace_numeric {\
color: #b5cea8;\
}\
.ace-zato-dark .ace_constant.ace_character {\
color: #ce9178;\
}\
.ace-zato-dark .ace_constant.ace_other {\
color: #9cdcfe;\
}\
.ace-zato-dark .ace_support.ace_function {\
color: #dcdcaa;\
}\
.ace-zato-dark .ace_support.ace_constant {\
color: #4ec9b0;\
}\
.ace-zato-dark .ace_support.ace_class {\
color: #4ec9b0;\
}\
.ace-zato-dark .ace_support.ace_type {\
color: #4ec9b0;\
}\
.ace-zato-dark .ace_storage {\
color: #569cd6;\
}\
.ace-zato-dark .ace_storage.ace_type {\
color: #569cd6;\
}\
.ace-zato-dark .ace_invalid {\
color: #f44747;\
background-color: rgba(244, 71, 71, 0.15);\
}\
.ace-zato-dark .ace_invalid.ace_deprecated {\
color: #d4d4d4;\
background-color: #569cd6;\
}\
.ace-zato-dark .ace_string {\
color: #ce9178;\
}\
.ace-zato-dark .ace_string.ace_regexp {\
color: #d16969;\
}\
.ace-zato-dark .ace_comment {\
color: #6a9955;\
}\
.ace-zato-dark .ace_comment.ace_doc {\
color: #6a9955;\
}\
.ace-zato-dark .ace_comment.ace_doc.ace_tag {\
color: #569cd6;\
}\
.ace-zato-dark .ace_variable {\
color: #9cdcfe;\
}\
.ace-zato-dark .ace_variable.ace_language {\
color: #7cb3e8;\
}\
.ace-zato-dark .ace_variable.ace_parameter {\
color: #9cdcfe;\
}\
.ace-zato-dark .ace_entity.ace_name.ace_function {\
color: #dcdcaa;\
}\
.ace-zato-dark .ace_entity.ace_name.ace_tag {\
color: #569cd6;\
}\
.ace-zato-dark .ace_entity.ace_other.ace_attribute-name {\
color: #9cdcfe;\
}\
.ace-zato-dark .ace_meta.ace_tag {\
color: #569cd6;\
}\
.ace-zato-dark .ace_heading {\
color: #569cd6;\
}\
.ace-zato-dark .ace_xml-pe {\
color: #569cd6;\
}\
.ace-zato-dark .ace_indent-guide {\
background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAEklEQVQImWNgYGBgYHB3d/8PAAOIAdULw8qMAAAAAElFTkSuQmCC) right repeat-y;\
}";

var dom = require("../lib/dom");
dom.importCssString(exports.cssText, exports.cssClass, false);
});                (function() {
                    window.require(["ace/theme/zato-dark"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
