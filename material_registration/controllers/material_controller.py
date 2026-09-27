# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

from ..services.material_api import MaterialApi, MaterialNotFoundError

_logger = logging.getLogger(__name__)


def _json_response(payload, status=200):
    response = request.make_response(
        json.dumps(payload, ensure_ascii=False),
        headers=[('Content-Type', 'application/json; charset=utf-8')],
    )
    response.status_code = status
    return response


def _error_message(exc):
    if not getattr(exc, 'args', None):
        return 'Terjadi kesalahan pada server.'
    message = exc.args[0]
    if isinstance(message, (list, tuple)):
        return ' '.join(str(part) for part in message if part)
    return str(message)


def _json_body():
    raw = request.httprequest.get_data(as_text=True)
    if raw is None:
        raw = ''
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    if not isinstance(raw, str):
        raise ValidationError('Body harus berupa JSON yang valid.')
    raw = raw.strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        raise ValidationError('Body harus berupa JSON yang valid.')
    if not isinstance(data, dict):
        raise ValidationError('Body JSON harus berupa object.')
    return data


def _dispatch(callback):
    try:
        api = MaterialApi(request.env(su=True))
        payload, status = callback(api)
        return _json_response(payload, status)
    except MaterialNotFoundError as exc:
        return _json_response({'success': False, 'message': _error_message(exc)}, 404)
    except (ValidationError, UserError, ValueError) as exc:
        return _json_response({'success': False, 'message': _error_message(exc)}, 400)
    except AccessError as exc:
        return _json_response({'success': False, 'message': _error_message(exc)}, 403)
    except Exception:
        _logger.exception('Material API failed')
        return _json_response({'success': False, 'message': 'Terjadi kesalahan pada server.'}, 500)


class MaterialController(http.Controller):

    @http.route(
        '/api/materials',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False,
        cors='*',
    )
    def list_materials(self, **kwargs):
        material_type = kwargs.get('material_type')
        return _dispatch(lambda api: (api.list_materials(material_type=material_type), 200))

    @http.route(
        '/api/materials',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False,
        cors='*',
    )
    def create_material(self, **kwargs):
        def action(api):
            return api.create_material(_json_body()), 201
        return _dispatch(action)

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False,
        cors='*',
    )
    def get_material(self, material_id, **kwargs):
        return _dispatch(lambda api: (api.get_material(material_id), 200))

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['PUT'],
        csrf=False,
        cors='*',
    )
    def update_material(self, material_id, **kwargs):
        def action(api):
            return api.update_material(material_id, _json_body()), 200
        return _dispatch(action)

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['DELETE'],
        csrf=False,
        cors='*',
    )
    def delete_material(self, material_id, **kwargs):
        return _dispatch(lambda api: (api.delete_material(material_id), 200))

    @http.route(
        '/api/suppliers',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False,
        cors='*',
    )
    def list_suppliers(self, **kwargs):
        return _dispatch(lambda api: (api.list_suppliers(), 200))
