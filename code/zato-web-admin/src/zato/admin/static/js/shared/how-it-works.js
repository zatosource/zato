/*
 * "How does it work?" badge - hover tooltip and click handler.
 *
 * Attaches a tippy tooltip to every .how-it-works-badge element
 * inside .data-popup dialogs. The tooltip explains what happens
 * when the badge is clicked.
 */

if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.how_it_works === 'undefined') { $.fn.zato.how_it_works = {}; }

$.fn.zato.how_it_works.init = function(elem_id) {

    var elem = document.getElementById(elem_id);
    if (!elem) {
        return;
    }

    if (elem._tippy) {
        elem._tippy.destroy();
    }

    tippy(elem, {
        content: 'Click to see a description<br>of each field in this form',
        allowHTML: true,
        placement: 'left',
        theme: 'dark',
        arrow: true,
        interactive: false,
        inertia: true,
        appendTo: function() { return elem.closest('.ui-dialog') || document.body; },
    });
};
