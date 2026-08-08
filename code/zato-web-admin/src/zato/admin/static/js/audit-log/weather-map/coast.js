
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the contours. Once the world is one continuous field, its
// shorelines and depth lines are wherever the field crosses one value, and
// marching squares walks the grid and finds every such crossing - the
// coastline at the sea level, the depth contours below it.

$.fn.zato.weather_map.coast = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var coast = $.fn.zato.weather_map.coast;

// /////////////////////////////////////////////////////////////////////////////

// Where between two samples the threshold is crossed - 0 at the first
// sample, 1 at the second
coast.crossing = function(firstValue, secondValue, threshold) {
    var span = secondValue - firstValue;

    // Two equal samples straddling a threshold can only both sit on it,
    // so the crossing is anywhere between them
    if(span === 0) {
        return 0.5;
    }

    var out = (threshold - firstValue) / span;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Every piece of one contour, as a path ready for stroking. The pieces are
// tiny disconnected segments, which stroking neither knows nor minds.
coast.buildPath = function(grid, threshold) {
    var step = grid.step;
    var columns = grid.columns;
    var elevation = grid.elevation;

    var out = new Path2D();

    for(var rowIdx = 0; rowIdx < grid.rows - 1; rowIdx++) {
        for(var columnIdx = 0; columnIdx < columns - 1; columnIdx++) {

            var sampleIdx = rowIdx * columns + columnIdx;

            var topLeft = elevation[sampleIdx];
            var topRight = elevation[sampleIdx + 1];
            var bottomRight = elevation[sampleIdx + columns + 1];
            var bottomLeft = elevation[sampleIdx + columns];

            // Which corners stand above the threshold names the case
            var caseIdx = 0;

            if(topLeft >= threshold) {
                caseIdx += 8;
            }
            if(topRight >= threshold) {
                caseIdx += 4;
            }
            if(bottomRight >= threshold) {
                caseIdx += 2;
            }
            if(bottomLeft >= threshold) {
                caseIdx += 1;
            }

            if(caseIdx === 0) {
                continue;
            }
            if(caseIdx === 15) {
                continue;
            }

            var leftX = columnIdx * step;
            var topY = rowIdx * step;
            var rightX = leftX + step;
            var bottomY = topY + step;

            // The four possible crossing points, one per cell edge
            var topPointX = leftX + coast.crossing(topLeft, topRight, threshold) * step;
            var bottomPointX = leftX + coast.crossing(bottomLeft, bottomRight, threshold) * step;
            var leftPointY = topY + coast.crossing(topLeft, bottomLeft, threshold) * step;
            var rightPointY = topY + coast.crossing(topRight, bottomRight, threshold) * step;

            switch(caseIdx) {

                case 1:
                case 14:
                    out.moveTo(leftX, leftPointY);
                    out.lineTo(bottomPointX, bottomY);
                    break;

                case 2:
                case 13:
                    out.moveTo(bottomPointX, bottomY);
                    out.lineTo(rightX, rightPointY);
                    break;

                case 3:
                case 12:
                    out.moveTo(leftX, leftPointY);
                    out.lineTo(rightX, rightPointY);
                    break;

                case 4:
                case 11:
                    out.moveTo(topPointX, topY);
                    out.lineTo(rightX, rightPointY);
                    break;

                case 5:
                    out.moveTo(leftX, leftPointY);
                    out.lineTo(topPointX, topY);
                    out.moveTo(bottomPointX, bottomY);
                    out.lineTo(rightX, rightPointY);
                    break;

                case 6:
                case 9:
                    out.moveTo(topPointX, topY);
                    out.lineTo(bottomPointX, bottomY);
                    break;

                case 7:
                case 8:
                    out.moveTo(leftX, leftPointY);
                    out.lineTo(topPointX, topY);
                    break;

                case 10:
                    out.moveTo(topPointX, topY);
                    out.lineTo(rightX, rightPointY);
                    out.moveTo(leftX, leftPointY);
                    out.lineTo(bottomPointX, bottomY);
                    break;
            }
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The coastline itself - the one contour the sea level draws
coast.coastline = function(grid) {
    var out = coast.buildPath(grid, grid.seaLevel);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

})();
