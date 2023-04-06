# Copyright 2023 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Missing Attachment Warn",
    "version": "14.0.1.0.0",
    "category": "Accounting/Accounting",
    "license": "AGPL-3",
    "summary": "Show warning banner on vendor bills when attachment is missing",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "data": [
        "views/account_move.xml",
    ],
    "installable": True,
}
