# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError

from .common import MaterialCommon


class TestMaterialModel(MaterialCommon):

    def test_create_material_with_valid_values(self):
        record = self.env['material.material'].create(self.payload())
        self.assertEqual(record.material_code, 'MAT-001')
        self.assertEqual(record.material_name, 'Katun Premium')
        self.assertEqual(record.material_type, 'cotton')
        self.assertEqual(record.material_buy_price, 150)
        self.assertEqual(record.supplier_id, self.supplier)

    def test_buy_price_of_100_is_accepted(self):
        record = self.env['material.material'].create(
            self.payload(material_code='MAT-100', material_buy_price=100)
        )
        self.assertEqual(record.material_buy_price, 100)

    def test_buy_price_below_100_is_rejected(self):
        with self.assertRaises(ValidationError) as error:
            self.env['material.material'].create(
                self.payload(material_code='MAT-LOW', material_buy_price=99.99)
            )
        self.assertIn('100', str(error.exception))
        self.assertFalse(self.env['material.material'].search([
            ('material_code', '=', 'MAT-LOW'),
        ]))

    def test_text_values_are_stripped(self):
        record = self.env['material.material'].create(self.payload(
            material_code='  MAT-TRIM  ',
            material_name='  Kain  ',
            material_type=' Fabric ',
        ))
        self.assertEqual(record.material_code, 'MAT-TRIM')
        self.assertEqual(record.material_name, 'Kain')
        self.assertEqual(record.material_type, 'fabric')

    def test_blank_material_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['material.material'].create(
                self.payload(material_name='   ')
            )

    def test_invalid_material_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['material.material'].create(
                self.payload(material_type='silk')
            )

    def test_duplicate_material_code_is_rejected(self):
        self.env['material.material'].create(self.payload())
        with self.assertRaises(ValidationError) as error:
            self.env['material.material'].create(
                self.payload(material_name='Kain Lain')
            )
        self.assertIn('sudah digunakan', str(error.exception))

    def test_unknown_supplier_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env['material.material'].create(
                self.payload(supplier_id=999999)
            )

    def test_update_keeps_previous_price_when_new_price_is_invalid(self):
        record = self.env['material.material'].create(self.payload())
        with self.assertRaises(ValidationError):
            record.write({'material_buy_price': 50})
        record.invalidate_cache()
        self.assertEqual(record.material_buy_price, 150)

    def test_supplier_with_material_cannot_be_deleted(self):
        self.env['material.material'].create(self.payload())
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.supplier.unlink()
        self.assertTrue(self.supplier.exists())

    def test_supplier_name_must_be_unique(self):
        self.env['material.supplier'].create({'name': 'Supplier Unik'})
        with self.assertRaises(ValidationError):
            self.env['material.supplier'].create({'name': 'Supplier Unik'})
