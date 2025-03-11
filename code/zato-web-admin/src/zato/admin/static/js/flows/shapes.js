// shapes.js - Custom shape definitions for workflow elements with Flows styling

function initializeCustomShapes() {
    // Custom shapes for workflow elements

    // Task shape (rectangle with Flows styling)
    joint.shapes.workflow = {};
    joint.shapes.workflow.Task = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Task',
            size: { width: 120, height: 50 },
            attrs: {
                body: {
                    fill: '#E9F3FE',
                    stroke: '#0F5F99',
                    strokeWidth: 2,
                    rx: 3,
                    ry: 3
                },
                label: {
                    text: 'Compute',
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

    // Process shape (Flows Transform node)
    joint.shapes.workflow.Process = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Process',
            size: { width: 120, height: 50 },
            attrs: {
                body: {
                    fill: '#FFF7E6',
                    stroke: '#C87533',
                    strokeWidth: 2,
                    rx: 0,
                    ry: 0
                },
                label: {
                    text: 'Transform',
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

    // Decision shape (diamond - filter node in Flows)
    joint.shapes.workflow.Decision = joint.shapes.standard.Polygon.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Decision',
            size: { width: 100, height: 70 },
            attrs: {
                body: {
                    refPoints: '0,10 10,0 20,10 10,20',
                    fill: '#FFF0F5',
                    stroke: '#9932CC',
                    strokeWidth: 2
                },
                label: {
                    text: 'Filter',
                    fill: '#4B0082',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Polygon.prototype.defaults)
    });

    // Start shape (Flows Input node)
    joint.shapes.workflow.Start = joint.shapes.standard.Path.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Start',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    refD: 'M 0,20 L 20,0 L 40,0 L 60,20 L 60,40 L 40,60 L 20,60 L 0,40 Z', // Octagon shape
                    fill: '#DBEAFF',
                    stroke: '#0062FF',
                    strokeWidth: 2
                },
                label: {
                    text: 'Input',
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

    // End shape (Flows Output node)
    joint.shapes.workflow.End = joint.shapes.standard.Path.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.End',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    refD: 'M 0,20 L 20,0 L 40,0 L 60,20 L 60,40 L 40,60 L 20,60 L 0,40 Z', // Octagon shape
                    fill: '#D9F0FF',
                    stroke: '#08BDBA',
                    strokeWidth: 2
                },
                label: {
                    text: 'Output',
                    fill: '#044317',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            }
        }, joint.shapes.standard.Path.prototype.defaults)
    });

    // Timer shape (Flows Timer node)
    joint.shapes.workflow.Timer = joint.shapes.standard.Circle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Timer',
            size: { width: 60, height: 60 },
            attrs: {
                body: {
                    fill: '#F0F7DA',
                    stroke: '#4F6700',
                    strokeWidth: 2
                },
                label: {
                    text: 'Timer',
                    fill: '#4F6700',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle'
                }
            },
            // Add clock hands to timer
            markup: [
                {
                    tagName: 'circle',
                    selector: 'body'
                },
                {
                    tagName: 'path',
                    selector: 'clockHour',
                    attributes: {
                        d: 'M 30,30 L 30,15',
                        stroke: '#4F6700',
                        strokeWidth: 2
                    }
                },
                {
                    tagName: 'path',
                    selector: 'clockMinute',
                    attributes: {
                        d: 'M 30,30 L 40,30',
                        stroke: '#4F6700',
                        strokeWidth: 2
                    }
                },
                {
                    tagName: 'text',
                    selector: 'label',
                    attributes: {
                        'text-anchor': 'middle',
                        'y': '0.8em',
                        'dy': '-1em'
                    }
                }
            ]
        }, joint.shapes.standard.Circle.prototype.defaults)
    });

    // Database shape (New - for Flows Database nodes)
    joint.shapes.workflow.Database = joint.shapes.standard.Cylinder.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Database',
            size: { width: 60, height: 70 },
            attrs: {
                body: {
                    fill: '#E8DAFF',
                    stroke: '#6929C4',
                    strokeWidth: 2
                },
                top: {
                    fill: '#D4BBFF',
                    stroke: '#6929C4',
                    strokeWidth: 2
                },
                label: {
                    text: 'Database',
                    fill: '#6929C4',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold',
                    textVerticalAnchor: 'middle',
                    textAnchor: 'middle',
                    refY: 0.5
                }
            }
        }, joint.shapes.standard.Cylinder.prototype.defaults)
    });

    // Message Flow Node (New - for Flows Message nodes)
    joint.shapes.workflow.Message = joint.shapes.standard.Rectangle.extend({
        defaults: joint.util.deepSupplement({
            type: 'workflow.Message',
            size: { width: 120, height: 50 },
            attrs: {
                body: {
                    fill: '#F2F4F8',
                    stroke: '#4589FF',
                    strokeWidth: 2,
                    rx: 10,
                    ry: 10
                },
                label: {
                    text: 'Message',
                    fill: '#0043CE',
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
