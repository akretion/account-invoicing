# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# Copyright (C) 2016-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
    _name = 'wizard.update.invoice.supplierinfo'

    line_ids = fields.One2many(
        comodel_name='wizard.update.invoice.supplierinfo.line',
        inverse_name='wizard_id', string='Lines')

    invoice_id = fields.Many2one(comodel_name='account.invoice', required=True)

    state = fields.Selection(
        related='invoice_id.state', readonly=True)

    supplier_partner_id = fields.Many2one(
        comodel_name='res.partner', string='Supplier',
        related='invoice_id.supplier_partner_id', readonly=True)

    @api.multi
    def update_supplierinfo(self):
        self.ensure_one()
        supplierinfo_obj = self.env['product.supplierinfo']
        partnerinfo_obj = self.env['pricelist.partnerinfo']
        for line in self.line_ids:
            supplierinfo = line.supplierinfo_id
            partnerinfo = line.partnerinfo_id

            # Create supplierinfo if not exist
            if not supplierinfo:
                supplierinfo = supplierinfo_obj.create(
                    line._prepare_supplierinfo())

            partnerinfo_vals = line._prepare_partnerinfo(supplierinfo)

            # Create partnerinfo if not exist
            if not line.partnerinfo_id:
                partnerinfo_obj.create(partnerinfo_vals)

            # Update partnerinfo, if exist
            else:
                partnerinfo.write(partnerinfo_vals)

        # Mark the invoice as checked
        self.invoice_id.write({'supplierinfo_ok': True})

    @api.multi
    def set_supplierinfo_ok(self):
        self.invoice_id.write({'supplierinfo_ok': True})

    @api.multi
    def update_supplierinfo_validate(self):
        self.update_supplierinfo()
        invoice = self.env['account.invoice'].browse(
            self._context['active_id'])
        invoice.signal_workflow('invoice_open')


class WizardUpdateInvoiceSupplierinfoLine(models.TransientModel):
    _name = 'wizard.update.invoice.supplierinfo.line'

    _SELECTION_STATE = [
        ('new_supplierinfo', 'New Supplier Info'),
        ('new_partnerinfo', 'New Partner Info'),
        ('update_partnerinfo', 'Update Partner Info'),
    ]

    wizard_id = fields.Many2one(
        comodel_name='wizard.update.invoice.supplierinfo', required=True,
        ondelete='cascade')

    product_id = fields.Many2one('product.product', string='Product')

    supplierinfo_id = fields.Many2one(comodel_name='product.supplierinfo')

    partnerinfo_id = fields.Many2one(comodel_name='pricelist.partnerinfo')

    current_min_quantity = fields.Integer(
        string='Current Quantity', readonly=True)

    new_min_quantity = fields.Float(string='New Quantity', required=True)

    current_price = fields.Float(
        string='Current Unit Price', digits=dp.get_precision('Product Price'),
        readonly=True)

    new_price = fields.Float(
        string='New Unit Price', digits=dp.get_precision('Product Price'),
        required=True)

    price_variation = fields.Float(
        string='Price Variation (%)', compute='_compute_price_variation',
        digits_compute=dp.get_precision('Discount'))

    state = fields.Selection(selection=_SELECTION_STATE)

    @api.depends('current_price', 'new_price')
    @api.multi
    def _compute_price_variation(self):
        for line in self:
            if line.current_price:
                line.price_variation = 100 *\
                    (line.new_price - line.current_price) / line.current_price
            else:
                line.price_variation = False

    # Custom Section
    @api.multi
    def _prepare_supplierinfo(self):
        self.ensure_one()
        return {
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'name': self.wizard_id.invoice_id.supplier_partner_id.id,
            'min_qty': 0.0,
            'delay': 1,
        }

    @api.multi
    def _prepare_partnerinfo(self, supplierinfo):
        self.ensure_one()
        return {
            'suppinfo_id': supplierinfo.id,
            'min_quantity': self.new_min_quantity,
            'price': self.new_price,
        }
