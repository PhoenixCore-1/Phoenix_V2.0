"""Create a local development database. Never commit the resulting file."""

from pathlib import Path
from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.services import CoreFoundationService

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / ".local"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "phoenix_core_v2_dev.db"

db = SQLiteDatabase(DB_PATH)
CoreFoundationService(db).initialise()
db.close()
print(f"Initialized {DB_PATH}")
