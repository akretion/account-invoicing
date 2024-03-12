# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fiscal_position_option_id = fields.Many2one(
        comodel_name="account.fiscal.position.option", string="Fiscal position option"
    )

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(
            SaleOrderLine,
            self.with_context(
                fiscal_position_option_id=line.fiscal_position_option_id.id
            ),
        )._prepare_order_line_invoice_line(line, account_id=account_id)
        vals["fiscal_position_option_id"] = line.fiscal_position_option_id.id
        return vals

    def product_id_change(
        self,
        pricelist,
        product,
        qty=0,
        uom=False,
        qty_uos=0,
        uos=False,
        name="",
        partner_id=False,
        lang=False,
        update_tax=True,
        date_order=False,
        packaging=False,
        fiscal_position=False,
        flag=False,
    ):
        res = super(
            SaleOrderLine,
            self.with_context(
                fiscal_position_option_id=self.fiscal_position_option_id.id
            ),
        ).product_id_change(
            pricelist,
            product,
            qty=qty,
            uom=uom,
            qty_uos=qty_uos,
            uos=uos,
            name=name,
            partner_id=partner_id,
            lang=lang,
            update_tax=update_tax,
            date_order=date_order,
            packaging=packaging,
            fiscal_position=fiscal_position,
            flag=flag,
        )
        return res

    @api.onchange("fiscal_position_option_id")
    def change_fiscal_position_option(self):
        product_change_result = self.product_id_change(
            self.order_id.pricelist_id.id,
            self.product_id.id,
            qty=self.product_uom_qty,
            uom=False,
            qty_uos=self.product_uom_qty,
            uos=False,
            name=self.name,
            partner_id=self.order_id.partner_id.id,
            lang=False,
            update_tax=True,
            date_order=self.order_id.date_order,
            packaging=False,
            fiscal_position=self.order_id.fiscal_position.id,
            flag=False,
        )
        if "tax_id" in product_change_result.get("value", {}):
            self.tax_id = [(6, 0, product_change_result["value"]["tax_id"])]
