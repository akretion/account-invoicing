# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    fiscal_position_option_id = fields.Many2one(
        comodel_name="account.fiscal.position.option", string="Fiscal position option"
    )

    @api.multi
    def product_id_change(
        self,
        product,
        uom_id,
        qty=0,
        name="",
        type="out_invoice",
        partner_id=False,
        fposition_id=False,
        price_unit=False,
        currency_id=False,
        company_id=None,
    ):
        return super(
            AccountInvoiceLine,
            self.with_context(
                fiscal_position_option_id=self.fiscal_position_option_id.id
            ),
        ).product_id_change(
            product,
            uom_id,
            qty=qty,
            name=name,
            type=type,
            partner_id=partner_id,
            fposition_id=fposition_id,
            price_unit=price_unit,
            currency_id=currency_id,
            company_id=company_id,
        )

    @api.onchange("fiscal_position_option_id")
    def change_fiscal_position_option(self):
        product_change_result = self.product_id_change(
            self.product_id.id,
            False,
            type=self.invoice_id.type,
            partner_id=self.partner_id.id,
            fposition_id=self.invoice_id.fiscal_position.id,
            company_id=self.invoice_id.company_id.id,
        )
        if "invoice_line_tax_id" in product_change_result.get("value", {}):
            self.invoice_line_tax_id = [
                (6, 0, product_change_result["value"]["invoice_line_tax_id"])
            ]
        if "account_id" in product_change_result.get("value", {}):
            self.account_id = product_change_result["value"]["account_id"]

    @api.multi
    def onchange_account_id(
        self, product_id, partner_id, inv_type, fposition_id, account_id
    ):
        return super(
            AccountInvoiceLine,
            self.with_context(
                fiscal_position_option_id=self.fiscal_position_option_id.id
            ),
        ).onchange_account_id(
            product_id, partner_id, inv_type, fposition_id, account_id
        )
