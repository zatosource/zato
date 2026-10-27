zatoPortal.sidebar = {};

zatoPortal.sidebar.config = {
    workspaceId: 'portal-workspace',
    sidebarId: 'portal-sidebar',
    toggleId: 'portal-sidebar-toggle',
    resizerId: 'portal-sidebar-resizer',
    filterId: 'portal-filter',
    clearId: 'portal-filter-clear',
    collapsedClass: 'portal-workspace portal-sidebar-collapsed',
    expandedClass: 'portal-workspace',
    resizingClass: 'portal-body portal-resizing',
    idleClass: 'portal-body',
    collapseLabel: 'Collapse',
    expandLabel: 'Expand',
    resizeLabel: 'Resize',
    collapsedStorageKey: 'zato.openapi.portal.sidebar.collapsed',
    widthStorageKey: 'zato.openapi.portal.sidebar.width',
    collapsedValue: '1',
    expandedValue: '0',
    widthVariable: '--portal-sidebar-width',
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
    iconCollapseClass: 'portal-sidebar-icon portal-sidebar-icon-collapse',
    iconExpandClass: 'portal-sidebar-icon portal-sidebar-icon-expand',
};

zatoPortal.sidebar.drag = {
    isDragging: false,
    startX: 0,
    startWidth: 0,
    width: 0,
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.init = function() {

    var config = zatoPortal.sidebar.config;

    var toggle = document.getElementById(config.toggleId);
    var resizer = document.getElementById(config.resizerId);
    var filter = document.getElementById(config.filterId);
    var clear = document.getElementById(config.clearId);

    var collapseIcon = zatoPortal.sidebar.buildIcon(config.iconCollapseChevron, config.iconCollapseClass);
    var expandIcon = zatoPortal.sidebar.buildIcon(config.iconExpandChevron, config.iconExpandClass);

    toggle.appendChild(collapseIcon);
    toggle.appendChild(expandIcon);
    toggle.addEventListener('click', zatoPortal.sidebar.onToggleClick);

    resizer.setAttribute('role', 'separator');
    resizer.setAttribute('aria-orientation', 'vertical');
    resizer.setAttribute('aria-label', config.resizeLabel);
    resizer.addEventListener('pointerdown', zatoPortal.sidebar.onPointerDown);
    resizer.addEventListener('pointermove', zatoPortal.sidebar.onPointerMove);
    resizer.addEventListener('pointerup', zatoPortal.sidebar.onPointerUp);
    resizer.addEventListener('pointercancel', zatoPortal.sidebar.onPointerUp);

    filter.addEventListener('input', zatoPortal.sidebar.onFilterInput);
    clear.addEventListener('click', zatoPortal.sidebar.onClearClick);

    // The width and the collapsed state of an earlier visit apply before the workspace is first shown.
    // localStorage returns null for a key that was never stored.
    var storedWidth = localStorage.getItem(config.widthStorageKey);

    if(storedWidth !== null) {
        document.documentElement.style.setProperty(config.widthVariable, storedWidth + config.widthUnit);
    }

    var storedCollapsed = localStorage.getItem(config.collapsedStorageKey);
    zatoPortal.sidebar.applyCollapsed(storedCollapsed === config.collapsedValue);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.buildIcon = function(chevron, className) {

    var config = zatoPortal.sidebar.config;
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

zatoPortal.sidebar.applyCollapsed = function(isCollapsed) {

    var config = zatoPortal.sidebar.config;

    var workspace = document.getElementById(config.workspaceId);
    var toggle = document.getElementById(config.toggleId);
    var label = isCollapsed ? config.expandLabel : config.collapseLabel;

    workspace.className = isCollapsed ? config.collapsedClass : config.expandedClass;

    toggle.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.onToggleClick = function() {

    var config = zatoPortal.sidebar.config;
    var stored = localStorage.getItem(config.collapsedStorageKey);
    var isCollapsed = stored !== config.collapsedValue;

    zatoPortal.sidebar.applyCollapsed(isCollapsed);
    localStorage.setItem(config.collapsedStorageKey, isCollapsed ? config.collapsedValue : config.expandedValue);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.onPointerDown = function(event) {

    var config = zatoPortal.sidebar.config;
    var drag = zatoPortal.sidebar.drag;

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

zatoPortal.sidebar.onPointerMove = function(event) {

    var config = zatoPortal.sidebar.config;
    var drag = zatoPortal.sidebar.drag;

    if(!drag.isDragging) {
        return;
    }

    var requested = drag.startWidth + event.clientX - drag.startX;
    var atLeastMinimum = Math.max(config.widthMinimum, requested);

    drag.width = Math.min(config.widthMaximum, atLeastMinimum);
    document.documentElement.style.setProperty(config.widthVariable, drag.width + config.widthUnit);
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.onPointerUp = function(event) {

    var config = zatoPortal.sidebar.config;
    var drag = zatoPortal.sidebar.drag;

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

zatoPortal.sidebar.onFilterInput = function(event) {

    var clear = document.getElementById(zatoPortal.sidebar.config.clearId);
    clear.hidden = event.target.value === '';
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.onClearClick = function() {

    var filter = document.getElementById(zatoPortal.sidebar.config.filterId);

    // The filter is cleared the same way typing changes it, so the navigation and the clear button both follow
    filter.value = '';
    filter.dispatchEvent(new Event('input'));
    filter.focus();
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.sidebar.init();
