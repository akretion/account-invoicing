# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        option_id = False
        if (
            inv_type in ("out_invoice", "out_refund")
            and move.procurement_id
            and move.procurement_id.sale_line_id
        ):
            line = move.procurement_id.sale_line_id
            option_id = (
                line.fiscal_position_option_id
                and line.fiscal_position_option_id.id
                or False
            )
        res = super(
            StockMove, self.with_context(fiscal_position_option_id=option_id)
        )._get_invoice_line_vals(move, partner, inv_type)
        return res
