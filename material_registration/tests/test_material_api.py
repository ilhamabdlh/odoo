# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError

from ..services.material_api import MaterialApi, MaterialNotFoundError
from .common import MaterialCommon


class TestMaterialApi(MaterialCommon):

    def setUp(self):
        super(TestMaterialApi, self).setUp()
        self.api = MaterialApi(self.env)

    def test_create_list_filter_update_and_delete(self):
        self.api.create_material(self.payload(
            material_code='FAB-1',
            material_name='Kain Fabric',
            material_type='fabric',
        ))
        jeans = self.api.create_material(self.payload(
            material_code='JNS-1',
            material_name='Kain Jeans',
            material_type='Jeans',
            material_buy_price='180',
        ))
        self.assertEqual(jeans['data']['material_type'], 'jeans')
        self.assertEqual(jeans['data']['material_buy_price'], 180)
        self.assertEqual(jeans['data']['supplier_name'], 'PT Sumber Kain')

        fabric_only = self.api.list_materials(material_type='Fabric')
        codes = [item['material_code'] for item in fabric_only['data']]
        self.assertIn('FAB-1', codes)
        self.assertNotIn('JNS-1', codes)
        self.assertTrue(all(item['material_type'] == 'fabric' for item in fabric_only['data']))

        updated = self.api.update_material(jeans['data']['id'], {
            'material_name': 'Jeans Premium',
        })
        self.assertEqual(updated['data']['material_name'], 'Jeans Premium')
        self.assertEqual(updated['data']['material_code'], 'JNS-1')
        self.assertEqual(updated['data']['material_buy_price'], 180)

        deleted = self.api.delete_material(jeans['data']['id'])
        self.assertTrue(deleted['success'])
        self.assertTrue(self.env['material.material'].search([
            ('material_code', '=', 'FAB-1'),
        ]))
        with self.assertRaises(MaterialNotFoundError):
            self.api.get_material(jeans['data']['id'])

    def test_buy_price_boundary(self):
        created = self.api.create_material(
            self.payload(material_code='MAT-100', material_buy_price=100)
        )
        self.assertEqual(created['data']['material_buy_price'], 100)
        with self.assertRaises(ValidationError) as error:
            self.api.create_material(
                self.payload(material_code='MAT-99', material_buy_price=99)
            )
        self.assertIn('100', str(error.exception))

    def test_create_requires_every_field(self):
        payload = self.payload()
        payload.pop('material_name')
        payload.pop('supplier_id')
        with self.assertRaises(ValidationError) as error:
            self.api.create_material(payload)
        message = str(error.exception)
        self.assertIn('Material Name', message)
        self.assertIn('Related Supplier', message)

    def test_unknown_field_is_rejected(self):
        with self.assertRaises(ValidationError) as error:
            self.api.create_material(self.payload(extra='nope'))
        self.assertIn('extra', str(error.exception))

    def test_invalid_type_filter_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.api.list_materials(material_type='silk')

    def test_empty_filter_returns_every_material(self):
        self.api.create_material(self.payload(material_code='FAB-2', material_type='fabric'))
        self.api.create_material(self.payload(
            material_code='COT-2',
            material_type='cotton',
            material_name='Kapas',
        ))
        result = self.api.list_materials(material_type='   ')
        codes = {item['material_code'] for item in result['data']}
        self.assertIn('FAB-2', codes)
        self.assertIn('COT-2', codes)

    def test_update_rejects_price_below_minimum_without_changing_record(self):
        created = self.api.create_material(self.payload())
        with self.assertRaises(ValidationError):
            self.api.update_material(created['data']['id'], {'material_buy_price': 10})
        record = self.env['material.material'].browse(created['data']['id'])
        self.assertEqual(record.material_buy_price, 150)

    def test_empty_update_is_rejected(self):
        created = self.api.create_material(self.payload())
        with self.assertRaises(ValidationError):
            self.api.update_material(created['data']['id'], {})

    def test_missing_material_cannot_be_deleted(self):
        with self.assertRaises(MaterialNotFoundError):
            self.api.delete_material(999999)

    def test_supplier_string_id_is_accepted(self):
        created = self.api.create_material(
            self.payload(supplier_id=str(self.supplier.id), material_code='MAT-SUP')
        )
        self.assertEqual(created['data']['supplier_id'], self.supplier.id)

    def test_list_suppliers_contains_master_data(self):
        result = self.api.list_suppliers()
        names = {item['name'] for item in result['data']}
        self.assertIn('PT Sumber Kain', names)
        self.assertIn('PT Tekstil Nusantara', names)
        self.assertIn('CV Denim Jaya', names)
        self.assertIn('PT Kapas Indonesia', names)
