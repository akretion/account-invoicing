# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestAccountGlobalDiscountAmount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner Test"})
        cls.product01 = cls.env.ref("product.consu_delivery_01")
        cls.product03 = cls.env.ref("product.consu_delivery_03")
        cls.discount_product = cls.env.ref(
            "account_global_discount_amount.discount_product")
        cls.account = cls.env["account.account"].search(
            [("user_type_id", "=",
              cls.env.ref("account.data_account_type_revenue").id)], limit=1)
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1)
        cls.type_current_liability = cls.env.ref(
            "account.data_account_type_current_liabilities")
        cls.output_vat10_acct = cls.env["account.account"].create(
            {"name": "10",
             "code": "10",
             "user_type_id": type_current_liability.id})
        cls.output_vat20_acct = cls.env["account.account"].create(
            {"name": "20",
             "code": "20",
             "user_type_id": type_current_liability.id})
        cls.tax_group_vat10 = cls.env["account.tax.group"].create({
            "name": "VAT10"})
        cls.tax_group_vat20 = cls.env["account.tax.group"].create({
            "name": "VAT20"})
        cls.vat10 = cls.env["account.tax"].create(
            {"name": "TEST 10%",
             "type_tax_use": "sale",
             "amount_type": "percent",
             "amount": 10.00,
             "tax_group_id": cls.tax_group_vat10.id,
             "tax_exigibility": "on_invoice",
             "invoice_repartition_line_ids": [
                (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                (0, 0, {"factor_percent": 100.0, "repartition_type": "tax",
                        "account_id": cls.output_vat10_acct.id})]
            }
        cls.vat20 = cls.env["account.tax"].create(
            {"name": "TEST 20%",
             "type_tax_use": "sale",
             "amount_type": "percent",
             "amount": 20.00,
             "tax_group_id": cls.tax_group_vat20.id,
             "tax_exigibility": "on_invoice",
             "invoice_repartition_line_ids": [
                (0, 0, {"factor_percent": 100.0, "repartition_type": "base"}),
                (0, 0, {"factor_percent": 100.0, "repartition_type": "tax",
                        "account_id": cls.output_vat20_acct.id})],
            }
        single_tax_invoice_line_vals = [
            (0, 0, {
                    "product_id": self.product01.id,
                    "quantity": 1.0,
                    "account_id": self.account.id,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "tax_ids": [(6, 0, [self.vat10.id])],
                },
            )
        ]
        cls.invoice_single_tax = cls.env["account.move"].create({
                    "journal_id": self.journal.id,
                    "partner_id": self.partner.id,
                    "type": "out_invoice",
                    "invoice_line_ids": single_tax_invoice_line_vals,
                    "global_discount_amount": 30.00,
                })
        multi_tax_invoice_line_vals = [
            (0, 0, {
                    "product_id": self.product01.id,
                    "quantity": 1.0,
                    "account_id": self.account.id,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    "tax_ids": [(6, 0, [self.vat10.id])],
                },
            ),
            (0, 0, {
                    "product_id": self.product03.id,
                    "quantity": 1.0,
                    "account_id": self.account.id,
                    "name": "Line 1",
                    "price_unit": 150.00,
                    "tax_ids": [(6, 0, [self.vat20.id])],
                },
            )
        ]
        cls.invoice_multi_tax = cls.env["account.move"].create({
                    "journal_id": self.journal.id,
                    "partner_id": self.partner.id,
                    "type": "out_invoice",
                    "invoice_line_ids": multi_tax_invoice_line_vals,
                    "global_discount_amount": 50.00,
                })

    def test_create_invoice_single_tax_with_global_discount(self):
        self.assertEqual(self.invoice_single_tax.amount_total, 187.00)
        self.assertEqual(self.invoice_single_tax.amount_tax, 17.00)
        #self.assertEqual(self.invoice_single_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_single_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 1)
        self.assertEqual(discount_move_lines[0].is_discount_line, True)
        self.assertEqual(discount_move_lines[0].price_unit, -30.00)
        self.assertEqual(discount_move_lines[0].quantity, 1.0)
        self.assertEqual(len(discount_move_lines[0].tax_ids), 1)
        self.assertEqual(discount_move_lines[0].tax_ids[0].name, "TEST 10%")

    def test_create_invoice_multi_tax_with_global_discount(self):
        self.assertEqual(self.invoice_multi_tax.amount_untaxed, 300.00)
        self.assertEqual(self.invoice_multi_tax.amount_tax, 42.86)
        self.assertEqual(self.invoice_multi_tax.amount_total, 342.86)
        #self.assertEqual(self.invoice_multi_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_multi_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 2)
        discount_line_10 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat10)
        self.assertEqual(discount_line_10.price_unit, -28.57)
        discount_line_20 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat20)
        self.assertEqual(discount_line_20.price_unit, -21.43)

    def test_write_invoice_single_tax_with_change_global_discount(self):
        self.invoice_single_tax.write({"global_discount_amount": 25.00})
        self.assertEqual(self.invoice_single_tax.amount_total, 192.50)
        self.assertEqual(self.invoice_single_tax.amount_tax, 17.50)
        #self.assertEqual(self.invoice_single_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_single_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 1)
        self.assertEqual(discount_move_lines[0].is_discount_line, True)
        self.assertEqual(discount_move_lines[0].price_unit, -25.00)

    def test_write_invoice_multi_tax_with_change_global_discount(self):
        self.invoice_multi_tax.write({"global_discount_amount": 45.00})
        self.assertEqual(self.invoice_multi_tax.amount_untaxed, 305.00)
        self.assertEqual(self.invoice_multi_tax.amount_tax, 43.57)
        self.assertEqual(self.invoice_multi_tax.amount_total, 348.57)
        #self.assertEqual(self.invoice_multi_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_multi_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 2)
        discount_line_10 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat10)
        self.assertEqual(discount_line_10.price_unit, -25.71)
        discount_line_20 = discount_move_lines.filtered(
            lambda x: x.tax_ids == self.vat20)
        self.assertEqual(discount_line_20.price_unit, -19.29)

    def test_write_invoice_single_tax_with_null_global_discount(self):
        self.invoice_single_tax.write({"global_discount_amount": 0.00})
        self.assertEqual(self.invoice_single_tax.amount_total, 200.00)
        self.assertEqual(self.invoice_single_tax.amount_tax, 20.00)
        #self.assertEqual(self.invoice_single_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_single_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 0)

    def test_write_invoice_multi_tax_with_null_global_discount(self):
        self.invoice_multi_tax.write({"global_discount_amount": 0.00})
        self.assertEqual(self.invoice_multi_tax.amount_untaxed, 350.00)
        self.assertEqual(self.invoice_multi_tax.amount_tax, 50.00)
        self.assertEqual(self.invoice_multi_tax.amount_total, 400.00)
        #self.assertEqual(self.invoice_multi_tax.global_discount_ok, True)
        discount_move_lines = self.env["account.move.line"].search([
            ("product_id", "=", self.discount_product.id),
            ("move_id", "=", self.invoice_multi_tax.id)
        ])
        self.assertEqual(len(discount_move_lines), 0)
