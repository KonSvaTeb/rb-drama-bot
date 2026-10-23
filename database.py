import sqlite3
from typing import Optional, List, Dict, Any
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """បង្កើតតារាងចាំបាច់ក្នុង Database បើមិនទាន់មាន"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # User table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Drama table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dramas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT DEFAULT 'ទូទៅ',
                description TEXT DEFAULT '',
                poster_url TEXT DEFAULT '',
                status TEXT DEFAULT 'កំពុងចាក់ផ្សាយ',
                price TEXT DEFAULT '0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add price column if upgrading from older version
        try:
            cursor.execute("ALTER TABLE dramas ADD COLUMN price TEXT DEFAULT '0'")
        except sqlite3.OperationalError:
            pass

        # Episodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drama_id INTEGER NOT NULL,
                episode_number INTEGER NOT NULL,
                title TEXT DEFAULT '',
                video_url TEXT DEFAULT '',
                file_id TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (drama_id) REFERENCES dramas (id) ON DELETE CASCADE,
                UNIQUE (drama_id, episode_number)
            )
        """)

        # Purchases table (សម្រាប់សំណើទិញរឿង និងផ្ញើ Slip)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                drama_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_slip_file_id TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (drama_id) REFERENCES dramas (id) ON DELETE CASCADE
            )
        """)

        # Settings table (សម្រាប់រក្សាទុកព័ត៌មានបង់ប្រាក់ ABA, Wing...)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Default payment info
        cursor.execute("SELECT value FROM settings WHERE key = 'payment_info'")
        if not cursor.fetchone():
            default_payment = (
                "🏦 **ធនាគារ ABA ៖** `000 123 456` (RB DRAMA)\n"
                "📱 **វីង (Wing) ៖** `012 345 678`\n\n"
                "💰 សូមផ្ញើប្រាក់តាមតម្លៃដែលបានកំណត់ រួចផ្ញើរូបភាពវិក្កយបត្រ (Slip) មកកាន់ទីនេះផ្ទាល់!"
            )
            cursor.execute("INSERT INTO settings (key, value) VALUES ('payment_info', ?)", (default_payment,))

        conn.commit()

# --- Settings Operations ---
def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def set_setting(key: str, value: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        conn.commit()

# --- User Operations ---
def add_or_update_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username, first_name))
        conn.commit()

def get_all_user_ids() -> List[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row["user_id"] for row in cursor.fetchall()]

def get_user_count() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        return cursor.fetchone()["count"]

# --- Drama Operations ---
def add_drama(title: str, genre: str = "ទូទៅ", description: str = "", poster_url: str = "", status: str = "កំពុងចាក់ផ្សាយ", price: str = "0") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dramas (title, genre, description, poster_url, status, price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, genre, description, poster_url, status, price))
        conn.commit()
        return cursor.lastrowid

def is_drama_paid(drama: Optional[Dict[str, Any]]) -> bool:
    """ពិនិត្យមើលថាតើរឿងនេះជាប្រភេទរឿងលក់/VIP ឬអត់"""
    if not drama:
        return False
    price = str(drama.get("price", "0")).strip().lower()
    return price not in ["0", "0$", "$0", "free", "ហ្វ្រី", "មើលហ្វ្រី", ""]

def get_dramas(limit: int = 10, offset: int = 0, paid_only: Optional[bool] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if paid_only is True:
            cursor.execute("""
                SELECT d.*, COUNT(e.id) as episode_count
                FROM dramas d
                LEFT JOIN episodes e ON d.id = e.drama_id
                WHERE d.price NOT IN ('0', '0$', '$0', 'free', 'Free', 'ហ្វ្រី', '')
                GROUP BY d.id
                ORDER BY d.id DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        elif paid_only is False:
            cursor.execute("""
                SELECT d.*, COUNT(e.id) as episode_count
                FROM dramas d
                LEFT JOIN episodes e ON d.id = e.drama_id
                WHERE d.price IN ('0', '0$', '$0', 'free', 'Free', 'ហ្វ្រី', '')
                GROUP BY d.id
                ORDER BY d.id DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        else:
            cursor.execute("""
                SELECT d.*, COUNT(e.id) as episode_count
                FROM dramas d
                LEFT JOIN episodes e ON d.id = e.drama_id
                GROUP BY d.id
                ORDER BY d.id DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_drama_count(paid_only: Optional[bool] = None) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        if paid_only is True:
            cursor.execute("SELECT COUNT(*) as count FROM dramas WHERE price NOT IN ('0', '0$', '$0', 'free', 'Free', 'ហ្វ្រី', '')")
        elif paid_only is False:
            cursor.execute("SELECT COUNT(*) as count FROM dramas WHERE price IN ('0', '0$', '$0', 'free', 'Free', 'ហ្វ្រី', '')")
        else:
            cursor.execute("SELECT COUNT(*) as count FROM dramas")
        return cursor.fetchone()["count"]

def get_drama_by_id(drama_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, COUNT(e.id) as episode_count
            FROM dramas d
            LEFT JOIN episodes e ON d.id = e.drama_id
            WHERE d.id = ?
            GROUP BY d.id
        """, (drama_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def search_dramas(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        like_query = f"%{query}%"
        cursor.execute("""
            SELECT d.*, COUNT(e.id) as episode_count
            FROM dramas d
            LEFT JOIN episodes e ON d.id = e.drama_id
            WHERE d.title LIKE ? OR d.genre LIKE ? OR d.description LIKE ?
            GROUP BY d.id
            ORDER BY d.id DESC
            LIMIT ?
        """, (like_query, like_query, like_query, limit))
        return [dict(row) for row in cursor.fetchall()]

def delete_drama(drama_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM episodes WHERE drama_id = ?", (drama_id,))
        cursor.execute("DELETE FROM user_purchases WHERE drama_id = ?", (drama_id,))
        cursor.execute("DELETE FROM dramas WHERE id = ?", (drama_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- Episode Operations ---
def add_episode(drama_id: int, episode_number: int, title: str = "", video_url: str = "", file_id: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO episodes (drama_id, episode_number, title, video_url, file_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(drama_id, episode_number) DO UPDATE SET
                title = excluded.title,
                video_url = excluded.video_url,
                file_id = excluded.file_id
        """, (drama_id, episode_number, title, video_url, file_id))
        conn.commit()
        return cursor.lastrowid

def get_episodes(drama_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM episodes
            WHERE drama_id = ?
            ORDER BY episode_number ASC
        """, (drama_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_episode(drama_id: int, episode_number: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM episodes
            WHERE drama_id = ? AND episode_number = ?
        """, (drama_id, episode_number))
        row = cursor.fetchone()
        return dict(row) if row else None

# --- Purchase Operations ---
def add_purchase_request(user_id: int, drama_id: int, payment_slip_file_id: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_purchases (user_id, drama_id, status, payment_slip_file_id)
            VALUES (?, ?, 'pending', ?)
        """, (user_id, drama_id, payment_slip_file_id))
        conn.commit()
        return cursor.lastrowid

def get_purchase_by_id(purchase_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, d.title as drama_title, d.price as drama_price, u.first_name, u.username
            FROM user_purchases p
            JOIN dramas d ON p.drama_id = d.id
            LEFT JOIN users u ON p.user_id = u.user_id
            WHERE p.id = ?
        """, (purchase_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_purchase_status(user_id: int, drama_id: int) -> Optional[str]:
    """ត្រួតពិនិត្យស្ថានភាពទិញ៖ 'approved', 'pending', 'rejected', ឬ None"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM user_purchases
            WHERE user_id = ? AND drama_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (user_id, drama_id))
        row = cursor.fetchone()
        return row["status"] if row else None

def update_purchase_status(purchase_id: int, status: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE user_purchases SET status = ? WHERE id = ?", (status, purchase_id))
        conn.commit()
        return cursor.rowcount > 0

def has_user_access(user_id: int, drama_id: int, is_admin_user: bool = False) -> bool:
    """ពិនិត្យថាតើ User មានសិទ្ធិមើលរឿងនេះឬនៅ"""
    if is_admin_user:
        return True
    drama = get_drama_by_id(drama_id)
    if not is_drama_paid(drama):
        return True
    status = get_user_purchase_status(user_id, drama_id)
    return status == "approved"

# --- Statistics ---
def get_stats() -> Dict[str, int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as users_count FROM users")
        users_count = cursor.fetchone()["users_count"]
        cursor.execute("SELECT COUNT(*) as dramas_count FROM dramas")
        dramas_count = cursor.fetchone()["dramas_count"]
        cursor.execute("SELECT COUNT(*) as episodes_count FROM episodes")
        episodes_count = cursor.fetchone()["episodes_count"]
        cursor.execute("SELECT COUNT(*) as purchases_count FROM user_purchases WHERE status = 'approved'")
        purchases_count = cursor.fetchone()["purchases_count"]
        return {
            "users": users_count,
            "dramas": dramas_count,
            "episodes": episodes_count,
            "purchases": purchases_count
        }
