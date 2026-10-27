zatoApp.sidebar = {};

zatoApp.sidebar.config = {
    workspaceId: 'app-workspace',
    sidebarId: 'app-sidebar',
    toggleId: 'app-sidebar-toggle',
    resizerId: 'app-sidebar-resizer',
    filterId: 'app-filter',
    clearId: 'app-filter-clear',
    collapsedClass: 'app-workspace app-sidebar-collapsed',
    expandedClass: 'app-workspace',
    resizingClass: 'app-body app-resizing',
    idleClass: 'app-body',
    collapseLabel: 'Collapse',
    expandLabel: 'Expand',
    resizeLabel: 'Resize',
    collapsedStorageKey: 'zato.openapi.app.sidebar.collapsed',
    widthStorageKey: 'zato.openapi.app.sidebar.width',
    collapsedValue: '1',
    expandedValue: '0',
    widthVariable: '--app-sidebar-width',
    widthUnit: 'px',
    widthMinimum: 220,
    widthMaximum: 560,
    primaryButton: 0,
    svgNamespace: 'http://www.w3.org/2000/svg',
    iconViewBox: '0 0 24 24',
    iconFrame: 'M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z',
    iconDivider: 'M9 3v18',
    iconCollapseChevron: 'm16 15-3-3 3-3',
    iconExpandChevron: 'm14 9 3 3-3 3',
    iconCollapseClass: 'app-sidebar-icon app-sidebar-icon-collapse',
    iconExpandClass: 'app-sidebar-icon app-sidebar-icon-expand',
};

zatoApp.sidebar.drag = {
    isDragging: false,
    startX: 0,
    startWidth: 0,
    width: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.init = function() {

    var config = zatoApp.sidebar.config;

    var toggle = document.getElementById(config.toggleId);
    var resizer = document.getElementById(config.resizerId);
    var filter = document.getElementById(config.filterId);
    var clear = document.getElementById(config.clearId);

    var collapseIcon = zatoApp.sidebar.buildIcon(config.iconCollapseChevron, config.iconCollapseClass);
    var expandIcon = zatoApp.sidebar.buildIcon(config.iconExpandChevron, config.iconExpandClass);

    toggle.appendChild(collapseIcon);
    toggle.appendChild(expandIcon);
    toggle.addEventListener('click', zatoApp.sidebar.onToggleClick);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'vertical');
    resizer.setAttribute('aria-label', config.resizeLabel);
    resizer.addEventListener('pointerdown', zatoApp.sidebar.onPointerDown);
    resizer.addEventListener('pointermove', zatoApp.sidebar.onPointerMove);
    resizer.addEventListener('pointerup', zatoApp.sidebar.onPointerUp);
    resizer.addEventListener('pointercancel', zatoApp.sidebar.onPointerUp);

    filter.addEventListener('input', zatoApp.sidebar.onFilterInput);
    clear.addEventListener('click', zatoApp.sidebar.onClearClick);

    // The width and the collapsed state of an earlier visit apply before the workspace is first shown.
    // localStorage returns null for a key that was never stored.
    var storedWidth = localStorage.getItem(config.widthStorageKey);

    if(storedWidth !== null) {
        document.documentElement.style.setProperty(config.widthVariable, storedWidth + config.widthUnit);
    }

    var storedCollapsed = localStorage.getItem(config.collapsedStorageKey);
    zatoApp.sidebar.applyCollapsed(storedCollapsed === config.collapsedValue);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.buildIcon = function(chevron, className) {

    var config = zatoApp.sidebar.config;
    var shapes = [config.iconFrame, config.iconDivider, chevron];

    var icon = document.createElementNS(config.svgNamespace, 'svg');
    icon.setAttribute('class', className);
    icon.setAttribute('viewBox', config.iconViewBox);

    for(var shapeIndex = 0; shapeIndex < shapes.length; shapeIndex++) {
        var path = document.createElementNS(config.svgNamespace, 'path');
        path.setAttribute('d', shapes[shapeIndex]);
        icon.appendChild(path);
    }

    return icon;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.applyCollapsed = function(isCollapsed) {

    var config = zatoApp.sidebar.config;

    var workspace = document.getElementById(config.workspaceId);
    var toggle = document.getElementById(config.toggleId);
    var label = isCollapsed ? config.expandLabel : config.collapseLabel;

    workspace.className = isCollapsed ? config.collapsedClass : config.expandedClass;

    toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onToggleClick = function() {

    var config = zatoApp.sidebar.config;
    var stored = localStorage.getItem(config.collapsedStorageKey);
    var isCollapsed = stored !== config.collapsedValue;

    zatoApp.sidebar.applyCollapsed(isCollapsed);
    localStorage.setItem(config.collapsedStorageKey, isCollapsed ? config.collapsedValue : config.expandedValue);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onPointerDown = function(event) {

    var config = zatoApp.sidebar.config;
    var drag = zatoApp.sidebar.drag;

    // Only the primary button starts a drag ..
    if(event.button !== config.primaryButton) {
        return;
    }

    // .. no text is selected while the pointer crosses the page ..
    event.preventDefault();

    var sidebar = document.getElementById(config.sidebarId);

    drag.isDragging = true;
    drag.startX = event.clientX;
    drag.startWidth = sidebar.getBoundingClientRect().width;
    drag.width = drag.startWidth;

    // .. and capturing the pointer keeps the drag going when it leaves the thin edge.
    event.currentTarget.setPointerCapture(event.pointerId);
    document.body.className = config.resizingClass;
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onPointerMove = function(event) {

    var config = zatoApp.sidebar.config;
    var drag = zatoApp.sidebar.drag;

    if(!drag.isDragging) {
        return;
    }

    var requested = drag.startWidth + event.clientX - drag.startX;
    var atLeastMinimum = Math.max(config.widthMinimum, requested);

    drag.width = Math.min(config.widthMaximum, atLeastMinimum);
    document.documentElement.style.setProperty(config.widthVariable, drag.width + config.widthUnit);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onPointerUp = function(event) {

    var config = zatoApp.sidebar.config;
    var drag = zatoApp.sidebar.drag;

    if(!drag.isDragging) {
        return;
    }

    drag.isDragging = false;

    event.currentTarget.releasePointerCapture(event.pointerId);
    document.body.className = config.idleClass;

    var width = Math.round(drag.width);
    localStorage.setItem(config.widthStorageKey, width);
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onFilterInput = function(event) {

    var clear = document.getElementById(zatoApp.sidebar.config.clearId);
    clear.hidden = event.target.value === '';
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.onClearClick = function() {

    var filter = document.getElementById(zatoApp.sidebar.config.filterId);

    // The filter is cleared the same way typing changes it, so the navigation and the clear button both follow
    filter.value = '';
    filter.dispatchEvent(new Event('input'));
    filter.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoApp.sidebar.init();
