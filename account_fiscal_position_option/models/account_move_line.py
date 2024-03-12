# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fiscal_position_option_id = fields.Many2one(
        "account.fiscal.position.option", string="Fiscal position option"
    )

    def _sale_prepare_sale_line_values(self, order, price):
        return super(AccountMoveLine, self.with_context(fiscal_position_option_id=self.fiscal_position_option_id))._sale_prepare_sale_line_values(order, price)

    def _compute_account_id(self):
        return super(AccountMoveLine, self.with_context(fiscal_position_option_id=self.fiscal_position_option_id))._compute_account_id()

    def onchange_partner_id(
        self,
        move_id,
        partner_id,
        account_id=None,
        debit=0,
        credit=0,
        date=False,
        journal=False,
    ):
        return super(
            AccountMoveLine, self.with_context(fiscal_position_option_id=False)
        ).onchange_partner_id(
            move_id,
            partner_id,
            account_id=account_id,
            debit=debit,
            credit=credit,
            date=date,
            journal=journal,
        )

    def onchange_account_id(self, account_id=False, partner_id=False):
        return super(
            AccountMoveLine, self.with_context(fiscal_position_option_id=False)
        ).onchange_account_id(account_id=account_id, partner_id=partner_id)

    @api.model
    def _default_get(self, fields):
        return super(
            AccountMoveLine, self.with_context(fiscal_position_option_id=False)
        )._default_get(fields)
