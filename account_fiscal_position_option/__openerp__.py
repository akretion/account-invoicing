# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Account fiscal position optaion",
    "version": "8.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "summary": "Add fiscal position option to change on sale order line.",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_fiscal_position.xml",
        "views/sale_order_line.xml",
        "views/account_invoice_line.xml",
    ],
}
