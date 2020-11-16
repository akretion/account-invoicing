# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountMove(models.Model):
    _inherit = ["account.move", "discount.mixin"]
    _name = "account.move"

    @api.model_create_multi
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if ("global_discount_amount" in vals[0] and
            vals[0]["global_discount_amount"] != 0.0 and
                move.amount_untaxed != 0.0 and
                not self.env.context.get("discount_lines_from_sale", False)):
            self.env["account.move.line"]._create_discount_lines(move=move)
            move.with_context(check_move_validity=False)._recompute_tax_lines()
        return move

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if (("global_discount_amount" in vals or "line_ids" in vals or
             not self.global_discount_ok) and
                not self.env.context.get("discount_lines", False) and
                not self.env.context.get("discount_lines_from_sale", False)):
            # we can not unlink move lines linked with sale lines
            self.invoice_line_ids.filtered(
                lambda x: x.is_discount_line).with_context(
                    check_move_validity=False, discount_lines=True).unlink()
            self.with_context(check_move_validity=False,
                              discount_lines=True)._recompute_tax_lines()
            if self.global_discount_amount != 0.0:
                self.env["account.move.line"]._create_discount_lines(move=self)
                self.with_context(check_move_validity=False,
                                  discount_lines=True)._recompute_tax_lines()
        return res


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "discount.line.mixin"]
    _name = "account.move.line"

    def _create_discount_lines(self, move):
        amount_untaxed = move.amount_untaxed
        # create discount lines by tax line
        with_tax_lines = move.line_ids.filtered(
            lambda x: x.tax_line_id)
        for line in with_tax_lines:
            tax_ids = [(6, 0, [line.tax_line_id.id])]
            tax_base_amount = line.tax_base_amount
            self._create_one_discount_line(
                move=move, tax_ids=tax_ids, tax_base_amount=tax_base_amount,
                amount_untaxed=amount_untaxed)
        # create one discount line for the all invoice lines without tax lines
        lines_with_tax = move.line_ids.filtered(lambda x: x.tax_ids)
        line_tax_ids = lines_with_tax.tax_ids - with_tax_lines.tax_line_id
        without_tax_lines = move.invoice_line_ids.filtered(
            lambda x: x.tax_ids == line_tax_ids)
        without_tax_base_amount = 0.0
        for line in without_tax_lines:
            without_tax_base_amount += line.price_subtotal
        if without_tax_lines:
            tax_ids = [(6, 0, without_tax_lines.tax_ids.ids)]
            self._create_one_discount_line(
                move=move, tax_ids=tax_ids,
                tax_base_amount=without_tax_base_amount,
                amount_untaxed=amount_untaxed)

    def _create_one_discount_line(
            self, move, tax_ids, tax_base_amount, amount_untaxed):
        global_discount_amount = move.global_discount_amount
        discount_product = self.env.ref(
            "account_global_discount_amount.discount_product")
        discount_line = self.env["account.move.line"].new({
            "product_id": discount_product.id,
            "move_id": move.id,
            "partner_id": move.partner_id.id})
        discount_line._onchange_product_id()
        discount_line_vals = discount_line._prepare_discount_line_vals(
            amount_untaxed=amount_untaxed,
            tax_base_amount=tax_base_amount,
            global_discount_amount=global_discount_amount)
        discount_line_vals.update({"move_id": move.id,
                                   "partner_id": move.partner_id.id,
                                   "quantity": 1,
                                   "tax_ids": tax_ids,
                                   "account_id": discount_line.account_id.id})
        discount_line.with_context(check_move_validity=False).unlink()
        self.with_context(check_move_validity=False).create(
            discount_line_vals)
