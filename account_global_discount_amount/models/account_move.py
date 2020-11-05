# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountMove(models.Model):
    _inherit = ["account.move", "discount.mixin"]
    _name = "account.move"

    @api.model_create_multi
    def create(self, vals):
        move = super(AccountMove, self).create(vals)
        if (vals[0]["global_discount_amount"] != 0.0 and
                move.amount_untaxed != 0.0):
            self.env["account.move.line"]._create_discount_lines(move=move)
            move.with_context({
                "check_move_validity": False})._recompute_tax_lines()
        return move

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if "global_discount_amount" in vals:
            self.invoice_line_ids.filtered(
                lambda x: x.is_discount_line).with_context({
                    "check_move_validity": False}).unlink()
            self.with_context({
                "check_move_validity": False})._recompute_tax_lines()
            if vals["global_discount_amount"] != 0.0:
                self.env["account.move.line"]._create_discount_lines(move=self)
                self.with_context({
                    "check_move_validity": False})._recompute_tax_lines()
        return res


class AccountMoveLine(models.Model):
    _inherit = ["account.move.line", "discount.line.mixin"]
    _name = "account.move.line"

    def _create_discount_lines(self, move):
        amount_untaxed = move.amount_untaxed
        tax_lines = move.line_ids.filtered(
            lambda x: x.tax_base_amount != 0.0)
        for tax_line in tax_lines:
            tax_id = tax_line.tax_line_id.id
            global_discount_amount = move.global_discount_amount
            discount_product = self.env.ref(
                "account_global_discount_amount.discount_product")
            tax_base_amount = tax_line.tax_base_amount
            discount_line = self.env["account.move.line"].new()
            discount_line.with_context({"check_move_validity": False}).write({
                "product_id": discount_product.id,
                "move_id": move.id,
                "partner_id": move.partner_id.id})
            discount_line_vals = discount_line._prepare_discount_line_vals(
                amount_untaxed=amount_untaxed,
                tax_base_amount=tax_base_amount,
                global_discount_amount=global_discount_amount,
                tax_id=tax_id)
            discount_line.with_context({"check_move_validity": False}).unlink()
            self.with_context({"check_move_validity": False}).create(
                discount_line_vals)
