# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_move_vals(self, default_values, cancel=True):
        # Set the sale_qty_to_reinvoice based on the boolean from the
        # reversal wizard. Callers that do not pass the key (the switch of an
        # invoice into a credit note) keep the flag copied from the lines.
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        if "sale_qty_to_reinvoice" in self.env.context:
            to_reinvoice = bool(self.env.context["sale_qty_to_reinvoice"])
            for vals in move_vals["line_ids"]:
                vals[2].update({"sale_qty_to_reinvoice": to_reinvoice})
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_qty_to_reinvoice = fields.Boolean(
        string="Sale qty to reinvoice",
        default=True,
        help="Leave it marked if you will reinvoice the same sale order line",
    )
