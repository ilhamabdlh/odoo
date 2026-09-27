# Material Registration

Modul Odoo 14 untuk registrasi material yang akan dijual.

Field yang disimpan: Material Code, Material Name, Material Type (Fabric, Jeans, Cotton), Material Buy Price, dan Related Supplier. Semua wajib diisi. Material Buy Price di bawah 100 ditolak. Nilai 100 masih diterima.

ERD: [docs/ERD.pdf](docs/ERD.pdf)

## Install

Masukkan folder project ini ke `addons_path`, lalu install `material_registration`.

Dengan Docker:

```bash
docker compose up -d
docker compose run --rm web odoo -d keda --db_host=db --db_user=odoo --db_password=odoo -i material_registration --without-demo=all --stop-after-init
docker compose up -d
```

Buka http://localhost:8069, database `keda`.

Supplier yang ikut terpasang: PT Tekstil Nusantara, CV Denim Jaya, dan PT Kapas Indonesia.

Tanpa Docker juga bisa selama Odoo 14 (Python 3.6–3.8) dan PostgreSQL sudah jalan. Langkah install modulnya sama.

## API

Header: `Content-Type: application/json`

```text
GET    /api/suppliers
GET    /api/materials
GET    /api/materials?material_type=fabric
GET    /api/materials/<id>
POST   /api/materials
PUT    /api/materials/<id>
DELETE /api/materials/<id>
```

`material_type` untuk filter: `fabric`, `jeans`, atau `cotton`.

```bash
curl -X POST http://localhost:8069/api/materials \
  -H 'Content-Type: application/json' \
  -d '{"material_code":"MAT-001","material_name":"Katun Premium","material_type":"cotton","material_buy_price":150,"supplier_id":1}'
```

`supplier_id` diambil dari `GET /api/suppliers`. Pada PUT, field yang tidak dikirim tidak berubah.

## Unit test

```bash
docker compose run --rm web odoo -d keda_test --db_host=db --db_user=odoo --db_password=odoo -i material_registration --test-enable --stop-after-init --without-demo=all
```

Kalau Odoo sudah terpasang di mesin:

```bash
./odoo-bin -d keda_test -i material_registration --test-enable --stop-after-init --without-demo=all
```
