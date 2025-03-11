// shapes.js - Custom shape definitions for workflow elements

function initializeCustomShapes() {
    // Custom shapes for workflow elements
    joint.shapes.workflow = {};

    // Start shape (octagonal)
    joint.shapes.workflow.Start = joint.shapes.standard.Path.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Start',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    refD: 'M 15,0 L 45,0 L 60,15 L 60,45 L 45,60 L 15,60 L 0,45 L 0,15 Z', // Octagon shape
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
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    refD: 'M 15,0 L 45,0 L 60,15 L 60,45 L 45,60 L 15,60 L 0,45 L 0,15 Z', // Octagon shape
                    fill: '#FFE2E2',
                    stroke: '#DA1E28',
                    strokeWidth: 2
                },
                label: {
                    text: 'Stop',
                    fill: '#750E13',
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
            size: { width: 120, height: 50 },
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

    // Parallel shape (rectangle with different styling)
    joint.shapes.workflow.Parallel = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Parallel',
            size: { width: 120, height: 50 },
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

    // Fork/Join shape (rectangle with different styling)
    joint.shapes.workflow.ForkJoin = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.ForkJoin',
            size: { width: 120, height: 50 },
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
