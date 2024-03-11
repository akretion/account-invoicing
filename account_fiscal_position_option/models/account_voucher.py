# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, models


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.multi
    def compute_tax(self):
        return super(
            AccountVoucher, self.with_context(fiscal_position_option_id=False)
        ).compute_tax()

    @api.multi
    def onchange_price(self, line_ids, tax_id, partner_id=False):
        return super(
            AccountVoucher, self.with_context(fiscal_position_option_id=False)
        ).onchange_price(line_ids, tax_id, partner_id=partner_id)
