# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class MaterialCommon(TransactionCase):

    def setUp(self):
        super(MaterialCommon, self).setUp()
        self.supplier = self.env['material.supplier'].create({
            'name': 'PT Sumber Kain',
        })

    def payload(self, **overrides):
        values = {
            'material_code': 'MAT-001',
            'material_name': 'Katun Premium',
            'material_type': 'cotton',
            'material_buy_price': 150,
            'supplier_id': self.supplier.id,
        }
        values.update(overrides)
        return values
