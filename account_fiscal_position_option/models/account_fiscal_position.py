# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    use_fiscal_position_option = fields.Boolean(string="Use fiscal position option")

    def map_tax(self, taxes):
        if not self:
            return taxes
        if not self.use_fiscal_position_option:
            return super().map_tax(taxes)
        # If this raise it means a case is not supported and should be fixed
        if "fiscal_position_option_id" not in self.env.context:
            raise UserError(
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        result = self.env['account.tax']
        option = self.env.context.get("fiscal_position_option_id", self.env["account.fiscal.position.option"])
        for tax in taxes.filtered(lambda t: t.fiscal_position_option_id == option):
            taxes_correspondance = self.tax_ids.filtered(lambda t: t.tax_src_id == tax._origin)
            result |= taxes_correspondance.tax_dest_id if taxes_correspondance else tax
        return result

    def map_account(self, account):
        if not self.use_fiscal_position_option:
            return super().map_account(account)
        # If this raise it means a case is not supported and should be fixed
        if "fiscal_position_option_id" not in self.env.context:
            raise UserError(
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        option = self.env.context.get("fiscal_position_option_id", self.env["account.fiscal.position.option"])
        for pos in self.account_ids.filtered(lambda a: a.fiscal_position_option_id == option):
            if pos.account_src_id == account:
                return pos.account_dest_id
        return account

    def map_accounts(self, accounts):
        if not self.use_fiscal_position_option:
            return super().map_account(account)
        # If this raise it means a case is not supported and should be fixed
        if "fiscal_position_option_id" not in self.env.context:
            raise UserError(
                _("Fiscal position option is mandatory for this fiscal position"),
            )
        option = self.env.context.get("fiscal_position_option_id", self.env["account.fiscal.position.option"])
        ref_dict = {}
        for line in self.account_ids.filtered(lambda a: a.fiscal_position_option_id == option):
            ref_dict[line.account_src_id] = line.account_dest_id
        for key, acc in accounts.items():
            if acc in ref_dict:
                accounts[key] = ref_dict[acc]
        return accounts


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    fiscal_position_option_id = fields.Many2one(
        string="Fiscal postion option"
    )


class AccountFiscalPositionAccount(models.Model):
    _inherit = "account.fiscal.position.account"

    fiscal_position_option_id = fields.Many2one(
        "account.fiscal.position.option", string="Fiscal postion option"
    )


class AccountFiscalPositionOption(models.Model):
    _name = "account.fiscal.position.option"
    _description = "Account Fiscal Position Option"

    name = fields.Char(string="Name", required=True)
