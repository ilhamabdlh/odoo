# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

MATERIAL_TYPES = [
    ('fabric', 'Fabric'),
    ('jeans', 'Jeans'),
    ('cotton', 'Cotton'),
]


class Material(models.Model):
    _name = 'material.material'
    _description = 'Material'
    _order = 'material_code, id'
    _rec_name = 'material_name'

    material_code = fields.Char(string='Material Code', required=True, index=True)
    material_name = fields.Char(string='Material Name', required=True)
    material_type = fields.Selection(MATERIAL_TYPES, string='Material Type', required=True)
    material_buy_price = fields.Float(
        string='Material Buy Price',
        required=True,
        help='Tidak boleh kurang dari 100.',
    )
    supplier_id = fields.Many2one(
        'material.supplier',
        string='Related Supplier',
        required=True,
        ondelete='restrict',
    )

    _sql_constraints = [
        ('material_code_uniq', 'unique(material_code)', 'Material Code harus unik.'),
        ('material_buy_price_min', 'CHECK(material_buy_price >= 100)', 'Material Buy Price tidak boleh kurang dari 100.'),
    ]

    @api.constrains('material_buy_price')
    def _check_material_buy_price(self):
        for material in self:
            if material.material_buy_price < 100:
                raise ValidationError('Material Buy Price tidak boleh kurang dari 100.')

    @api.constrains('material_code', 'material_name')
    def _check_required_text(self):
        for material in self:
            if not (material.material_code or '').strip():
                raise ValidationError('Material Code wajib diisi.')
            if not (material.material_name or '').strip():
                raise ValidationError('Material Name wajib diisi.')

    @api.model
    def create(self, vals):
        vals = self._clean_vals(vals)
        self._check_vals(vals)
        return super(Material, self).create(vals)

    def write(self, vals):
        vals = self._clean_vals(vals)
        self._check_vals(vals, current=self)
        return super(Material, self).write(vals)

    def _clean_vals(self, vals):
        vals = dict(vals)
        for field_name in ('material_code', 'material_name', 'material_type'):
            if isinstance(vals.get(field_name), str):
                vals[field_name] = vals[field_name].strip()
        if isinstance(vals.get('material_type'), str):
            vals['material_type'] = vals['material_type'].lower()
        return vals

    def _check_vals(self, vals, current=None):
        if 'material_code' in vals and not vals.get('material_code'):
            raise ValidationError('Material Code wajib diisi.')
        if 'material_name' in vals and not vals.get('material_name'):
            raise ValidationError('Material Name wajib diisi.')
        if 'material_type' in vals and vals.get('material_type') not in dict(MATERIAL_TYPES):
            raise ValidationError('Material Type harus salah satu dari: Fabric, Jeans, Cotton.')
        if 'material_buy_price' in vals and vals.get('material_buy_price') < 100:
            raise ValidationError('Material Buy Price tidak boleh kurang dari 100.')
        if 'supplier_id' in vals:
            supplier = self.env['material.supplier'].browse(vals.get('supplier_id')).exists()
            if not supplier:
                raise ValidationError('Related Supplier tidak ditemukan.')
        code = vals.get('material_code')
        if code:
            domain = [('material_code', '=', code)]
            if current:
                domain.append(('id', 'not in', current.ids))
            if self.search(domain, limit=1):
                raise ValidationError('Material Code "%s" sudah digunakan.' % code)
