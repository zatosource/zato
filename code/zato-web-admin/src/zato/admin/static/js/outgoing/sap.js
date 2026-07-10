// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SAP = new Class({
   toString: function() {
       var s = '<SAP id:{0} name:{1} is_active:{2}>';
       return String.format(s, this.id ? this.id : '(none)',
                               this.name ? this.name : '(none)',
                               this.is_active ? this.is_active : '(none)');
   }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
   $('#data-table').tablesorter();
   $.fn.zato.data_table.password_required = true;
   $.fn.zato.data_table.class_ = $.fn.zato.data_table.SAP;
   $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.sap.data_table.new_row;
   $.fn.zato.data_table.parse();
   $.fn.zato.data_table.setup_forms(['name', 'host', 'sysnr', 'sysid', 'user', 'client', 'pool_size']);
   var unique_constraints = [
       {field: 'name', entity_type: 'outgoing_sap', attr_name: 'name'}
   ];
   $.each(unique_constraints, function(i, c) {
       $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
       $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
   });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sap.field_descriptions = {
   'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>through self.out.sap.',
   'id_is_active': 'Whether this connection can be used.<br>Services cannot invoke SAP<br>through an inactive connection.',
   'id_host': 'Host name or IP address of the SAP<br>application server the RFC calls go to.',
   'id_sysnr': 'Two-digit instance number of the SAP system,<br>e.g. 00. Together with the host it decides<br>the gateway port the connection uses.',
   'id_sysid': 'Three-character system ID of the SAP system,<br>e.g. PRD or DEV.',
   'id_user': 'SAP user the RFC calls run as. It needs<br>authorizations for the function modules invoked.<br>The password is set with the Change password link.',
   'id_client': 'Three-digit SAP client (mandant) to log on to,<br>e.g. 100. It selects the business data set<br>within the system.',
   'id_router': 'SAPRouter route string when the system sits<br>behind a SAProuter, e.g. /H/saprouter.example.com/S/3299.<br>Leave empty for direct connections.',
   'id_pool_size': 'How many RFC connections are kept open in the pool.<br>More lets concurrent services call SAP in parallel<br>at the cost of more open sessions.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.sap.create = function() {
   $.fn.zato.data_table._create_edit('create', 'Create a new outgoing SAP RFC connection', null);
   $.fn.zato.how_it_works.init({
       badgeId: 'create-how-it-works',
       divId: '#create-div',
       descriptions: $.fn.zato.outgoing.sap.field_descriptions
   });
}

$.fn.zato.outgoing.sap.edit = function(id) {
   $.fn.zato.data_table._create_edit('edit', 'Update the outgoing SAP RFC connection', id);
   $.fn.zato.how_it_works.init({
       badgeId: 'edit-how-it-works',
       divId: '#edit-div',
       descriptions: $.fn.zato.outgoing.sap.field_descriptions
   });
}

$.fn.zato.outgoing.sap.data_table.new_row = function(item, data, include_tr) {
   var row = '';

   if(include_tr) {
       row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
   }

   var is_active = item.is_active == true;

   row += "<td class='numbering'>&nbsp;</td>";
   row += "<td class='impexp'><input type='checkbox' /></td>";
   row += String.format('<td>{0}</td>', item.name);
   row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
   row += String.format('<td>{0}</td>', item.host);
   row += String.format('<td>{0}</td>', item.sysnr);
   row += String.format('<td>{0}</td>', item.sysid);
   row += String.format('<td>{0}</td>', item.user);
   row += String.format('<td>{0}</td>', item.client);
   row += String.format('<td>{0}</td>', item.router || $.fn.zato.empty_value);
   row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change password</a>", item.id));
   row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sap.edit('{0}')\">Edit</a>", item.id));
   row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.sap.delete_('{0}');\">Delete</a>", item.id));
   row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
   row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
   row += String.format("<td class='ignore'>{0}</td>", is_active);
   row += String.format("<td class='ignore'>{0}</td>", item.pool_size);

   if(include_tr) {
       row += '</tr>';
   }

   return row;
}

$.fn.zato.outgoing.sap.delete_ = function(id) {
   $.fn.zato.data_table.delete_(id, 'td.item_id_',
       'SAP RFC connection [{0}] deleted',
       'Are you sure you want to delete the outgoing SAP RFC connection `{0}`?',
       true);
}
