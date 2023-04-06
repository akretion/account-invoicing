# Copyright 2023 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    show_missing_attachment_warn = fields.Boolean(
        compute="_compute_show_missing_attachment_warn"
    )

    # Main implementation difficulty: make sure warning banner is automatically removed
    # when an attachment is added
    # It is not the case at the moment because the invoice-part of the form view is not
    # refreshed when an attachment is added (only the chatter is refreshed)
    @api.depends("state", "message_main_attachment_id")
    def _compute_show_missing_attachment_warn(self):
        for move in self:
            show = False
            if (
                move.move_type in ("in_invoice", "in_refund")
                and move.state == "posted"
                and not move.message_main_attachment_id
            ):
                show = True
            move.show_missing_attachment_warn = show
