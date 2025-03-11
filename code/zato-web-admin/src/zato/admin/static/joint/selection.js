// selection.js - Element selection functionality

class Selection {
    constructor(graph, paper) {
        this.graph = graph;
        this.paper = paper;
        this.cells = [];
        this.box = null;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Selection handling
        let selecting = false;
        let startX, startY;

        this.paper.on('blank:pointerdown', (evt, x, y) => {
            // Only start selection if not in panning mode
            if (!isPanning) {
                selecting = true;
                startX = evt.clientX;
                startY = evt.clientY;
                this.createSelectionBox();
            }
        });

        document.addEventListener('mousemove', (evt) => {
            if (selecting) {
                this.updateSelectionBox(startX, startY, evt.clientX, evt.clientY);
            }
        });

        document.addEventListener('mouseup', (evt) => {
            if (selecting) {
                selecting = false;
                this.selectElements(startX, startY, evt.clientX, evt.clientY);
                this.removeSelectionBox();
            }
        });

        // Handle element selection with click
        this.paper.on('element:pointerclick', (elementView, evt) => {
            const element = elementView.model;
            this.toggle(element, evt.ctrlKey);
        });

        // Clear selection when clicking on blank area
        this.paper.on('blank:pointerclick', () => {
            this.clear();
        });

        // Add keyboard shortcuts
        document.addEventListener('keydown', (evt) => {
            // Ctrl+A to select all
            if (evt.ctrlKey && evt.key === 'a') {
                evt.preventDefault();
                this.selectAll();
            }

            // Delete or Backspace to remove selected elements
            if ((evt.key === 'Delete' || evt.key === 'Backspace') && this.cells.length > 0) {
                evt.preventDefault();
                this.removeSelected();
            }
        });
    }

    // Create rubberband selection box
    createSelectionBox() {
        this.box = document.createElement('div');
        this.box.style.position = 'absolute';
        this.box.style.border = '1px dashed blue';
        this.box.style.backgroundColor = 'rgba(0, 0, 255, 0.1)';
        this.box.style.pointerEvents = 'none';
        document.querySelector('.main-content').appendChild(this.box);
    }

    // Update rubberband position and size
    updateSelectionBox(x1, y1, x2, y2) {
        if (!this.box) this.createSelectionBox();

        const left = Math.min(x1, x2);
        const top = Math.min(y1, y2);
        const width = Math.abs(x2 - x1);
        const height = Math.abs(y2 - y1);

        this.box.style.left = left + 'px';
        this.box.style.top = top + 'px';
        this.box.style.width = width + 'px';
        this.box.style.height = height + 'px';
        this.box.style.display = 'block';
    }

    // Remove the rubberband
    removeSelectionBox() {
        if (this.box && this.box.parentNode) {
            this.box.parentNode.removeChild(this.box);
            this.box = null;
        }
    }

    // Select elements inside the selection box
    selectElements(x1, y1, x2, y2) {
        const paperOffset = this.paper.el.getBoundingClientRect();
        const localX1 = x1 - paperOffset.left;
        const localY1 = y1 - paperOffset.top;
        const localX2 = x2 - paperOffset.left;
        const localY2 = y2 - paperOffset.top;

        // Convert to paper coordinates
        const scale = this.paper.scale();
        const p1 = this.paper.clientToLocalPoint({ x: localX1, y: localY1 });
        const p2 = this.paper.clientToLocalPoint({ x: localX2, y: localY2 });

        // Create selection rectangle
        const rect = {
            x: Math.min(p1.x, p2.x),
            y: Math.min(p1.y, p2.y),
            width: Math.abs(p2.x - p1.x),
            height: Math.abs(p2.y - p1.y)
        };

        // Find elements inside the rectangle
        const elements = this.graph.getElements().filter(function(el) {
            const bbox = el.getBBox();
            return (
                bbox.x >= rect.x &&
                bbox.x + bbox.width <= rect.x + rect.width &&
                bbox.y >= rect.y &&
                bbox.y + bbox.height <= rect.y + rect.height
            );
        });

        // Select elements
        this.clear();
        elements.forEach(this.add.bind(this));
    }

    // Add element to selection
    add(element) {
        if (!element || this.cells.indexOf(element) > -1) return;
        this.cells.push(element);
        this.highlight(element);
    }

    // Remove element from selection
    remove(element) {
        const index = this.cells.indexOf(element);
        if (index === -1) return;
        this.cells.splice(index, 1);
        this.unhighlight(element);
    }

    // Clear all selections
    clear() {
        this.cells.forEach(this.unhighlight.bind(this));
        this.cells = [];
    }

    // Toggle element selection
    toggle(element, ctrlKey) {
        if (!element) return;

        if (!ctrlKey) {
            // If ctrl is not pressed, clear selection and select just this element
            this.clear();
            this.add(element);
        } else {
            // If ctrl is pressed, toggle the element's selection
            const index = this.cells.indexOf(element);
            if (index === -1) {
                this.add(element);
            } else {
                this.remove(element);
            }
        }
    }

    // Select all elements
    selectAll() {
        this.clear();
        this.graph.getElements().forEach(this.add.bind(this));
    }

    // Remove selected elements
    removeSelected() {
        if (this.cells.length > 0 && confirm('Are you sure you want to delete the selected elements?')) {
            const toRemove = [...this.cells]; // Create a copy since removal will modify the array
            toRemove.forEach(element => element.remove());
            this.cells = []; // Clear the selection after removal
        }
    }

    // Highlight selected element
    highlight(element) {
        const view = element.findView(this.paper);
        if (view) {
            view.highlight(null, {
                highlighter: {
                    name: 'stroke',
                    options: {
                        padding: 8,
                        attrs: {
                            'stroke': '#2196F3',
                            'stroke-width': 2,
                            'stroke-dasharray': '5,5'
                        }
                    }
                }
            });
        }
    }

    // Remove highlight from element
    unhighlight(element) {
        const view = element.findView(this.paper);
        if (view) view.unhighlight();
    }
}

// Global variable to track panning state
var isPanning = false;
