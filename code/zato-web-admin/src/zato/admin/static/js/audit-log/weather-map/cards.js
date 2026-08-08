
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the card. One translucent panel floats over the map and
// reads whatever the pointer rests on or a click pinned - a city with its
// type, a continent with its count - and leads into the audit log and the
// object's own configuration page.

$.fn.zato.weather_map.cards = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var cards = $.fn.zato.weather_map.cards;

// /////////////////////////////////////////////////////////////////////////////

cards.config = {

    // How far from its anchor the card stands
    offset: 18,

    // How close to the frame's edge the card may get
    edgePadding: 12,

    words: {
        showLog: 'Show log',
        configuration: 'Configuration',
        connectionSingular: 'connection',
        connectionPlural: 'connections'
    }
};

// /////////////////////////////////////////////////////////////////////////////

// What the page handed over on init - the links and the elements the card
// writes itself into
cards.page = null;
cards.frame = null;
cards.element = null;

// /////////////////////////////////////////////////////////////////////////////

cards.init = function(page, frame, element) {
    cards.page = page;
    cards.frame = frame;
    cards.element = element;
};

// /////////////////////////////////////////////////////////////////////////////

// Where the audit log opens for one source, and for one object of it
cards.showLogURL = function(source, objectName) {
    var out = cards.page.auditLogPage;
    out += '?source=' + encodeURIComponent(source);

    if(objectName) {
        out += '&object_name=' + encodeURIComponent(objectName);
    }

    out += '&cluster=' + cards.page.clusterId;

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

cards.addLink = function(row, label, href) {
    var link = document.createElement('a');
    link.className = 'weather-map-card-link';
    link.textContent = label;
    link.href = href;

    row.appendChild(link);
};

// /////////////////////////////////////////////////////////////////////////////

// The card's contents for one hit - the title, one line saying what it is,
// and the links out
cards.fill = function(hit) {
    var words = cards.config.words;
    var element = cards.element;

    element.textContent = '';

    var title = document.createElement('div');
    title.className = 'weather-map-card-title';

    var detail = document.createElement('div');
    detail.className = 'weather-map-card-detail';

    var links = document.createElement('div');
    links.className = 'weather-map-card-links';

    if(hit.kind === 'city') {

        title.textContent = hit.city.name;
        detail.textContent = hit.continent.label;

        var showLogURL = cards.showLogURL(hit.continent.source, hit.city.name);
        cards.addLink(links, words.showLog, showLogURL);

        var objectLink = cards.page.objectLinks[hit.continent.source];
        var configurationURL = objectLink.replace('{name}', encodeURIComponent(hit.city.name));
        cards.addLink(links, words.configuration, configurationURL);
    }
    else {

        var count = hit.continent.cities.length;
        var countWord = count === 1 ? words.connectionSingular : words.connectionPlural;

        title.textContent = hit.continent.label;
        detail.textContent = count + ' ' + countWord;

        cards.addLink(links, words.showLog, cards.showLogURL(hit.continent.source, ''));
        cards.addLink(links, words.configuration, cards.page.sourceLinks[hit.continent.source]);
    }

    element.appendChild(title);
    element.appendChild(detail);
    element.appendChild(links);
};

// /////////////////////////////////////////////////////////////////////////////

// The card near its anchor, held inside the frame whatever corner the
// anchor sits in
cards.show = function(hit, anchorX, anchorY) {
    var config = cards.config;

    cards.fill(hit);

    var element = cards.element;
    element.className = 'weather-map-card weather-map-card-visible';

    var frameWidth = cards.frame.clientWidth;
    var frameHeight = cards.frame.clientHeight;

    var cardWidth = element.offsetWidth;
    var cardHeight = element.offsetHeight;

    var left = anchorX + config.offset;
    var top = anchorY + config.offset;

    if(left + cardWidth > frameWidth - config.edgePadding) {
        left = anchorX - config.offset - cardWidth;
    }
    if(top + cardHeight > frameHeight - config.edgePadding) {
        top = anchorY - config.offset - cardHeight;
    }

    if(left < config.edgePadding) {
        left = config.edgePadding;
    }
    if(top < config.edgePadding) {
        top = config.edgePadding;
    }

    element.style.left = left + 'px';
    element.style.top = top + 'px';
};

// /////////////////////////////////////////////////////////////////////////////

cards.hide = function() {
    cards.element.className = 'weather-map-card';
};

// /////////////////////////////////////////////////////////////////////////////

})();
