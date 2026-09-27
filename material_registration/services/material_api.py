# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError


MATERIAL_TYPES = ('fabric', 'jeans', 'cotton')
FIELDS = (
    'material_code',
    'material_name',
    'material_type',
    'material_buy_price',
    'supplier_id',
)
FIELD_LABELS = {
    'material_code': 'Material Code',
    'material_name': 'Material Name',
    'material_type': 'Material Type',
    'material_buy_price': 'Material Buy Price',
    'supplier_id': 'Related Supplier',
}


class MaterialNotFoundError(UserError):
    pass


class MaterialApi(object):

    def __init__(self, env):
        self.env = env

    def list_materials(self, material_type=None):
        domain = []
        material_type = self._normalize_type(material_type, allow_empty=True)
        if material_type:
            domain.append(('material_type', '=', material_type))
        records = self.env['material.material'].search(domain)
        return {'success': True, 'data': [self._to_dict(record) for record in records]}

    def get_material(self, material_id):
        record = self._get(material_id)
        return {'success': True, 'data': self._to_dict(record)}

    def create_material(self, payload):
        vals = self._vals_from_payload(payload, partial=False)
        record = self.env['material.material'].create(vals)
        return {
            'success': True,
            'message': 'Material berhasil didaftarkan.',
            'data': self._to_dict(record),
        }

    def update_material(self, material_id, payload):
        record = self._get(material_id)
        vals = self._vals_from_payload(payload, partial=True)
        if not vals:
            raise ValidationError('Tidak ada data yang diubah.')
        record.write(vals)
        return {
            'success': True,
            'message': 'Material berhasil diperbarui.',
            'data': self._to_dict(record),
        }

    def delete_material(self, material_id):
        record = self._get(material_id)
        record.unlink()
        return {'success': True, 'message': 'Material berhasil dihapus.'}

    def list_suppliers(self):
        suppliers = self.env['material.supplier'].search([])
        return {
            'success': True,
            'data': [{'id': supplier.id, 'name': supplier.name} for supplier in suppliers],
        }

    def _get(self, material_id):
        try:
            material_id = int(material_id)
        except (TypeError, ValueError):
            raise MaterialNotFoundError('Material tidak ditemukan.')
        if material_id <= 0:
            raise MaterialNotFoundError('Material tidak ditemukan.')
        record = self.env['material.material'].browse(material_id).exists()
        if not record:
            raise MaterialNotFoundError('Material tidak ditemukan.')
        return record

    def _normalize_type(self, value, allow_empty=False):
        if value is None or value is False:
            if allow_empty:
                return None
            raise ValidationError('Material Type harus salah satu dari: Fabric, Jeans, Cotton.')
        if not isinstance(value, str):
            raise ValidationError('Material Type harus salah satu dari: Fabric, Jeans, Cotton.')
        value = value.strip().lower()
        if not value and allow_empty:
            return None
        if value not in MATERIAL_TYPES:
            raise ValidationError('Material Type harus salah satu dari: Fabric, Jeans, Cotton.')
        return value

    def _vals_from_payload(self, payload, partial):
        if not isinstance(payload, dict):
            raise ValidationError('Body JSON harus berupa object.')
        unknown = [key for key in payload if key not in FIELDS]
        if unknown:
            raise ValidationError('Field tidak dikenal: %s.' % ', '.join(sorted(unknown)))
        if not partial:
            missing = []
            for field_name in FIELDS:
                if field_name not in payload or self._blank(field_name, payload.get(field_name)):
                    missing.append(FIELD_LABELS[field_name])
            if missing:
                raise ValidationError('Field wajib belum diisi: %s.' % ', '.join(missing))

        vals = {}
        if 'material_code' in payload:
            vals['material_code'] = self._text(payload.get('material_code'), 'Material Code wajib diisi.')
        if 'material_name' in payload:
            vals['material_name'] = self._text(payload.get('material_name'), 'Material Name wajib diisi.')
        if 'material_type' in payload:
            vals['material_type'] = self._normalize_type(payload.get('material_type'))
        if 'material_buy_price' in payload:
            vals['material_buy_price'] = self._price(payload.get('material_buy_price'))
        if 'supplier_id' in payload:
            vals['supplier_id'] = self._supplier_id(payload.get('supplier_id'))
        return vals

    def _blank(self, field_name, value):
        if field_name == 'material_buy_price':
            return value is None or value == ''
        if value is None or value is False:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    def _text(self, value, message):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(message)
        return value.strip()

    def _price(self, value):
        if value is None or value == '':
            raise ValidationError('Material Buy Price wajib diisi.')
        if isinstance(value, bool):
            raise ValidationError('Material Buy Price harus berupa angka.')
        if isinstance(value, str):
            value = value.strip()
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValidationError('Material Buy Price harus berupa angka.')
        if value < 100:
            raise ValidationError('Material Buy Price tidak boleh kurang dari 100.')
        return value

    def _supplier_id(self, value):
        if value is None or value is False or value == '':
            raise ValidationError('Related Supplier wajib diisi.')
        if isinstance(value, bool):
            raise ValidationError('Related Supplier tidak valid.')
        if isinstance(value, str):
            value = value.strip()
        try:
            supplier_id = int(value)
        except (TypeError, ValueError):
            raise ValidationError('Related Supplier tidak valid.')
        if supplier_id <= 0:
            raise ValidationError('Related Supplier tidak valid.')
        supplier = self.env['material.supplier'].browse(supplier_id).exists()
        if not supplier:
            raise ValidationError('Related Supplier tidak ditemukan.')
        return supplier.id

    def _to_dict(self, record):
        return {
            'id': record.id,
            'material_code': record.material_code,
            'material_name': record.material_name,
            'material_type': record.material_type,
            'material_buy_price': record.material_buy_price,
            'supplier_id': record.supplier_id.id,
            'supplier_name': record.supplier_id.name,
        }
