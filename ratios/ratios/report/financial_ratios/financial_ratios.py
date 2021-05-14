# Copyright (c) 2013, Babatunde Akinyanmi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_data)

def execute(filters=None):
	sales_accounts_names = get_sales_accounts_names(filters)

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.period_start_date, filters.period_end_date, filters.filter_based_on, filters.periodicity,
		company=filters.company)
	# print(period_list)

	income = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company, filters.presentation_currency)

	data = []
	p_and_l_data = []
	p_and_l_data.extend(income or [])
	p_and_l_data.extend(expense or [])
	if net_profit_loss:
		p_and_l_data.append(net_profit_loss)

	data.extend(get_net_profit_margin(p_and_l_data, sales_accounts_names, period_list))

	# print(net_profit_loss)
	# print('==================================================')
	# print(p_and_l_data)
	# print(data)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)
	print(columns)

	return columns, data


def get_net_profit_margin(data_list, sales_accounts_names, periods):
	sales = []
	net_income = None
	for item in data_list:
		if item.get('account') and item.get('account') in sales_accounts_names:
			sales.append(item)
		elif item.get('account_name') == "'Profit for the year'":
			net_income = item

	total_sales = {
		'account_name': 'Net Profit Margin', 
		'account': "'Net Profit Margin'",
		'warn_if_negative': True,
		'currency': 'NGN',
		'total': 0
	}

	for item in sales:
		for period in periods:
			total_sales[period['key']] = item[period['key']] if total_sales.get(period['key']) else item[period['key']]
		total_sales['total'] += item['total']

	for period in periods:
		total_sales[period['key']] = flt(net_income[period['key']] / max(total_sales[period['key']], 1), 2)
	total_sales['total'] = flt(net_income['total'] / max(total_sales['total'], 1), 2)

	return [total_sales]



def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [{
		"fieldname": "account",
		"label": _("Ratio"),
		"fieldtype": "Data",
		"width": 300
	}]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Data",
			"width": 150
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Data",
				"width": 150
			})

	return columns



def get_sales_accounts_names(filters):
	sales_accounts = []

	for account in frappe.get_single('Financial Ratio Configurator').sales_accounts:
		sales_accounts.append(account.account)

	return sales_accounts

def get_report_summary(period_list, periodicity, income, expense, net_profit_loss, currency, consolidated=False):
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

	for period in period_list:
		key = period if consolidated else period.key
		if income:
			net_income += income[-2].get(key)
		if expense:
			net_expense += expense[-2].get(key)
		if net_profit_loss:
			net_profit += net_profit_loss.get(key)

	if (len(period_list) == 1 and periodicity== 'Yearly'):
			profit_label = _("Profit This Year")
			income_label = _("Total Income This Year")
			expense_label = _("Total Expense This Year")
	else:
		profit_label = _("Net Profit")
		income_label = _("Total Income")
		expense_label = _("Total Expense")

	return [
		{
			"value": net_income,
			"label": income_label,
			"datatype": "Currency",
			"currency": currency
		},
		{ "type": "separator", "value": "-"},
		{
			"value": net_expense,
			"label": expense_label,
			"datatype": "Currency",
			"currency": currency
		},
		{ "type": "separator", "value": "=", "color": "blue"},
		{
			"value": net_profit,
			"indicator": "Green" if net_profit > 0 else "Red",
			"label": profit_label,
			"datatype": "Currency",
			"currency": currency
		}
	]


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss
