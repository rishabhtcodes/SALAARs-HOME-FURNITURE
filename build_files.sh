#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Loading seed data ==="
python manage.py loaddata store/fixtures/products.json store/fixtures/faqs.json store/fixtures/navigation.json

echo "=== Build complete ==="

