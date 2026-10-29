#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Loading product fixtures ==="
python manage.py loaddata store/fixtures/products.json || echo "Fixture load skipped (already loaded or error)"

echo "=== Build complete ==="
