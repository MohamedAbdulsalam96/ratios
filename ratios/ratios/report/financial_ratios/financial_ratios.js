// Copyright (c) 2016, Babatunde Akinyanmi and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	console.log(erpnext.financial_statements)
	frappe.query_reports["Financial Ratios"] = $.extend({},
		erpnext.financial_statements);

	erpnext.utils.add_dimensions('Profit and Loss Statement', 10);

	// frappe.query_reports["Profit and Loss Statement"]["filters"].push(
	// 	{
	// 		"fieldname": "project",
	// 		"label": __("Project"),
	// 		"fieldtype": "MultiSelectList",
	// 		get_data: function(txt) {
	// 			return frappe.db.get_link_options('Project', txt);
	// 		}
	// 	},
	// 	{
	// 		"fieldname": "include_default_book_entries",
	// 		"label": __("Include Default Book Entries"),
	// 		"fieldtype": "Check",
	// 		"default": 1
	// 	}
	// );
});
