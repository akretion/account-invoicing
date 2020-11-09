# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class DiscountMixin(models.AbstractModel):
    _name = "discount.mixin"
    _description = "Discount Mixin"

    global_discount_amount = fields.Float(
        string="Global Discount Amount", tracking=True, digits="Discount")
    global_discount_ok = fields.Boolean(
        string="Global Discount OK",
        compute="_compute_global_discount_ok", store=True,
        help="The application of the global discount amount is right")

    def _get_line_ids_by_model(self):
        if self._name == "account.move":
            line_ids = self.invoice_line_ids
            return line_ids

    @api.depends("global_discount_amount", "amount_tax", "amount_total")
    def _compute_global_discount_ok(self):
        for record in self:
            global_discount_ok = True
            line_ids = record._get_line_ids_by_model()
            if (line_ids.filtered(lambda x: x.is_discount_line) or
                    record.global_discount_amount != 0.0):
                discount_line_total_amount = 0.0
                for line in line_ids.filtered(lambda x: x.is_discount_line):
                    discount_line_total_amount += (-1 * line.price_subtotal)
                if record.global_discount_amount != discount_line_total_amount:
                    global_discount_ok = False
            record.global_discount_ok = global_discount_ok

    @api.constrains("global_discount_amount")
    def _check_global_discount_amount(self):
        for record in self:
            if record.global_discount_amount < 0.0:
                raise UserError(_(
                    "Global Discount Amount must be a positive number !"))


class DiscountLineMixin(models.AbstractModel):
    _name = "discount.line.mixin"
    _description = "Discount Line Mixin"

    is_discount_line = fields.Boolean(string="Is Discount Line")

    def _prepare_discount_line_vals(self, tax_ids, amount_untaxed,
                                    tax_base_amount, global_discount_amount):
        price_unit = (
            tax_base_amount / amount_untaxed) * global_discount_amount
        return {"product_id": self.product_id.id,
                "quantity": 1,
                "price_unit": -1 * price_unit,
                "tax_ids": tax_ids,
                "account_id": self.account_id.id,
                "name": self.name,
                "partner_id": self.partner_id.id,
                "is_discount_line": True,
                }
