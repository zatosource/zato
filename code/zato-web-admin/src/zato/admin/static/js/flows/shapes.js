// shapes.js - Custom shape definitions for workflow elements

function initializeCustomShapes() {
    // Custom shapes for workflow elements
    joint.shapes.workflow = {};

    // Start shape (octagonal)
    joint.shapes.workflow.Start = joint.shapes.standard.Path.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Start',
            size: { width: 80, height: 80 },  // Increased size to accommodate internal labels
            attrs: {
                body: {
                    refD: 'M 20,0 L 60,0 L 80,20 L 80,60 L 60,80 L 20,80 L 0,60 L 0,20 Z', // Octagon shape
                    fill: '#DBEAFF',
                    stroke: '#0062FF',
                    strokeWidth: 2
                },
                label: {
                    text: 'Start',
                    fill: '#0043CE',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Path.prototype.defaults)
    });

    // Stop shape (octagonal)
    joint.shapes.workflow.Stop = joint.shapes.standard.Path.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Stop',
            size: { width: 80, height: 80 },  // Increased size to accommodate internal labels
            attrs: {
                body: {
                    refD: 'M 20,0 L 60,0 L 80,20 L 80,60 L 60,80 L 20,80 L 0,60 L 0,20 Z', // Octagon shape
                    fill: '#ECEAF4',
                    stroke: '#79709C',
                    strokeWidth: 2
                },
                label: {
                    text: 'Stop',
                    fill: '#43337C',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Path.prototype.defaults)
    });

    // Service shape (rectangle)
    joint.shapes.workflow.Service = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Service',
            size: { width: 140, height: 60 },  // Increased width to accommodate internal labels
            attrs: {
                body: {
                    fill: '#E9F3FE',
                    stroke: '#0F5F99',
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4
                },
                label: {
                    text: 'Service',
                    fill: '#0F5F99',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Rectangle.prototype.defaults)
    });

    // Parallel shape (rectangle with different color)
    joint.shapes.workflow.Parallel = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Parallel',
            size: { width: 140, height: 80 },  // Increased dimensions for internal labels
            attrs: {
                body: {
                    fill: '#FFF7E6',
                    stroke: '#C87533',
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4
                },
                label: {
                    text: 'Parallel',
                    fill: '#703F00',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Rectangle.prototype.defaults)
    });

    // ForkJoin shape (rectangle with different color)
    joint.shapes.workflow.ForkJoin = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.ForkJoin',
            size: { width: 140, height: 80 },  // Increased dimensions for internal labels
            attrs: {
                body: {
                    fill: '#F0F7DA',
                    stroke: '#4F6700',
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4
                },
                label: {
                    text: 'Fork/Join',
                    fill: '#4F6700',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Rectangle.prototype.defaults)
    });
}
