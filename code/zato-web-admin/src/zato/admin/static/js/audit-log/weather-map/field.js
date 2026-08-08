
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the elevation field. Every continent accretes out of
// hundreds of small chunks a seeded walk laid down, and the chunks are
// rasterized straight onto the grid - the way the old strategy games grew
// their land tile by tile - so the ground is one continuous, irregular
// surface. The waterline is not a constant - it is placed at the exact
// height that puts the wanted share of the world above water. A water
// frame fades the field to nothing before any edge, so no land is ever
// cut off by the map's border, and a seeded, domain-warped noise raggedens
// every coast into fjords, inlets and peninsulas. Everything is
// deterministic off the seeds alone.

$.fn.zato.weather_map.field = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var field = $.fn.zato.weather_map.field;

// /////////////////////////////////////////////////////////////////////////////

field.config = {

    // How far apart the field is sampled - one reading per this many
    // logical pixels, everything in between read bilinearly
    step: 2,

    // How hard the coast noise bends the shoreline - the accretion already
    // raggedens the outline, the noise only sharpens the detail
    noiseAmplitude: 0.16,

    // The noise only matters near land - between these two field readings
    // its weight fades in, so the open ocean stays open
    noiseFadeFrom: 0.06,
    noiseFadeTo: 0.45,

    // The wavelength of the coastal detail and of the warp that folds it
    coastScale: 0.013,
    warpScale: 0.005,
    warpAmplitude: 70,

    // How many octaves of detail the noise carries
    octaves: 4,

    // The bimodal hypsometry - the sigmoid that turns a smooth mound into
    // a flat continental platform with a steep slope down to the abyssal
    // plain, which is the profile real continents float at
    platformPivot: 0.24,
    platformSharpness: 9,

    // How wide the soft cliff of a rifted margin is - the straight coast
    // left where a landmass was torn
    riftWidth: 16,

    // How tall the collision belts stand above the platform
    ridgeHeight: 0.42,

    // The water frame - the field fades to open sea this close to any edge
    edgeMarginFraction: 0.06,
    edgeMarginMin: 36,

    // The waterline never sinks below this, however empty the world is
    seaLevelMin: 0.02
};

// /////////////////////////////////////////////////////////////////////////////

// One lattice cell always hashes to one number in [0, 1)
field.hashCell = function(cellX, cellY, seed) {
    var hash = seed ^ Math.imul(cellX, 374761393) ^ Math.imul(cellY, 668265263);

    hash = Math.imul(hash ^ (hash >>> 13), 1274126177);
    hash = hash ^ (hash >>> 16);

    return (hash >>> 0) / 4294967296;
};

// /////////////////////////////////////////////////////////////////////////////

// Smooth noise - the four surrounding lattice values blended with an
// ease-in-ease-out curve, so nothing creases at the cell borders
field.valueNoise = function(pointX, pointY, seed) {
    var cellX = Math.floor(pointX);
    var cellY = Math.floor(pointY);

    var fractionX = pointX - cellX;
    var fractionY = pointY - cellY;

    var easeX = fractionX * fractionX * (3 - 2 * fractionX);
    var easeY = fractionY * fractionY * (3 - 2 * fractionY);

    var topLeft = field.hashCell(cellX, cellY, seed);
    var topRight = field.hashCell(cellX + 1, cellY, seed);
    var bottomLeft = field.hashCell(cellX, cellY + 1, seed);
    var bottomRight = field.hashCell(cellX + 1, cellY + 1, seed);

    var top = topLeft + (topRight - topLeft) * easeX;
    var bottom = bottomLeft + (bottomRight - bottomLeft) * easeX;

    var out = top + (bottom - top) * easeY;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Octaves of the noise stacked up - broad swells first, ever finer ripples
// on top, the sum normalized back into [0, 1)
field.fractalNoise = function(pointX, pointY, seed) {
    var config = field.config;

    var total = 0;
    var amplitude = 1;
    var frequency = 1;
    var reach = 0;

    for(var octaveIdx = 0; octaveIdx < config.octaves; octaveIdx++) {

        total += field.valueNoise(pointX * frequency, pointY * frequency, seed + octaveIdx * 101) * amplitude;
        reach += amplitude;

        amplitude = amplitude * 0.5;
        frequency = frequency * 2;
    }

    var out = total / reach;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The coastal detail - the noise sampled through a warp of itself, which is
// what turns round wobbles into fjords and hooked peninsulas
field.coastNoise = function(pointX, pointY, seed) {
    var config = field.config;

    var warpX = field.fractalNoise(pointX * config.warpScale, pointY * config.warpScale, seed + 11);
    var warpY = field.fractalNoise(pointX * config.warpScale, pointY * config.warpScale, seed + 29);

    var bentX = pointX + (warpX - 0.5) * config.warpAmplitude;
    var bentY = pointY + (warpY - 0.5) * config.warpAmplitude;

    var out = field.fractalNoise(bentX * config.coastScale, bentY * config.coastScale, seed + 47);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// How wide the water frame is on a map of this size
field.edgeMargin = function(width, height) {
    var config = field.config;

    var out = Math.min(width, height) * config.edgeMarginFraction;

    if(out < config.edgeMarginMin) {
        out = config.edgeMarginMin;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The whole field sampled onto a grid - the elevation, whose ground every
// sample is, the waterline the land share puts where it must be, the slopes
// the hillshade reads, and where each continent's land gathers
field.build = function(continents, ridges, width, height, seed, landFraction) {
    var config = field.config;
    var step = config.step;

    var columns = Math.floor(width / step) + 2;
    var rows = Math.floor(height / step) + 2;

    var cellCount = columns * rows;

    var elevation = new Float32Array(cellCount);
    var bestShare = new Float32Array(cellCount);
    var scratch = new Float32Array(cellCount);

    var owner = new Int16Array(cellCount);
    owner.fill(-1);

    // Every continent's chunks are rasterized straight onto the grid, one
    // continent at a time - its pile gathers in the scratch, joins the
    // ground, and wherever its pile is the tallest so far, it owns the cell
    for(var continentIdx = 0; continentIdx < continents.length; continentIdx++) {
        var stamps = continents[continentIdx].stamps;

        scratch.fill(0);

        for(var stampIdx = 0; stampIdx < stamps.length; stampIdx++) {
            var stamp = stamps[stampIdx];

            var radiusSquared = stamp.radius * stamp.radius;

            var minColumn = Math.floor((stamp.x - stamp.radius) / step);
            var maxColumn = Math.ceil((stamp.x + stamp.radius) / step);
            var minRow = Math.floor((stamp.y - stamp.radius) / step);
            var maxRow = Math.ceil((stamp.y + stamp.radius) / step);

            if(minColumn < 0) {
                minColumn = 0;
            }
            if(minRow < 0) {
                minRow = 0;
            }
            if(maxColumn > columns - 1) {
                maxColumn = columns - 1;
            }
            if(maxRow > rows - 1) {
                maxRow = rows - 1;
            }

            for(var stampRowIdx = minRow; stampRowIdx <= maxRow; stampRowIdx++) {
                for(var stampColumnIdx = minColumn; stampColumnIdx <= maxColumn; stampColumnIdx++) {

                    var deltaX = stampColumnIdx * step - stamp.x;
                    var deltaY = stampRowIdx * step - stamp.y;

                    var normalized = (deltaX * deltaX + deltaY * deltaY) / radiusSquared;

                    if(normalized >= 1) {
                        continue;
                    }

                    var falloff = 1 - normalized;
                    scratch[stampRowIdx * columns + stampColumnIdx] += falloff * falloff * stamp.height;
                }
            }
        }

        // The basins are carved out of whatever piled up where they sit -
        // proportionally, so an inland sea holds in low ground and high,
        // and one breaching the coast opens into a gulf
        var basins = continents[continentIdx].basins;

        for(var basinIdx = 0; basinIdx < basins.length; basinIdx++) {
            var basin = basins[basinIdx];

            var basinRadiusSquared = basin.radius * basin.radius;

            var basinMinColumn = Math.floor((basin.x - basin.radius) / step);
            var basinMaxColumn = Math.ceil((basin.x + basin.radius) / step);
            var basinMinRow = Math.floor((basin.y - basin.radius) / step);
            var basinMaxRow = Math.ceil((basin.y + basin.radius) / step);

            if(basinMinColumn < 0) {
                basinMinColumn = 0;
            }
            if(basinMinRow < 0) {
                basinMinRow = 0;
            }
            if(basinMaxColumn > columns - 1) {
                basinMaxColumn = columns - 1;
            }
            if(basinMaxRow > rows - 1) {
                basinMaxRow = rows - 1;
            }

            for(var basinRowIdx = basinMinRow; basinRowIdx <= basinMaxRow; basinRowIdx++) {
                for(var basinColumnIdx = basinMinColumn; basinColumnIdx <= basinMaxColumn; basinColumnIdx++) {

                    var basinDeltaX = basinColumnIdx * step - basin.x;
                    var basinDeltaY = basinRowIdx * step - basin.y;

                    var basinNormalized = (basinDeltaX * basinDeltaX + basinDeltaY * basinDeltaY) / basinRadiusSquared;

                    if(basinNormalized >= 1) {
                        continue;
                    }

                    var basinFalloff = 1 - basinNormalized;
                    var basinIdxCell = basinRowIdx * columns + basinColumnIdx;

                    scratch[basinIdxCell] = scratch[basinIdxCell] * (1 - basinFalloff * basinFalloff * basin.strength);
                }
            }
        }

        var rift = continents[continentIdx].rift;

        for(var mergeRowIdx = 0; mergeRowIdx < rows; mergeRowIdx++) {
            for(var mergeColumnIdx = 0; mergeColumnIdx < columns; mergeColumnIdx++) {

                var pileIdx = mergeRowIdx * columns + mergeColumnIdx;
                var pile = scratch[pileIdx];

                if(!pile) {
                    continue;
                }

                // A rifted margin - the ground past the tear line drops off
                // over a soft cliff, which is what leaves the straight coast
                if(rift) {

                    var riftAlongX = mergeColumnIdx * step - rift.originX;
                    var riftAlongY = mergeRowIdx * step - rift.originY;

                    var signed = riftAlongX * rift.normalX + riftAlongY * rift.normalY;

                    if(signed > 0) {

                        if(signed >= config.riftWidth) {
                            continue;
                        }

                        var tear = 1 - signed / config.riftWidth;
                        pile = pile * tear * tear;
                    }
                }

                elevation[pileIdx] += pile;

                if(pile > bestShare[pileIdx]) {
                    bestShare[pileIdx] = pile;
                    owner[pileIdx] = continentIdx;
                }
            }
        }
    }

    // The collision belts are rasterized into their own relief, so they
    // can be laid on top of the shaped platforms and rise above them
    var relief = new Float32Array(cellCount);

    for(var ridgeIdx = 0; ridgeIdx < ridges.length; ridgeIdx++) {
        var ridgeStamp = ridges[ridgeIdx];

        var ridgeRadiusSquared = ridgeStamp.radius * ridgeStamp.radius;

        var ridgeMinColumn = Math.floor((ridgeStamp.x - ridgeStamp.radius) / step);
        var ridgeMaxColumn = Math.ceil((ridgeStamp.x + ridgeStamp.radius) / step);
        var ridgeMinRow = Math.floor((ridgeStamp.y - ridgeStamp.radius) / step);
        var ridgeMaxRow = Math.ceil((ridgeStamp.y + ridgeStamp.radius) / step);

        if(ridgeMinColumn < 0) {
            ridgeMinColumn = 0;
        }
        if(ridgeMinRow < 0) {
            ridgeMinRow = 0;
        }
        if(ridgeMaxColumn > columns - 1) {
            ridgeMaxColumn = columns - 1;
        }
        if(ridgeMaxRow > rows - 1) {
            ridgeMaxRow = rows - 1;
        }

        for(var ridgeRowIdx = ridgeMinRow; ridgeRowIdx <= ridgeMaxRow; ridgeRowIdx++) {
            for(var ridgeColumnIdx = ridgeMinColumn; ridgeColumnIdx <= ridgeMaxColumn; ridgeColumnIdx++) {

                var ridgeDeltaX = ridgeColumnIdx * step - ridgeStamp.x;
                var ridgeDeltaY = ridgeRowIdx * step - ridgeStamp.y;

                var ridgeNormalized = (ridgeDeltaX * ridgeDeltaX + ridgeDeltaY * ridgeDeltaY) / ridgeRadiusSquared;

                if(ridgeNormalized >= 1) {
                    continue;
                }

                var ridgeFalloff = 1 - ridgeNormalized;
                relief[ridgeRowIdx * columns + ridgeColumnIdx] += ridgeFalloff * ridgeFalloff * ridgeStamp.height;
            }
        }
    }

    // The ground is normalized so the platform sigmoid and the noise
    // thresholds mean the same however many chunks piled up anywhere
    var tallest = 0;

    for(var tallIdx = 0; tallIdx < cellCount; tallIdx++) {
        if(elevation[tallIdx] > tallest) {
            tallest = elevation[tallIdx];
        }
    }

    var scale = tallest > 0 ? 1 / tallest : 1;

    // The sigmoid's own span, so its output can be stretched back to [0, 1]
    var sigmoidFloor = 1 / (1 + Math.exp(config.platformPivot * config.platformSharpness));
    var sigmoidCeiling = 1 / (1 + Math.exp((config.platformPivot - 1) * config.platformSharpness));
    var sigmoidSpan = sigmoidCeiling - sigmoidFloor;

    var fadeSpan = config.noiseFadeTo - config.noiseFadeFrom;
    var margin = field.edgeMargin(width, height);

    for(var rowIdx = 0; rowIdx < rows; rowIdx++) {
        for(var columnIdx = 0; columnIdx < columns; columnIdx++) {

            var pointX = columnIdx * step;
            var pointY = rowIdx * step;

            var sampleIdx = rowIdx * columns + columnIdx;
            var base = elevation[sampleIdx] * scale;

            // The bimodal hypsometry - mid heights are pushed up onto a
            // flat platform and low ones down to the abyssal plain, so
            // the land reads as a continent, not as the tip of a mound
            var shaped = 1 / (1 + Math.exp((config.platformPivot - base) * config.platformSharpness));
            shaped = (shaped - sigmoidFloor) / sigmoidSpan;

            // The collision belts stand on top of the platform
            var value = shaped + relief[sampleIdx] * config.ridgeHeight;

            // The water frame - however tall the ground, it sinks into
            // the sea before any edge of the map
            var edgeDistance = pointX;

            if(pointY < edgeDistance) {
                edgeDistance = pointY;
            }
            if(width - pointX < edgeDistance) {
                edgeDistance = width - pointX;
            }
            if(height - pointY < edgeDistance) {
                edgeDistance = height - pointY;
            }

            if(edgeDistance < margin) {
                var edgeEase = edgeDistance / margin;

                if(edgeEase < 0) {
                    edgeEase = 0;
                }

                value = value * edgeEase * edgeEase * (3 - 2 * edgeEase);
            }

            // The coast noise fades in with the ground itself, so it bends
            // the shorelines without littering the open ocean
            var weight = (value - config.noiseFadeFrom) / fadeSpan;

            if(weight < 0) {
                weight = 0;
            }
            if(weight > 1) {
                weight = 1;
            }

            if(weight > 0) {
                var noise = field.coastNoise(pointX, pointY, seed);
                value = value + (noise - 0.5) * 2 * config.noiseAmplitude * weight;
            }

            elevation[sampleIdx] = value;
        }
    }

    // The waterline goes exactly where the wanted land share puts it -
    // the heights are sorted and the line is drawn at the right rank
    var sorted = elevation.slice();
    sorted.sort();

    var rankIdx = Math.floor(sorted.length * (1 - landFraction));

    if(rankIdx > sorted.length - 1) {
        rankIdx = sorted.length - 1;
    }

    var seaLevel = sorted[rankIdx];

    if(seaLevel < config.seaLevelMin) {
        seaLevel = config.seaLevelMin;
    }

    // Only now that the waterline is known can the land be told from the
    // sea - where each continent's ground gathers is where its name goes
    var centroidX = [];
    var centroidY = [];
    var landCells = [];

    for(var landIdx = 0; landIdx < continents.length; landIdx++) {
        centroidX.push(0);
        centroidY.push(0);
        landCells.push(0);
    }

    for(var landRowIdx = 0; landRowIdx < rows; landRowIdx++) {
        for(var landColumnIdx = 0; landColumnIdx < columns; landColumnIdx++) {

            var landSampleIdx = landRowIdx * columns + landColumnIdx;

            if(elevation[landSampleIdx] < seaLevel) {
                continue;
            }

            var landOwner = owner[landSampleIdx];

            if(landOwner < 0) {
                continue;
            }

            centroidX[landOwner] += landColumnIdx * step;
            centroidY[landOwner] += landRowIdx * step;
            landCells[landOwner] += 1;
        }
    }

    for(var ownerIdx = 0; ownerIdx < continents.length; ownerIdx++) {
        if(landCells[ownerIdx]) {
            centroidX[ownerIdx] = centroidX[ownerIdx] / landCells[ownerIdx];
            centroidY[ownerIdx] = centroidY[ownerIdx] / landCells[ownerIdx];
        }
    }

    // The slopes, read once so every later pass can look downhill cheaply
    var slopeX = new Float32Array(columns * rows);
    var slopeY = new Float32Array(columns * rows);

    for(var slopeRowIdx = 1; slopeRowIdx < rows - 1; slopeRowIdx++) {
        for(var slopeColumnIdx = 1; slopeColumnIdx < columns - 1; slopeColumnIdx++) {

            var slopeIdx = slopeRowIdx * columns + slopeColumnIdx;

            slopeX[slopeIdx] = elevation[slopeIdx - 1] - elevation[slopeIdx + 1];
            slopeY[slopeIdx] = elevation[slopeIdx - columns] - elevation[slopeIdx + columns];
        }
    }

    return {
        step: step,
        columns: columns,
        rows: rows,
        elevation: elevation,
        slopeX: slopeX,
        slopeY: slopeY,
        owner: owner,
        seaLevel: seaLevel,
        centroidX: centroidX,
        centroidY: centroidY,
        landCells: landCells
    };
};

// /////////////////////////////////////////////////////////////////////////////

// One grid array read bilinearly at any point between its samples
field.sampleArray = function(grid, values, pointX, pointY) {
    var step = grid.step;

    var gridX = pointX / step;
    var gridY = pointY / step;

    var columnIdx = Math.floor(gridX);
    var rowIdx = Math.floor(gridY);

    if(columnIdx < 0) {
        columnIdx = 0;
    }
    if(rowIdx < 0) {
        rowIdx = 0;
    }
    if(columnIdx > grid.columns - 2) {
        columnIdx = grid.columns - 2;
    }
    if(rowIdx > grid.rows - 2) {
        rowIdx = grid.rows - 2;
    }

    var fractionX = gridX - columnIdx;
    var fractionY = gridY - rowIdx;

    var sampleIdx = rowIdx * grid.columns + columnIdx;

    var topLeft = values[sampleIdx];
    var topRight = values[sampleIdx + 1];
    var bottomLeft = values[sampleIdx + grid.columns];
    var bottomRight = values[sampleIdx + grid.columns + 1];

    var top = topLeft + (topRight - topLeft) * fractionX;
    var bottom = bottomLeft + (bottomRight - bottomLeft) * fractionX;

    var out = top + (bottom - top) * fractionY;
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

field.sample = function(grid, pointX, pointY) {
    var out = field.sampleArray(grid, grid.elevation, pointX, pointY);
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Whose ground one point stands on - the nearest sample answers
field.ownerAt = function(grid, pointX, pointY) {
    var columnIdx = Math.round(pointX / grid.step);
    var rowIdx = Math.round(pointY / grid.step);

    if(columnIdx < 0) {
        columnIdx = 0;
    }
    if(rowIdx < 0) {
        rowIdx = 0;
    }
    if(columnIdx > grid.columns - 1) {
        columnIdx = grid.columns - 1;
    }
    if(rowIdx > grid.rows - 1) {
        rowIdx = grid.rows - 1;
    }

    var out = grid.owner[rowIdx * grid.columns + columnIdx];
    return out;
};

// /////////////////////////////////////////////////////////////////////////////

})();
