
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the geography. The world is generated out of the inventory
// alone, deterministically - the same connections always draw the same map.
// Every type lays its ground down the way the old strategy games did - a
// seeded drunken walk drops hundreds of small chunks of ground, one on top
// of another, branching back into itself to grow lobes and peninsulas, so
// a landmass accretes into an irregular shape no circle survives in.
// Related types are pulled together so their ground fuses into shared
// continents, unrelated ones keep straits between them, and every
// connection is a city placed by a hash of its own name onto its own
// type's land.

$.fn.zato.weather_map = {};
$.fn.zato.weather_map.geography = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var geography = $.fn.zato.weather_map.geography;

// /////////////////////////////////////////////////////////////////////////////

geography.config = {

    // How much of the canvas the land covers, all continents together -
    // the waterline is placed so this share holds exactly
    landFraction: 0.4,

    // How unequal the landmasses are - real worlds have a couple of
    // dominant continents, not equal blobs, and this exponent spreads
    // the shares apart
    massDominance: 1.9,

    // How often a landmass carries a rifted margin - the straight coast
    // left where it was torn off another one - and how far out of its
    // center the tear line runs
    riftChance: 0.45,
    riftOffsetMin: 0.45,
    riftOffsetSpan: 0.3,

    // The collision belts - where two fused neighbours press on one
    // another, a mountain range runs along the suture
    ridgeStampRadius: 11,
    ridgeStampSpacing: 0.55,
    ridgeLength: 0.85,
    ridgeWobble: 7,
    ridgeHeightVariance: 0.5,

    // The one great ocean - a seeded share of the map claimed before any
    // land is placed, so every world keeps one long open basin
    oceanReserveFraction: 0.3,
    oceanReserveOffset: 0.32,

    // The hotspot chains - short trails of small islands out in the open
    // water, each seeded off its own index
    hotspotChains: 3,
    hotspotStampsMin: 3,
    hotspotStampsSpan: 4,
    hotspotRadiusMin: 6,
    hotspotRadiusSpan: 7,
    hotspotStep: 2.4,
    hotspotCurve: 0.5,
    hotspotTries: 30,
    hotspotClearance: 34,

    // The island arcs - chains curving off the biggest continents' flanks
    arcContinents: 2,
    arcStamps: 5,
    arcRadius: 8,
    arcRadiusVariance: 0.6,
    arcDistance: 1.25,
    arcSpread: 0.9,

    // Lone islands are small piles on a field ruled by the tall interiors,
    // so their chunks stand taller to be sure of surfacing
    hotspotHeight: 3,
    arcHeight: 2.5,

    // The basins - inland seas and gulfs carved out of the big masses,
    // one per this many chunks of ground, up to the cap
    basinStampsPer: 60,
    basinCountMax: 3,
    basinRadiusMin: 1.6,
    basinRadiusSpan: 1.2,
    basinReach: 0.8,
    basinStrength: 0.85,

    // The chunk of ground one step of the walk lays down grows with the
    // landmass itself - a dominant continent accretes in bold strokes,
    // an islet in small ones - and how unevenly the chunks are sized
    stampRadiusScale: 0.085,
    stampRadiusMin: 12,
    stampRadiusMax: 30,
    stampRadiusVariance: 0.5,

    // How many chunks one type's walk may drop - its share of the land
    // decides the exact number within these bounds
    stampCountMin: 60,
    stampCountMax: 340,

    // How much of a chunk's area counts as new ground - chunks overlap
    stampPacking: 0.5,

    // How far the walk steps between chunks, as a share of the chunk size
    walkStep: 0.55,

    // How often the walk jumps back onto ground already laid and grows a
    // new lobe out of it
    walkBranchChance: 0.09,

    // How far out of its own heartland the walk may wander before the
    // leash pulls it back - the sprawl is what makes a mass continental
    walkLeash: 1.6,

    // Which types belong on one continent - the sides of one protocol
    // fuse, the health family fuses, the mail pair fuses
    groupCatalog: [
        ['rest-channel', 'rest-outgoing', 'soap-channel', 'soap-outgoing'],
        ['mllp-channel', 'mllp-outgoing', 'fhir'],
        ['email-imap', 'email-smtp'],
        ['pubsub'],
        ['sql-outgoing']
    ],

    // How close two members of one group stand - near enough for their
    // ground to fuse - and how close they may ever get
    memberSpacing: 0.8,
    memberSeparation: 0.62,
    memberAttempts: 40,

    // How much open water two groups keep between their bounds - below 1
    // the bounds may brush, and the world leans supercontinental
    groupSeparation: 0.8,

    // How far from the water frame a group keeps, on top of the frame itself
    edgePad: 14,

    // How many spots the placement tries before settling for the least
    // crowded one
    placementAttempts: 240,

    // How far out of its own center a city may look for ground
    cityReach: 0.95,

    // How many placements a city tries before falling in around the
    // continent's heartland
    cityAttempts: 60,

    // The least room two cities keep between one another
    cityGap: 26,

    // How much ground above the waterline a city insists on
    cityClearance: 0.05
};

// /////////////////////////////////////////////////////////////////////////////

// One text always hashes to one number, which is what seeds every random
// stream the map is drawn from
geography.hashText = function(text) {
    var hash = 2166136261;

    for(var charIdx = 0; charIdx < text.length; charIdx++) {
        hash = hash ^ text.charCodeAt(charIdx);
        hash = Math.imul(hash, 16777619);
    }

    return hash >>> 0;
};

// /////////////////////////////////////////////////////////////////////////////

// A seeded stream of numbers in [0, 1) - the same seed always yields
// the same sequence, which is what keeps the map deterministic
geography.makeRandom = function(seed) {
    var state = seed;

    return function() {
        state = (state + 0x6D2B79F5) | 0;

        var mixed = Math.imul(state ^ (state >>> 15), 1 | state);
        mixed = (mixed + Math.imul(mixed ^ (mixed >>> 7), 61 | mixed)) ^ mixed;

        return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
    };
};

// /////////////////////////////////////////////////////////////////////////////

// One type's ground - a drunken walk that lays down one small chunk after
// another, jumping back into itself now and then to grow a new lobe, kept
// on a leash so it accretes into one mass rather than a trail. Hundreds of
// small chunks melt into an irregular landmass in which no single chunk is
// ever visible. The walk is seeded off the type name alone, so its
// character survives any relayout.
geography.buildLand = function(source, mass) {
    var config = geography.config;

    var random = geography.makeRandom(geography.hashText('land|' + source));

    // The stroke grows with the mass - a dominant continent is drawn in
    // bold chunks, an islet in fine ones
    var stampRadius = Math.sqrt(mass) * config.stampRadiusScale;

    if(stampRadius < config.stampRadiusMin) {
        stampRadius = config.stampRadiusMin;
    }
    if(stampRadius > config.stampRadiusMax) {
        stampRadius = config.stampRadiusMax;
    }

    // How many chunks this type's share of the land comes to
    var stampArea = stampRadius * stampRadius * Math.PI * config.stampPacking;
    var count = Math.round(mass / stampArea);

    if(count < config.stampCountMin) {
        count = config.stampCountMin;
    }
    if(count > config.stampCountMax) {
        count = config.stampCountMax;
    }

    // The leash - how far from the heartland the walk may roam before it
    // is turned around
    var leash = Math.sqrt(mass / Math.PI) * config.walkLeash;

    var stamps = [];

    var walkX = 0;
    var walkY = 0;

    for(var stampIdx = 0; stampIdx < count; stampIdx++) {

        var sizing = 1 - config.stampRadiusVariance / 2 + random() * config.stampRadiusVariance;
        var radius = stampRadius * sizing;

        stamps.push({x: walkX, y: walkY, radius: radius, height: 1});

        // Now and then the walk jumps back onto ground already laid, and
        // the next steps grow a fresh lobe out of that older shore
        if(stamps.length > 4 && random() < config.walkBranchChance) {
            var branch = stamps[Math.floor(random() * stamps.length)];

            walkX = branch.x;
            walkY = branch.y;
        }

        // Each step goes wherever it pleases - the drunken walk is what
        // keeps any circle from surviving in the outline
        var angle = random() * Math.PI * 2;

        // Unless the walk has roamed too far - then it is pointed home
        var roam = Math.sqrt(walkX * walkX + walkY * walkY);

        if(roam > leash) {
            angle = Math.atan2(-walkY, -walkX) + (random() - 0.5) * 1.2;
        }

        var stepLength = radius * 2 * config.walkStep;

        walkX += Math.cos(angle) * stepLength;
        walkY += Math.sin(angle) * stepLength;
    }

    // The basins - a big mass carries inland seas and gulfs, carved out
    // of whatever ground piled up where they sit
    var basins = [];

    var basinCount = Math.floor(count / config.basinStampsPer);

    if(basinCount > config.basinCountMax) {
        basinCount = config.basinCountMax;
    }

    for(var basinIdx = 0; basinIdx < basinCount; basinIdx++) {

        var basinAngle = random() * Math.PI * 2;
        var basinReach = random() * leash * config.basinReach;
        var basinRadius = stampRadius * (config.basinRadiusMin + random() * config.basinRadiusSpan);

        basins.push({
            x: Math.cos(basinAngle) * basinReach,
            y: Math.sin(basinAngle) * basinReach,
            radius: basinRadius,
            strength: config.basinStrength
        });
    }

    // The walk is recentered on its own middle so the placement can treat
    // it as one circle
    var centerX = 0;
    var centerY = 0;

    for(var centerIdx = 0; centerIdx < stamps.length; centerIdx++) {
        centerX += stamps[centerIdx].x;
        centerY += stamps[centerIdx].y;
    }

    centerX = centerX / stamps.length;
    centerY = centerY / stamps.length;

    var boundRadius = 0;

    for(var boundIdx = 0; boundIdx < stamps.length; boundIdx++) {
        var stamp = stamps[boundIdx];

        stamp.x = stamp.x - centerX;
        stamp.y = stamp.y - centerY;

        var reach = Math.sqrt(stamp.x * stamp.x + stamp.y * stamp.y) + stamp.radius;

        if(reach > boundRadius) {
            boundRadius = reach;
        }
    }

    for(var basinCenterIdx = 0; basinCenterIdx < basins.length; basinCenterIdx++) {
        basins[basinCenterIdx].x = basins[basinCenterIdx].x - centerX;
        basins[basinCenterIdx].y = basins[basinCenterIdx].y - centerY;
    }

    return {stamps: stamps, basins: basins, radius: boundRadius};
};

// /////////////////////////////////////////////////////////////////////////////

// The hotspot chains - short seeded trails of small islands out in the
// open water, the way a plume dots a plate moving over it. Every chain
// joins whichever continent stands nearest, as its offshore islands.
geography.scatterHotspots = function(continents, landBounds, width, height, layoutSeed) {
    var config = geography.config;
    var field = $.fn.zato.weather_map.field;

    var margin = field.edgeMargin(width, height) + config.edgePad;

    for(var chainIdx = 0; chainIdx < config.hotspotChains; chainIdx++) {

        var random = geography.makeRandom(geography.hashText('hotspot|' + chainIdx + '|' + layoutSeed));

        // The chain needs open water - a start clear of every landmass
        var startX = 0;
        var startY = 0;
        var open = false;

        for(var tryIdx = 0; tryIdx < config.hotspotTries; tryIdx++) {

            startX = margin + random() * (width - margin * 2);
            startY = margin + random() * (height - margin * 2);

            open = true;

            for(var boundIdx = 0; boundIdx < landBounds.length; boundIdx++) {
                var bound = landBounds[boundIdx];

                var deltaX = startX - bound.centerX;
                var deltaY = startY - bound.centerY;
                var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                if(distance < bound.radius + config.hotspotClearance) {
                    open = false;
                    break;
                }
            }

            if(open) {
                break;
            }
        }

        // A world too full for this chain simply does not carry it
        if(!open) {
            continue;
        }

        // The chain joins the nearest continent as its offshore islands
        var ownerIdx = 0;
        var ownerDistance = Infinity;

        for(var continentIdx = 0; continentIdx < continents.length; continentIdx++) {
            var continent = continents[continentIdx];

            var toContinentX = startX - continent.centerX;
            var toContinentY = startY - continent.centerY;
            var toContinent = Math.sqrt(toContinentX * toContinentX + toContinentY * toContinentY);

            if(toContinent < ownerDistance) {
                ownerDistance = toContinent;
                ownerIdx = continentIdx;
            }
        }

        var count = config.hotspotStampsMin + Math.floor(random() * config.hotspotStampsSpan);
        var angle = random() * Math.PI * 2;

        var chainX = startX;
        var chainY = startY;

        for(var stampIdx = 0; stampIdx < count; stampIdx++) {

            var radius = config.hotspotRadiusMin + random() * config.hotspotRadiusSpan;

            continents[ownerIdx].stamps.push({
                x: chainX,
                y: chainY,
                radius: radius,
                height: config.hotspotHeight
            });

            // The chain drifts on and bends a little, plume-trail style
            angle += (random() - 0.5) * config.hotspotCurve;

            chainX += Math.cos(angle) * radius * config.hotspotStep;
            chainY += Math.sin(angle) * radius * config.hotspotStep;
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The island arcs - a chain curving off a big continent's flank, the way
// subduction bends island arcs off real margins
geography.scatterArcs = function(continents) {
    var config = geography.config;

    // The biggest continents carry the arcs
    var order = [];

    for(var orderIdx = 0; orderIdx < continents.length; orderIdx++) {
        order.push(orderIdx);
    }

    order.sort(function(first, second) {
        return continents[second].radius - continents[first].radius;
    });

    var arcCount = config.arcContinents;

    if(arcCount > order.length) {
        arcCount = order.length;
    }

    for(var pickIdx = 0; pickIdx < arcCount; pickIdx++) {
        var continent = continents[order[pickIdx]];

        var random = geography.makeRandom(geography.hashText('arc|' + continent.source));

        var baseAngle = random() * Math.PI * 2;
        var distance = continent.radius * config.arcDistance;

        for(var stampIdx = 0; stampIdx < config.arcStamps; stampIdx++) {

            // The arc sweeps around the flank, one stamp per step of it
            var sweep = stampIdx / (config.arcStamps - 1) - 0.5;
            var angle = baseAngle + sweep * config.arcSpread;

            var sizing = 1 - config.arcRadiusVariance / 2 + random() * config.arcRadiusVariance;

            continent.stamps.push({
                x: continent.centerX + Math.cos(angle) * distance,
                y: continent.centerY + Math.sin(angle) * distance,
                radius: config.arcRadius * sizing,
                height: config.arcHeight
            });
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The mountain range between two fused neighbours - a belt of tall, narrow
// stamps running along the suture, perpendicular to the line joining the
// two heartlands, wobbling a little so it reads as a range and not a wall
geography.buildRidge = function(sourceA, sourceB, pointA, pointB, radiusA, radiusB) {
    var config = geography.config;

    var random = geography.makeRandom(geography.hashText('ridge|' + sourceA + '|' + sourceB));

    var axisX = pointB.x - pointA.x;
    var axisY = pointB.y - pointA.y;
    var axisLength = Math.sqrt(axisX * axisX + axisY * axisY);

    axisX = axisX / axisLength;
    axisY = axisY / axisLength;

    // The belt runs across the axis, through its middle
    var perpX = -axisY;
    var perpY = axisX;

    var midX = (pointA.x + pointB.x) / 2;
    var midY = (pointA.y + pointB.y) / 2;

    var smaller = radiusA < radiusB ? radiusA : radiusB;
    var length = smaller * config.ridgeLength;

    var stepLength = config.ridgeStampRadius * 2 * config.ridgeStampSpacing;
    var count = Math.floor(length / stepLength) + 1;

    var out = [];

    for(var stampIdx = 0; stampIdx < count; stampIdx++) {

        var along = -length / 2 + stampIdx * stepLength;

        // The seeded wander off the line is what keeps the belt alive
        var wobble = (random() - 0.5) * 2 * config.ridgeWobble;
        var height = 1 - config.ridgeHeightVariance / 2 + random() * config.ridgeHeightVariance;

        out.push({
            x: midX + perpX * along + axisX * wobble,
            y: midY + perpY * along + axisY * wobble,
            radius: config.ridgeStampRadius,
            height: height
        });
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Which inventory entries share a continent - the catalog names the
// families, and a type the catalog does not know stands alone
geography.buildGroups = function(inventory) {
    var catalog = geography.config.groupCatalog;

    var familyBySource = {};

    for(var familyIdx = 0; familyIdx < catalog.length; familyIdx++) {
        for(var memberIdx = 0; memberIdx < catalog[familyIdx].length; memberIdx++) {
            familyBySource[catalog[familyIdx][memberIdx]] = familyIdx;
        }
    }

    var groupByKey = {};
    var out = [];

    for(var entryIdx = 0; entryIdx < inventory.length; entryIdx++) {

        var source = inventory[entryIdx].source;
        var key = source in familyBySource ? 'family-' + familyBySource[source] : 'alone-' + source;

        if(!(key in groupByKey)) {
            var group = {key: key, entryIdxs: []};

            groupByKey[key] = group;
            out.push(group);
        }

        groupByKey[key].entryIdxs.push(entryIdx);
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// Where a group's members stand around one another - each chained onto the
// one before it, near enough to fuse and no nearer than the floor allows
geography.layoutMembers = function(memberRadii, random) {
    var config = geography.config;

    var positions = [{x: 0, y: 0}];

    for(var memberIdx = 1; memberIdx < memberRadii.length; memberIdx++) {

        var anchor = positions[memberIdx - 1];
        var spacing = (memberRadii[memberIdx - 1] + memberRadii[memberIdx]) * config.memberSpacing;

        var candidateX = anchor.x + spacing;
        var candidateY = anchor.y;

        for(var attemptIdx = 0; attemptIdx < config.memberAttempts; attemptIdx++) {

            var angle = random() * Math.PI * 2;

            candidateX = anchor.x + Math.cos(angle) * spacing;
            candidateY = anchor.y + Math.sin(angle) * spacing;

            // The spot holds once every earlier member keeps its floor distance
            var crowded = false;

            for(var otherIdx = 0; otherIdx < memberIdx - 1; otherIdx++) {
                var other = positions[otherIdx];

                var deltaX = candidateX - other.x;
                var deltaY = candidateY - other.y;
                var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                var floor = (memberRadii[otherIdx] + memberRadii[memberIdx]) * config.memberSeparation;

                if(distance < floor) {
                    crowded = true;
                    break;
                }
            }

            if(!crowded) {
                break;
            }
        }

        positions.push({x: candidateX, y: candidateY});
    }

    return positions;
};

// /////////////////////////////////////////////////////////////////////////////

// The circle one whole group fits in, which is what the group placement
// keeps apart from the other groups and from the edges
geography.boundingCircle = function(positions, memberRadii) {
    var centerX = 0;
    var centerY = 0;

    for(var positionIdx = 0; positionIdx < positions.length; positionIdx++) {
        centerX += positions[positionIdx].x;
        centerY += positions[positionIdx].y;
    }

    centerX = centerX / positions.length;
    centerY = centerY / positions.length;

    var radius = 0;

    for(var memberIdx = 0; memberIdx < positions.length; memberIdx++) {

        var deltaX = positions[memberIdx].x - centerX;
        var deltaY = positions[memberIdx].y - centerY;

        var reach = Math.sqrt(deltaX * deltaX + deltaY * deltaY) + memberRadii[memberIdx];

        if(reach > radius) {
            radius = reach;
        }
    }

    return {centerX: centerX, centerY: centerY, radius: radius};
};

// /////////////////////////////////////////////////////////////////////////////

// Where one more group goes - open water is sampled all over the map in a
// seeded order, and the composition decides among the spots that fit. The
// anchor - the dominant mass - stands as near the visual center as the
// water allows, the counterweight stands as far across the water from the
// anchor as it can, and everything after takes the roomiest spot left.
// A crowded map settles for the least crowded spot there is.
geography.placeGroup = function(placed, radius, width, height, random, edgePad, role, anchor) {
    var config = geography.config;

    var margin = radius + edgePad;

    var spanX = width - margin * 2;
    var spanY = height - margin * 2;

    // A group too big for its canvas can only stand in the middle
    if(spanX < 1 || spanY < 1) {
        return {centerX: width / 2, centerY: height / 2};
    }

    var bestX = width / 2;
    var bestY = height / 2;
    var bestClearance = -Infinity;

    var bestFitX = 0;
    var bestFitY = 0;
    var bestFitScore = -Infinity;
    var anyFit = false;

    for(var attemptIdx = 0; attemptIdx < config.placementAttempts; attemptIdx++) {

        var candidateX = margin + random() * spanX;
        var candidateY = margin + random() * spanY;

        // How much open water the tightest neighbour leaves - positive
        // means the required separation holds
        var clearance = Infinity;

        for(var neighbourIdx = 0; neighbourIdx < placed.length; neighbourIdx++) {
            var neighbour = placed[neighbourIdx];

            var deltaX = candidateX - neighbour.centerX;
            var deltaY = candidateY - neighbour.centerY;
            var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            var required = (radius + neighbour.radius) * config.groupSeparation;
            var room = distance - required;

            if(room < clearance) {
                clearance = room;
            }
        }

        if(clearance > bestClearance) {
            bestClearance = clearance;
            bestX = candidateX;
            bestY = candidateY;
        }

        if(clearance < 0) {
            continue;
        }

        // Among the spots that fit, the role decides which one wins
        var score = clearance;

        if(role === 'anchor') {

            var toCenterX = candidateX - width / 2;
            var toCenterY = candidateY - height / 2;

            score = -Math.sqrt(toCenterX * toCenterX + toCenterY * toCenterY);
        }

        if(role === 'counterweight') {

            var toAnchorX = candidateX - anchor.centerX;
            var toAnchorY = candidateY - anchor.centerY;

            score = Math.sqrt(toAnchorX * toAnchorX + toAnchorY * toAnchorY);
        }

        if(score > bestFitScore) {
            bestFitScore = score;
            bestFitX = candidateX;
            bestFitY = candidateY;
            anyFit = true;
        }
    }

    if(anyFit) {
        return {centerX: bestFitX, centerY: bestFitY};
    }

    return {centerX: bestX, centerY: bestY};
};

// /////////////////////////////////////////////////////////////////////////////

// Where one city stands - hashed off its own name, on its own type's
// ground and clear of the water, kept out of its neighbours' way. A name
// whose every try lands in the sea settles in around the heartland.
geography.placeCity = function(model, continentIdx, name) {
    var config = geography.config;
    var field = $.fn.zato.weather_map.field;

    var continent = model.continents[continentIdx];

    var seed = geography.hashText(continent.source + '|' + name);
    var random = geography.makeRandom(seed);

    var waterline = model.grid.seaLevel + config.cityClearance;

    var cityX = continent.labelX;
    var cityY = continent.labelY;
    var placed = false;

    for(var attemptIdx = 0; attemptIdx < config.cityAttempts; attemptIdx++) {

        var angle = random() * Math.PI * 2;
        var reach = Math.sqrt(random()) * config.cityReach * continent.radius;

        var candidateX = continent.centerX + Math.cos(angle) * reach;
        var candidateY = continent.centerY + Math.sin(angle) * reach;

        // Dry ground of the right owner first ..
        if(field.sample(model.grid, candidateX, candidateY) < waterline) {
            continue;
        }
        if(field.ownerAt(model.grid, candidateX, candidateY) !== continentIdx) {
            continue;
        }

        // .. then room from the cities already standing.
        var crowded = false;

        for(var cityIdx = 0; cityIdx < continent.cities.length; cityIdx++) {
            var other = continent.cities[cityIdx];

            var deltaX = candidateX - other.x;
            var deltaY = candidateY - other.y;
            var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            if(distance < config.cityGap) {
                crowded = true;
                break;
            }
        }

        if(!crowded) {
            cityX = candidateX;
            cityY = candidateY;
            placed = true;
            break;
        }
    }

    // The heartland fills in a seeded spiral, one step out per city
    // already standing there
    if(!placed) {
        var goldenAngle = Math.PI * (3 - Math.sqrt(5));
        var spiralIdx = continent.cities.length;

        var spiralAngle = seed + spiralIdx * goldenAngle;
        var spiralReach = config.cityGap * 0.7 * Math.sqrt(spiralIdx + 1);

        cityX = continent.labelX + Math.cos(spiralAngle) * spiralReach;
        cityY = continent.labelY + Math.sin(spiralAngle) * spiralReach;
    }

    return {name: name, x: cityX, y: cityY};
};

// /////////////////////////////////////////////////////////////////////////////

// The whole world out of the inventory - every type's ground walked out,
// the families laid out and placed, the field sampled over everything, the
// waterline drawn, then the cities onto the ground the field says is there
geography.build = function(inventory, width, height) {
    var config = geography.config;
    var field = $.fn.zato.weather_map.field;

    // Each type's share of the land, by how many connections it holds -
    // the exponent spreads the shares apart, so the busiest types stand
    // as dominant continents rather than as equals among blobs
    var weights = [];
    var weightSum = 0;

    for(var weightIdx = 0; weightIdx < inventory.length; weightIdx++) {
        var weight = Math.pow(inventory[weightIdx].objects.length + 2, config.massDominance);

        weights.push(weight);
        weightSum += weight;
    }

    var totalLand = config.landFraction * width * height;

    var landSets = [];

    for(var setIdx = 0; setIdx < inventory.length; setIdx++) {
        var mass = totalLand * weights[setIdx] / weightSum;

        landSets.push(geography.buildLand(inventory[setIdx].source, mass));
    }

    var groups = geography.buildGroups(inventory);

    // The biggest families claim their waters first
    for(var weighIdx = 0; weighIdx < groups.length; weighIdx++) {
        var weighed = groups[weighIdx];

        weighed.totalRadius = 0;

        for(var weighMemberIdx = 0; weighMemberIdx < weighed.entryIdxs.length; weighMemberIdx++) {
            weighed.totalRadius += landSets[weighed.entryIdxs[weighMemberIdx]].radius;
        }
    }

    groups.sort(function(first, second) {
        return second.totalRadius - first.totalRadius;
    });

    // One seed for the whole layout, off the types alone, so a new
    // connection of an existing type keeps the world where it stands
    var seedParts = [];

    for(var seedIdx = 0; seedIdx < inventory.length; seedIdx++) {
        seedParts.push(inventory[seedIdx].source);
    }

    var layoutSeed = geography.hashText(seedParts.join('|'));
    var layoutRandom = geography.makeRandom(layoutSeed);

    var edgePad = field.edgeMargin(width, height) + config.edgePad;

    var continents = [];
    var ridges = [];
    var placedBounds = [];

    // The one great ocean is claimed before any land - a phantom bound the
    // placement respects, so the world keeps one long open basin the way a
    // planet keeps its Pacific
    var oceanAngle = layoutRandom() * Math.PI * 2;
    var oceanReach = Math.min(width, height) * config.oceanReserveOffset;
    var oceanRadius = Math.min(width, height) * config.oceanReserveFraction;

    placedBounds.push({
        centerX: width / 2 + Math.cos(oceanAngle) * oceanReach,
        centerY: height / 2 + Math.sin(oceanAngle) * oceanReach,
        radius: oceanRadius
    });

    var anchorBound = null;

    for(var groupIdx = 0; groupIdx < groups.length; groupIdx++) {
        var group = groups[groupIdx];

        var memberRadii = [];

        for(var radiusIdx = 0; radiusIdx < group.entryIdxs.length; radiusIdx++) {
            memberRadii.push(landSets[group.entryIdxs[radiusIdx]].radius);
        }

        // The family's inner shape holds still whatever the other
        // families do - its own key seeds it
        var memberRandom = geography.makeRandom(geography.hashText(group.key));
        var positions = geography.layoutMembers(memberRadii, memberRandom);

        // The dominant mass anchors the composition, the runner-up stands
        // across the water from it, the rest fill in what is left
        var role = 'filler';

        if(groupIdx === 0) {
            role = 'anchor';
        }
        else if(groupIdx === 1) {
            role = 'counterweight';
        }

        var bound = geography.boundingCircle(positions, memberRadii);
        var spot = geography.placeGroup(placedBounds, bound.radius, width, height, layoutRandom, edgePad, role, anchorBound);

        placedBounds.push({centerX: spot.centerX, centerY: spot.centerY, radius: bound.radius});

        if(groupIdx === 0) {
            anchorBound = {centerX: spot.centerX, centerY: spot.centerY};
        }

        for(var memberIdx = 0; memberIdx < group.entryIdxs.length; memberIdx++) {

            var entry = inventory[group.entryIdxs[memberIdx]];
            var landSet = landSets[group.entryIdxs[memberIdx]];

            var continentX = spot.centerX + positions[memberIdx].x - bound.centerX;
            var continentY = spot.centerY + positions[memberIdx].y - bound.centerY;

            // The walk's chunks follow their continent to its final spot,
            // and so do the basins carved into them
            var stamps = [];

            for(var stampIdx = 0; stampIdx < landSet.stamps.length; stampIdx++) {
                var stamp = landSet.stamps[stampIdx];

                stamps.push({
                    x: continentX + stamp.x,
                    y: continentY + stamp.y,
                    radius: stamp.radius,
                    height: stamp.height
                });
            }

            var basins = [];

            for(var basinIdx = 0; basinIdx < landSet.basins.length; basinIdx++) {
                var basin = landSet.basins[basinIdx];

                basins.push({
                    x: continentX + basin.x,
                    y: continentY + basin.y,
                    radius: basin.radius,
                    strength: basin.strength
                });
            }

            // A landmass may carry a rifted margin - seeded off its own
            // name, the tear line and the straight coast it leaves survive
            // any relayout
            var riftRandom = geography.makeRandom(geography.hashText('rift|' + entry.source));
            var rift = null;

            if(riftRandom() < config.riftChance) {

                var riftAngle = riftRandom() * Math.PI * 2;
                var riftOffset = landSet.radius * (config.riftOffsetMin + riftRandom() * config.riftOffsetSpan);

                rift = {
                    originX: continentX + Math.cos(riftAngle) * riftOffset,
                    originY: continentY + Math.sin(riftAngle) * riftOffset,
                    normalX: Math.cos(riftAngle),
                    normalY: Math.sin(riftAngle)
                };
            }

            continents.push({
                source: entry.source,
                label: entry.label,
                objects: entry.objects,
                centerX: continentX,
                centerY: continentY,
                radius: landSet.radius,
                stamps: stamps,
                basins: basins,
                rift: rift,
                labelX: 0,
                labelY: 0,
                cities: []
            });

            // The suture with the neighbour this member was chained onto
            // carries a collision belt - the mountains of the fused pair
            if(memberIdx) {
                var neighbour = continents[continents.length - 2];
                var member = continents[continents.length - 1];

                var belt = geography.buildRidge(
                    neighbour.source, member.source,
                    {x: neighbour.centerX, y: neighbour.centerY},
                    {x: member.centerX, y: member.centerY},
                    neighbour.radius, member.radius);

                for(var beltIdx = 0; beltIdx < belt.length; beltIdx++) {
                    ridges.push(belt[beltIdx]);
                }
            }
        }
    }

    // The scatter - island arcs off the biggest continents' flanks and
    // hotspot chains out in the open water, the great ocean included
    geography.scatterArcs(continents);
    geography.scatterHotspots(continents, placedBounds.slice(1), width, height, layoutSeed);

    var grid = field.build(continents, ridges, width, height, layoutSeed, config.landFraction);

    var model = {continents: continents, ridges: ridges, grid: grid, width: width, height: height};

    // Each name goes where the type's land actually gathered - a type whose
    // ground fused into a neighbour still names its own share of it
    for(var labelIdx = 0; labelIdx < continents.length; labelIdx++) {
        var continent = continents[labelIdx];

        if(grid.landCells[labelIdx]) {
            continent.labelX = grid.centroidX[labelIdx];
            continent.labelY = grid.centroidY[labelIdx];
        }
        else {
            continent.labelX = continent.centerX;
            continent.labelY = continent.centerY;
        }
    }

    for(var cityContinentIdx = 0; cityContinentIdx < continents.length; cityContinentIdx++) {
        var cityContinent = continents[cityContinentIdx];

        for(var objectIdx = 0; objectIdx < cityContinent.objects.length; objectIdx++) {
            var city = geography.placeCity(model, cityContinentIdx, cityContinent.objects[objectIdx]);
            cityContinent.cities.push(city);
        }
    }

    return model;
};

// /////////////////////////////////////////////////////////////////////////////

// What stands under one point - the nearest city when one is close enough,
// else the ground itself, else open water
geography.hitAt = function(model, pointX, pointY, cityRadius) {
    var field = $.fn.zato.weather_map.field;

    var bestCity = null;
    var bestContinent = null;
    var bestDistance = cityRadius;

    for(var continentIdx = 0; continentIdx < model.continents.length; continentIdx++) {
        var continent = model.continents[continentIdx];

        for(var cityIdx = 0; cityIdx < continent.cities.length; cityIdx++) {
            var city = continent.cities[cityIdx];

            var deltaX = pointX - city.x;
            var deltaY = pointY - city.y;
            var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            if(distance < bestDistance) {
                bestDistance = distance;
                bestCity = city;
                bestContinent = continent;
            }
        }
    }

    if(bestCity) {
        return {kind: 'city', city: bestCity, continent: bestContinent};
    }

    var elevation = field.sample(model.grid, pointX, pointY);

    if(elevation >= model.grid.seaLevel) {
        var ownerIdx = field.ownerAt(model.grid, pointX, pointY);

        if(ownerIdx >= 0) {
            return {kind: 'continent', continent: model.continents[ownerIdx], continentIdx: ownerIdx};
        }
    }

    return null;
};

// /////////////////////////////////////////////////////////////////////////////

})();
