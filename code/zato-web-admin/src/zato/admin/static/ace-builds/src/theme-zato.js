define("ace/theme/zato",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

exports.isDark = false;
exports.cssClass = "ace-zato";
exports.cssText = ".ace-zato .ace_gutter {\
background: #ebebeb;\
color: #333;\
overflow : hidden;\
}\
.ace-zato .ace_print-margin {\
width: 1px;\
background: #e8e8e8;\
}\
.ace-zato {\
background-color: #FFFFFF;\
color: black;\
}\
.ace-zato .ace_cursor {\
color: black;\
}\
.ace-zato .ace_invisible {\
color: rgb(191, 191, 191);\
}\
.ace-zato .ace_constant.ace_buildin {\
color: #b21104;\
}\
.ace-zato .ace_constant.ace_language {\
color: #b21104;\
}\
.ace-zato .ace_constant.ace_library {\
color: rgb(6, 150, 14);\
}\
.ace-zato .ace_invalid {\
background-color: rgb(153, 0, 0);\
color: white;\
}\
.ace-zato .ace_fold {\
}\
.ace-zato .ace_support.ace_function {\
color: #000;\
}\
.ace-zato .ace_support.ace_constant {\
color: #f0f;\
}\
.ace-zato .ace_support.ace_type {\
color: red;\
}\
.ace-zato .ace_support.ace_class {\
color: green;\
}\
.ace-zato .ace_support.ace_other {\
color: yellow;\
}\
.ace-zato .ace_variable.ace_parameter {\
font-style:italic;\
color:#FD971F;\
}\
.ace-zato .ace_keyword.ace_operator {\
color: #000;\
}\
.ace-zato .ace_comment {\
color: #007f00;\
}\
.ace-zato .ace_comment.ace_doc {\
color: #007f00;\
}\
.ace-zato .ace_comment.ace_doc.ace_tag {\
color: #007f00;\
}\
.ace-zato .ace_constant.ace_numeric {\
color: #000;\
}\
.ace-zato .ace_variable {\
color: #000;\
}\
.ace-zato .ace_xml-pe {\
color: red;\
}\
.ace-zato .ace_entity.ace_name.ace_function {\
color: #000;\
}\
.ace-zato .ace_heading {\
color: rgb(12, 7, 255);\
}\
.ace-zato .ace_list {\
color:rgb(185, 6, 144);\
}\
.ace-zato .ace_marker-layer .ace_selection {\
background: #fcfc55;\
}\
.ace-zato .ace_marker-layer .ace_step {\
background: rgb(252, 255, 0);\
}\
.ace-zato .ace_marker-layer .ace_stack {\
background: rgb(164, 229, 101);\
}\
.ace-zato .ace_marker-layer .ace_bracket {\
margin: -1px 0 0 -1px;\
border: 1px solid rgb(192, 192, 192);\
}\
.ace-zato .ace_marker-layer .ace_active-line {\
background: rgba(0, 0, 0, 0.07);\
}\
.ace-zato .ace_gutter-active-line {\
background-color : #dcdcdc;\
}\
.ace-zato .ace_marker-layer .ace_selected-word {\
background: rgb(250, 250, 255);\
border: 1px solid rgb(200, 200, 250);\
}\
.ace-zato .ace_storage {\
color: violet;\
}\
.ace-zato .ace_keyword {\
color: #b21104;\
}\
.ace-zato .ace_meta.ace_tag {\
color: #000;\
}\
.ace-zato .ace_string.ace_regex {\
color: #000\
}\
.ace-zato .ace_string {\
color: #007f00;\
}\
.ace-zato .ace_entity.ace_other.ace_attribute-name {\
color: #000;\
}\
.ace-zato .ace_indent-guide {\
background: url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bLly//BwAmVgd1/w11/gAAAABJRU5ErkJggg==\") right repeat-y;\
}";

var dom = require("../lib/dom");
dom.importCssString(exports.cssText, exports.cssClass, false);
});                (function() {
                    window.require(["ace/theme/zato"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
