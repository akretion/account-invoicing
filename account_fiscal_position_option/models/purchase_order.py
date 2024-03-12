# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _choose_account_from_po_line(self, po_line):
        return super(
            PurchaseOrder, self.with_context(fiscal_position_option_id=False)
        )._choose_account_from_po_line(po_line)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.cr_uid_ids
    def onchange_product_id(
        self,
        cr,
        uid,
        ids,
        pricelist_id,
        product_id,
        qty,
        uom_id,
        partner_id,
        date_order=False,
        fiscal_position_id=False,
        date_planned=False,
        name=False,
        price_unit=False,
        state="draft",
        context=None,
    ):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
        ctx = context.copy()
        ctx["fiscal_position_option_id"] = False
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr,
            uid,
            ids,
            pricelist_id,
            product_id,
            qty,
            uom_id,
            partner_id,
            date_order=date_order,
            fiscal_position_id=fiscal_position_id,
            date_planned=date_planned,
            name=name,
            price_unit=price_unit,
            state=state,
            context=ctx,
        )
        return res


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_po_line_values_from_proc(
        self, procurement, partner, company, schedule_date
    ):
        return super(
            ProcurementOrder, self.with_context(fiscal_position_option_id=False)
        )._get_po_line_values_from_proc(procurement, partner, company, schedule_date)
