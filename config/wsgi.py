import os
import shutil
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# On Vercel, copy pre-seeded database to /tmp if using SQLite
if os.environ.get('VERCEL'):
    base_dir = Path(__file__).resolve().parent.parent
    src_db = base_dir / 'db.sqlite3'
    dst_db = Path('/tmp/db.sqlite3')
    if src_db.exists() and not dst_db.exists():
        try:
            shutil.copyfile(src_db, dst_db)
        except Exception:
            pass

application = get_wsgi_application()
