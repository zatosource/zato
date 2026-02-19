define("ace/theme/zato-dark",["require","exports","module"], function(require, exports, module) {

exports.isDark = true;
exports.cssClass = "ace-zato-dark";

});
(function() {
    window.require(["ace/theme/zato-dark"], function(m) {
        if (typeof module == "object" && typeof exports == "object" && module) {
            module.exports = m;
        }
    });
})();
