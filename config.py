import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Parse admin IDs list
admin_ids_str = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS: list[int] = []
if admin_ids_str:
    for item in admin_ids_str.split(","):
        clean_id = item.strip()
        if clean_id.isdigit():
            ADMIN_IDS.append(int(clean_id))

FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "").strip().lstrip("@")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "").strip()

DB_PATH = BASE_DIR / "rb_drama.db"

def is_admin(user_id: int) -> bool:
    """ពិនិត្យមើលថាតើ user_id គឺជា Admin ឬអត់"""
    return user_id in ADMIN_IDS
