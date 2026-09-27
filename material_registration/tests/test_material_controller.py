# -*- coding: utf-8 -*-
import json

from werkzeug.wrappers import Response

from ..controllers.material_controller import MaterialController
from .common import MaterialCommon


def _make_response(data, headers=None, cookies=None):
    return Response(data, headers=headers)


class TestMaterialController(MaterialCommon):

    def setUp(self):
        super(TestMaterialController, self).setUp()
        self.controller = MaterialController()
        # Patch the request name used by the controller, not the HTTP proxy.
        from unittest.mock import patch
        self.patcher = patch(
            'odoo.addons.material_registration.controllers.material_controller.request'
        )
        self.request = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.request.env = self.env
        self.request.make_response.side_effect = _make_response
        self.request.httprequest.get_data.return_value = '{}'

    def _call(self, method_name, *args, **kwargs):
        method = getattr(MaterialController, method_name)
        return method.original_func(self.controller, *args, **kwargs)

    def _json(self, response):
        return json.loads(response.get_data(as_text=True))

    def test_routes_match_the_material_api(self):
        expected = {
            'list_materials': ('/api/materials', 'GET'),
            'create_material': ('/api/materials', 'POST'),
            'get_material': ('/api/materials/<int:material_id>', 'GET'),
            'update_material': ('/api/materials/<int:material_id>', 'PUT'),
            'delete_material': ('/api/materials/<int:material_id>', 'DELETE'),
            'list_suppliers': ('/api/suppliers', 'GET'),
        }
        for method_name, (path, http_method) in expected.items():
            routing = getattr(MaterialController, method_name).routing
            self.assertIn(path, routing['routes'])
            self.assertIn(http_method, routing['methods'])
            self.assertEqual(routing['auth'], 'public')
            self.assertFalse(routing['csrf'])

    def test_http_register_filter_update_and_delete(self):
        self.request.httprequest.get_data.return_value = json.dumps(self.payload(
            material_code='HTTP-1',
            material_type='cotton',
        ))
        created_response = self._call('create_material')
        self.assertEqual(created_response.status_code, 201)
        created = self._json(created_response)
        material_id = created['data']['id']
        self.assertEqual(created['data']['material_code'], 'HTTP-1')

        listed = self._json(self._call('list_materials', material_type='cotton'))
        self.assertTrue(any(item['id'] == material_id for item in listed['data']))

        denied = self._call('list_materials', material_type='silk')
        self.assertEqual(denied.status_code, 400)

        self.request.httprequest.get_data.return_value = json.dumps({
            'material_buy_price': 50,
        })
        rejected = self._call('update_material', material_id)
        self.assertEqual(rejected.status_code, 400)
        self.assertFalse(self.env['material.material'].browse(material_id).material_buy_price == 50)

        self.request.httprequest.get_data.return_value = json.dumps({
            'material_name': 'Kapas HTTP',
        })
        updated = self._call('update_material', material_id)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self._json(updated)['data']['material_name'], 'Kapas HTTP')

        deleted = self._call('delete_material', material_id)
        self.assertEqual(deleted.status_code, 200)
        missing = self._call('get_material', material_id)
        self.assertEqual(missing.status_code, 404)

    def test_invalid_json_returns_400_and_does_not_create_material(self):
        self.request.httprequest.get_data.return_value = '{bukan-json'
        response = self._call('create_material')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self._json(response)['success'])
        self.assertFalse(self.env['material.material'].search([]))

    def test_price_below_minimum_returns_400_without_persisting(self):
        self.request.httprequest.get_data.return_value = json.dumps(
            self.payload(material_code='TOO-CHEAP', material_buy_price=99)
        )
        response = self._call('create_material')
        self.assertEqual(response.status_code, 400)
        self.assertIn('100', self._json(response)['message'])
        self.assertFalse(self.env['material.material'].search([
            ('material_code', '=', 'TOO-CHEAP'),
        ]))
