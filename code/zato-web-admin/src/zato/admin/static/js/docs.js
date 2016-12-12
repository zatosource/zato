// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.docs.Docs = new Class({
    initialize: function() {
        this.data = 'aaaa';
    },

    get_data: function() {
        return this.data;
    }

});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.docs.show_docs = function() {

    var docs = new $.fn.zato.docs.Docs();
    console.log(docs.data);

    /*
    var data = JSON.parse($('#docs-data').text());

    var main_div = $('#main-div');
    var main_table = $('<table></table>');
    var tbody = $('<tbody></tbody>', {'id':'docs-tbody'});

    main_div.append(main_table);
    main_table.append(tbody);
    */
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $.fn.zato.docs.show_docs();

})
