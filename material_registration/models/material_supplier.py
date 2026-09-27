# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MaterialSupplier(models.Model):
    _name = 'material.supplier'
    _description = 'Material Supplier'
    _order = 'name, id'

    name = fields.Char(string='Supplier Name', required=True)
    material_ids = fields.One2many('material.material', 'supplier_id', string='Materials')

    _sql_constraints = [
        ('supplier_name_uniq', 'unique(name)', 'Nama supplier harus unik.'),
    ]

    @api.constrains('name')
    def _check_name(self):
        for supplier in self:
            if not (supplier.name or '').strip():
                raise ValidationError('Nama supplier wajib diisi.')

    @api.model
    def create(self, vals):
        vals = self._prepare_name(vals)
        self._check_unique_name(vals.get('name'))
        return super(MaterialSupplier, self).create(vals)

    def write(self, vals):
        vals = self._prepare_name(vals)
        if 'name' in vals:
            for supplier in self:
                supplier._check_unique_name(vals.get('name'), exclude_id=supplier.id)
        return super(MaterialSupplier, self).write(vals)

    def _prepare_name(self, vals):
        vals = dict(vals)
        if isinstance(vals.get('name'), str):
            vals['name'] = vals['name'].strip()
        return vals

    def _check_unique_name(self, name, exclude_id=None):
        if not name:
            raise ValidationError('Nama supplier wajib diisi.')
        domain = [('name', '=', name)]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        if self.search(domain, limit=1):
            raise ValidationError('Nama supplier "%s" sudah digunakan.' % name)
