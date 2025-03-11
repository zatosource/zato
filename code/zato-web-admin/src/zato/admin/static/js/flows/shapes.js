// shapes.js - Custom shape definitions for workflow elements

function initializeCustomShapes() {
    // Custom shapes for workflow elements

    // Task shape (rectangle)
    joint.shapes.workflow = {};
    joint.shapes.workflow.Task = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Task',
            size: { width: 120, height: 60 },
            attrs: {
                body: {
                    fill: '#FFFFFF',
                    stroke: '#5F95FF',
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4
                },
                label: {
                    text: 'Service',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Rectangle.prototype.defaults)
    });

    // Process shape (rectangle with different styling)
    joint.shapes.workflow.Process = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Process',
            size: { width: 120, height: 60 },
            attrs: {
                body: {
                    fill: '#FFFFFF',
                    stroke: '#813d9c',
                    strokeWidth: 2,
                    rx: 0,
                    ry: 0
                },
                label: {
                    text: 'Split / Join',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Rectangle.prototype.defaults)
    });

    // Decision shape (diamond)
    joint.shapes.workflow.Decision = joint.shapes.standard.Polygon.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Decision',
            size: { width: 120, height: 80 },
            attrs: {
                body: {
                    refPoints: '0,10 10,0 20,10 10,20',
                    fill: '#FFFFFF',
                    stroke: '#FF8C00',
                    strokeWidth: 2
                },
                label: {
                    text: 'Decision',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Polygon.prototype.defaults)
    });

    // Start shape (circle)
    joint.shapes.workflow.Start = joint.shapes.standard.Circle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Start',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    fill: '#FFFFFF',
                    stroke: '#2ECC71',
                    strokeWidth: 2
                },
                label: {
                    text: 'Start',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Circle.prototype.defaults)
    });

    // End shape (circle with different styling)
    joint.shapes.workflow.End = joint.shapes.standard.Circle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.End',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    fill: '#FFFFFF',
                    stroke: '#E74C3C',
                    strokeWidth: 2
                },
                label: {
                    text: 'End',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Circle.prototype.defaults)
    });

    // Timer shape (circle with clock icon)
    joint.shapes.workflow.Timer = joint.shapes.standard.Circle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Timer',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    fill: '#FFFFFF',
                    stroke: '#9B59B6',
                    strokeWidth: 2
                },
                label: {
                    text: 'Timer',
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 14,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Circle.prototype.defaults)
    });
}
