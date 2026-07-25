# Copyright (C) 2020-TODAY KMEE
# Copyright (C) 2021-TODAY Akretion
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    @api.model
    def _default_has_down_payment(self):
        pickings = self._load_pickings()
        sale_pickings = pickings.filtered(lambda pk: pk.sale_id)
        downpayment_lines = False
        if sale_pickings:
            for pick in sale_pickings:
                if pick.sale_id.order_line.filtered(lambda ln: ln.is_downpayment):
                    downpayment_lines = True

        return downpayment_lines

    deduct_down_payments = fields.Boolean("Deduct down payments", default=True)
    has_down_payments = fields.Boolean(
        "Has down payments", default=_default_has_down_payment, readonly=True
    )

    def _get_fields_not_used_from_sale(self):
        """Fields not used from Sale 'prepare' method"""
        return {
            "move_type",
            "currency_id",
            "user_id",
            "invoice_user_id",
            "partner_id",
            "fiscal_position_id",
            "journal_id",  # company comes from the journal
            "invoice_origin",
            "invoice_line_ids",
            "company_id",
            "__last_update",
            "display_name",
        }

    def _build_invoice_values_from_pickings(self, pickings):
        invoice, values = super()._build_invoice_values_from_pickings(pickings)

        sale_pickings = pickings.filtered(lambda pk: pk.sale_id)
        # Refund case don't get values from Sale Dict
        if sale_pickings and self._get_invoice_type() != "out_refund":
            payment_refs = set()
            refs = set()
            narration = set()
            for pick in sale_pickings.sorted(key=lambda p: p.name):
                sale_values = pick.sale_id._prepare_invoice()
                payment_refs.add(sale_values["payment_reference"])
                refs.add(sale_values["ref"])
                if sale_values["narration"]:
                    narration.add(sale_values["narration"])

                sale_values_rm = {
                    k: sale_values[k]
                    for k in set(sale_values) - self._get_fields_not_used_from_sale()
                }

                values.update(sale_values_rm)

            if len(sale_pickings) > 1:
                values.update(
                    {
                        "ref": ", ".join(refs)[:2000],
                        "payment_reference": len(payment_refs) == 1
                        and payment_refs.pop()
                        or False,
                        "narration": ", ".join(narration),
                    }
                )

        return invoice, values

    def _get_move_key(self, move):
        key = super()._get_move_key(move)
        if move.sale_line_id:
            key = key + (move.sale_line_id,)

        return key

    def _get_fields_not_used_from_sale_line(self):
        """Fields not used from Sale Line 'prepare' method"""
        return {
            "name",
            "product_id",
            "product_uom_id",
            "quantity",
            "price_unit",
            "tax_ids",
            "sale_line_ids",
            "anlytic_distribution",
            "__last_update",
            "display_name",
        }

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        values = super()._get_invoice_line_values(moves, invoice_values, invoice)
        move = fields.first(moves)
        if move.sale_line_id:
            sale_line_values = move.sale_line_id._prepare_invoice_line()
            values["sale_line_ids"] = [(6, 0, moves.sale_line_id.ids)]
            values["analytic_distribution"] = sale_line_values.get(
                "analytic_distribution"
            )
            if self._get_invoice_type() != "out_refund":
                sale_line_values_rm = {
                    k: sale_line_values[k]
                    for k in set(sale_line_values)
                    - self._get_fields_not_used_from_sale_line()
                }
                values.update(sale_line_values_rm)

        return values

    def _get_pickings_with_sale(self, invoice_values):
        pickings = self._load_pickings()
        picking_in_invoice_values = self.env["stock.picking"]
        for line in invoice_values.get("invoice_line_ids"):
            if line[2]:
                if len(line[2].get("move_line_ids")[0]) == 2:
                    move_line_id = line[2].get("move_line_ids")[0][1]
                else:
                    move_line_id = line[2].get("move_line_ids")[0][2]
                move_line = self.env["stock.move"].browse(move_line_id)
                picking_in_invoice_values |= move_line.mapped("picking_id")

        sale_pickings = pickings.filtered(
            lambda pk: pk.sale_id and pk.id in picking_in_invoice_values.ids
        )

        return sale_pickings

    def _create_invoice(self, invoice_values):
        """Override this method to inject Section, Note and Down Payment lines
        from linked Sale Orders before creating the invoice.

        :param invoice_values: dict with the invoice and its lines
        :return: invoice
        """
        sale_pickings = self._get_pickings_with_sale(invoice_values)

        if not sale_pickings or self._get_invoice_type() == "out_refund":
            return super()._create_invoice(invoice_values)

        section_note_lines = down_payment_lines = self.env["sale.order.line"]
        invoice_item_sequence = 0
        invoice_item_seq_dict = {}
        for pick in sale_pickings.sorted(key=lambda p: p.name):
            order = pick.sale_id.with_company(pick.sale_id.company_id)
            invoiceable_lines = order._get_invoiceable_lines(final=True)
            section_note_lines |= invoiceable_lines.filtered(
                lambda ln: ln.display_type in ("line_section", "line_note")
            )
            down_payment_lines |= invoiceable_lines.filtered(
                lambda ln: ln.is_downpayment
            )

            for line in order.order_line:
                invoice_item_seq_dict[line.id] = invoice_item_sequence
                invoice_item_sequence += 1

        # Sections and Notes
        if section_note_lines:
            section_note_vals = []
            for line in section_note_lines:
                sale_line_vals = line._prepare_invoice_line()
                sale_line_vals["sale_line_ids"] = [
                    (6, 0, [sale_line_vals.get("sale_line_ids")[0][1]])
                ]
                section_note_vals.append((0, 0, sale_line_vals))

            invoice_values["invoice_line_ids"] += section_note_vals

        # Resequencing for grouped Sale Orders
        for line in invoice_values.get("invoice_line_ids"):
            if line[2]:
                sale_line = line[2].get("sale_line_ids")
                if sale_line:
                    line[2]["sequence"] = invoice_item_seq_dict.get(sale_line[0][2][0])

        # Down Payments
        if down_payment_lines:
            down_payment_vals = []
            down_payment_section_added = False
            for line in down_payment_lines:
                if not down_payment_section_added and line.is_downpayment:
                    down_payment_vals.append(
                        (
                            0,
                            0,
                            line.order_id._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence,
                            ),
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1

                if line.is_downpayment:
                    down_payment_vals.append(
                        (
                            0,
                            0,
                            line._prepare_invoice_line(
                                sequence=invoice_item_sequence,
                            ),
                        ),
                    )
                    invoice_item_sequence += 1

            invoice_values["invoice_line_ids"] += down_payment_vals

        moves = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice")
            .create(invoice_values)
        )

        final = self.deduct_down_payments
        if final:
            moves.sudo().filtered(
                lambda m: m.amount_total < 0
            ).action_switch_move_type()
        for move in moves:
            move.message_post_with_source(
                "mail.message_origin_link",
                render_values={
                    "self": move.picking_ids,
                    "origin": move.picking_ids,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )

        return moves
