
/* Dashboard kit - SVG drawing primitives.
   The shapes every dashboard drawing is put together from - rectangles, text,
   text over several lines, plain lines and arrowheads - plus the measuring
   helpers a layout works with: wrapping text to a width and finding the
   longest of the lines it wrapped to. Nothing here decides what a drawing
   looks like - class names, corner radii and character widths are the
   caller's business. */

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.draw = {};

    var svgNamespace = 'http://www.w3.org/2000/svg';

    /* ------------------------------------------------------------ */

    ns.draw.createElement = function(name) {
        var out = document.createElementNS(svgNamespace, name);
        return out;
    };

    /* ------------------------------------------------------------ */

    ns.draw.addRect = function(host, x, y, width, height, className, radius) {
        var rect = ns.draw.createElement('rect');

        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', width);
        rect.setAttribute('height', height);
        rect.setAttribute('rx', radius);
        rect.setAttribute('class', className);

        host.appendChild(rect);
        return rect;
    };

    /* ------------------------------------------------------------ */

    ns.draw.addText = function(host, x, y, text, className, anchor) {
        var element = ns.draw.createElement('text');

        element.setAttribute('x', x);
        element.setAttribute('y', y);
        element.setAttribute('text-anchor', anchor);
        element.setAttribute('class', className);
        element.textContent = text;

        host.appendChild(element);
        return element;
    };

    /* ------------------------------------------------------------ */

    /* Text that runs on over several lines, one line under the other, all of
       them about the same middle. The line the text starts on is where a
       single line would have stood, so a name of one line is set exactly
       where it always was. */
    ns.draw.addTextLines = function(host, x, baseline, textLineList, className, lineHeight) {
        var out = [];

        for(var lineIdx = 0; lineIdx < textLineList.length; lineIdx++) {
            var y = baseline + lineIdx * lineHeight;
            out.push(ns.draw.addText(host, x, y, textLineList[lineIdx], className, 'middle'));
        }

        return out;
    };

    /* ------------------------------------------------------------ */

    ns.draw.addLine = function(host, x1, y1, x2, y2, className) {
        var line = ns.draw.createElement('line');

        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('class', className);

        host.appendChild(line);
        return line;
    };

    /* ------------------------------------------------------------ */

    /* A downward-pointing arrowhead ending at (x, y). */
    ns.draw.addArrow = function(host, x, y, length, width, className) {
        var top = y - length;
        var arrow = ns.draw.createElement('polygon');

        var points = (x - width) + ',' + top + ' ' +
            (x + width) + ',' + top + ' ' + x + ',' + y;

        arrow.setAttribute('points', points);
        arrow.setAttribute('class', className);

        host.appendChild(arrow);
        return arrow;
    };

    /* ------------------------------------------------------------ */

    /* Text longer than the room it has, laid out over as many lines as it
       takes - nothing is ever left out. The break falls on the last space
       that still fits, and text with no space in it is broken where the
       room ends. */
    ns.draw.wrap = function(text, room, charWidth) {
        var maxLength = Math.max(1, Math.floor(room / charWidth));
        var out = [];
        var rest = text;

        while(rest.length > maxLength) {
            var cutIdx = maxLength;
            var skipCount = 0;
            var spaceIdx = rest.lastIndexOf(' ', maxLength);

            if(spaceIdx > 0) {
                cutIdx = spaceIdx;
                skipCount = 1;
            }

            out.push(rest.slice(0, cutIdx));
            rest = rest.slice(cutIdx + skipCount);
        }

        out.push(rest);

        return out;
    };

    /* ------------------------------------------------------------ */

    /* How long the longest of the lines is, which is what says how wide the
       shape they go into has to be. */
    ns.draw.getLongest = function(textLineList) {
        var out = 0;

        for(var lineIdx = 0; lineIdx < textLineList.length; lineIdx++) {
            out = Math.max(out, textLineList[lineIdx].length);
        }

        return out;
    };

})();
