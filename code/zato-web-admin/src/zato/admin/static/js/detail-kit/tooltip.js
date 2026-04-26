
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.dashboard_kit === 'undefined') { $.fn.zato.dashboard_kit = {}; }

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.tooltip = {};

    kit.tooltip.show = function(event, html) {
        var $tt = $('#detail-kit-tooltip');
        if ($tt.length === 0) {
            $('body').append('<div id="detail-kit-tooltip" class="kit-tooltip"></div>');
            $tt = $('#detail-kit-tooltip');
        }
        $tt.html(html).css({display: 'block', left: '0px', top: '0px'});
        var w = $tt.outerWidth();
        var h = $tt.outerHeight();
        var margin = 8;
        var vw = $(window).width();
        var vh = $(window).height();
        var left = event.clientX + 14;
        var top = event.clientY - 14;
        if (left + w + margin > vw) left = event.clientX - w - 14;
        if (left < margin) left = margin;
        if (top + h + margin > vh) top = vh - h - margin;
        if (top < margin) top = margin;
        $tt.css({left: left + 'px', top: top + 'px'});
    };

    kit.tooltip.hide = function() {
        $('#detail-kit-tooltip').css('display', 'none');
    };
})();
