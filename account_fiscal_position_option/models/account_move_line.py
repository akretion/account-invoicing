# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
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

    @api.multi
    def onchange_account_id(self, account_id=False, partner_id=False):
        return super(
            AccountMoveLine, self.with_context(fiscal_position_option_id=False)
        ).onchange_account_id(account_id=account_id, partner_id=partner_id)

    @api.model
    def _default_get(self, fields):
        return super(
            AccountMoveLine, self.with_context(fiscal_position_option_id=False)
        )._default_get(fields)
