# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.cr_uid_ids_context
    def onchange_fiscal_position(self, cr, uid, ids, fiscal_position, order_lines, context=None):
        line_obj = self.pool.get('sale.order.line')
        order_lines_vals = []
        if context is None:
            context = {}
        for order_line in order_lines:
            print order_line
            # create    (0, 0,  { fields })
            # update    (1, ID, { fields })
            if order_line[0] in [0, 1]:
                ctx = context.copy()
                ctx['fiscal_position_option_id'] = order_line
                if order_line[2].get('fiscal_position_option_id'):
                    ctx['fiscal_position_option_id'] = order_line[2]['fiscal_position_option_id']
                elif order_line[1]:
                    ctx['fiscal_position_option_id'] = line_obj.browse(
                        cr, uid, line[1], context=context
                    ).fiscal_position_option_id.id
                res = super(SaleOrder, self).onchange_fiscal_position(
                    cr, uid, ids, fiscal_position, [order_line], context=ctx)
                print res
                order_lines_vals.append(res['value']['order_line'][0])

            # link      (4, ID)
            # link all  (6, 0, IDS)
            elif order_line[0] in [4, 6]:
                line_ids = order_line[0] == 4 and [order_line[1]] or order_line[2]
                for line_id in line_ids:
                    ctx = context.copy()
                    ctx['fiscal_position_option_id'] =  line_obj.browse(
                        cr, uid, line_id, context=context
                    ).fiscal_position_option_id.id
                    print line_id
                    res = super(SaleOrder, self).onchange_fiscal_position(
                        cr, uid, ids, fiscal_position, [(4, line_id)], context=ctx)
                    print res
                    order_lines_vals.append(res['value']['order_line'][0])
            else:
                order_lines_vals.append(order_line)
        return {'value': {
            'order_line': order_lines_vals, 'amount_untaxed': False,
            'amount_tax': False, 'amount_total': False
        }}
