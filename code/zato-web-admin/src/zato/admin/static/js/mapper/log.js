
// Mapper kit - console logging.
// Every part of the kit reports what it does to the browser console:
// store mutations, undo and redo, evaluator runs with per-row outcomes,
// preview runs, selections, commits and schema panel actions. Each entry
// is one line with the area, the message and the data serialized as JSON.

(function($) {

    // Logs one line: [mapper] area: message {"data": ...}
    zato.mapper.log = function(area, message, data) {

        var line = '[mapper] ' + area + ': ' + message;

        if (data === undefined) {
            console.log(line);
        }
        else {
            console.log(line + ' ' + JSON.stringify(data));
        }
    };

})(jQuery);
