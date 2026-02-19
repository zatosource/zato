define("ace/theme/zato",["require","exports","module"], function(require, exports, module) {

exports.isDark = false;
exports.cssClass = "ace-zato";

});
(function() {
    window.require(["ace/theme/zato"], function(m) {
        if (typeof module == "object" && typeof exports == "object" && module) {
            module.exports = m;
        }
    });
})();
