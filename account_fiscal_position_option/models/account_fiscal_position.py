##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    use_fiscal_position_option = fields.Boolean(string="Use fiscal position option")

    @api.v7
    def map_tax(self, cr, uid, fposition_id, taxes, context=None):
        if context is None:
            context = {}
        if not taxes:
            return []
        if not fposition_id:
            return map(lambda x: x.id, taxes)
        if (
            fposition_id.use_fiscal_position_option
            and not "fiscal_position_option_id" in context
        ):
            raise UserError(
                _("Error"),
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        result = set()
        for t in taxes:
            ok = False
            for tax in fposition_id.tax_ids:
                if fposition_id.use_fiscal_position_option:
                    if (
                        tax.tax_src_id.id == t.id
                        and tax.fiscal_position_option_id.id
                        == context["fiscal_position_option_id"]
                    ):
                        if tax.tax_dest_id:
                            result.add(tax.tax_dest_id.id)
                        ok = True
                else:
                    if tax.tax_src_id.id == t.id:
                        if tax.tax_dest_id:
                            result.add(tax.tax_dest_id.id)
                        ok = True
            if not ok:
                result.add(t.id)
        return list(result)

    @api.v8  # noqa
    def map_tax(self, taxes):
        if (
            self.use_fiscal_position_option
            and not "fiscal_position_option_id" in self._context
        ):
            raise UserError(
                _("Error"),
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        result = self.env["account.tax"].browse()
        for tax in taxes:
            tax_count = 0
            for t in self.tax_ids:
                if self.use_fiscal_position_option:
                    if (
                        t.tax_src_id == tax
                        and t.fiscal_position_option_id.id
                        == self._context["fiscal_position_option_id"]
                    ):
                        tax_count += 1
                        if t.tax_dest_id:
                            result |= t.tax_dest_id
                else:
                    if t.tax_src_id == tax:
                        tax_count += 1
                        if t.tax_dest_id:
                            result |= t.tax_dest_id
            if not tax_count:
                result |= tax
        return result

    @api.v7
    def map_account(self, cr, uid, fposition_id, account_id, context=None):
        if context is None:
            context = {}
        if not fposition_id:
            return account_id
        if (
            fposition_id.use_fiscal_position_option
            and not "fiscal_position_option_id" in context
        ):
            raise UserError(
                _("Error"),
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        for pos in fposition_id.account_ids:
            if fposition_id.use_fiscal_position_option:
                if (
                    pos.account_src_id.id == account_id
                    and pos.fiscal_position_option_id.id
                    == context["fiscal_position_option_id"]
                ):
                    account_id = pos.account_dest_id.id
                    break
            else:
                if pos.account_src_id.id == account_id:
                    account_id = pos.account_dest_id.id
                    break
        return account_id

    @api.v8
    def map_account(self, account):
        if (
            self.use_fiscal_position_option
            and not "fiscal_position_option_id" in self._context
        ):
            raise UserError(
                _("Error"),
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        for pos in self.account_ids:
            if self.use_fiscal_position_option:
                if (
                    pos.account_src_id == account
                    and pos.fiscal_position_option_id.id
                    == self._context["fiscal_position_option_id"]
                ):
                    return pos.account_dest_id
            else:
                if pos.account_src_id == account:
                    return pos.account_dest_id
        return account


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    fiscal_position_option_id = fields.Many2one(
        comodel_name="account.fiscal.position.option", string="Fiscal postion option"
    )


class AccountFiscalPositionAccount(models.Model):
    _inherit = "account.fiscal.position.account"

    fiscal_position_option_id = fields.Many2one(
        comodel_name="account.fiscal.position.option", string="Fiscal postion option"
    )


class AccountFiscalPositionOption(models.Model):
    _name = "account.fiscal.position.option"
    _description = "Account Fiscal Position Option"

    name = fields.Char(string="Name", required=True)
