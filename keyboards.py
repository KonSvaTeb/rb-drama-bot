from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional
import math

def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """មឺនុយមេ"""
    keyboard = [
        [InlineKeyboardButton("🎬 មើលបញ្ជីរឿងទាំងអស់", callback_data="dramas_page_0")],
        [
            InlineKeyboardButton("💎 រឿង VIP / សម្រាប់លក់", callback_data="paid_dramas_0"),
            InlineKeyboardButton("🎁 រឿងមើលហ្វ្រី (Free)", callback_data="free_dramas_0")
        ],
        [
            InlineKeyboardButton("🔍 ស្វែងរកតាមឈ្មោះ", callback_data="search_drama"),
            InlineKeyboardButton("⭐️ រឿងថ្មីៗ", callback_data="recent_dramas")
        ],
        [InlineKeyboardButton("ℹ️ ជំនួយ និងរបៀបទិញរឿង", callback_data="help_menu")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("👑 ផ្ទាំងគ្រប់គ្រង Admin", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def drama_list_keyboard(
    dramas: List[Dict[str, Any]],
    page: int,
    total_count: int,
    page_size: int = 6,
    prefix: str = "dramas_page"
) -> InlineKeyboardMarkup:
    """បញ្ជីរឿងជាមួយស្លាកតម្លៃ (Free / VIP) និង Pagination"""
    keyboard = []
    
    for drama in dramas:
        ep_count = drama.get("episode_count", 0)
        price = str(drama.get("price", "0")).strip()
        is_paid = price not in ["0", "0$", "$0", "free", "Free", "ហ្វ្រី", ""]
        tag = f"💎 [{price}]" if is_paid else "🎁 [Free]"
        title = f"{tag} {drama['title']} ({ep_count} ភាគ)"
        keyboard.append([InlineKeyboardButton(title, callback_data=f"view_drama_{drama['id']}")])
        
    total_pages = max(1, math.ceil(total_count / page_size))
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ ថយក្រោយ", callback_data=f"{prefix}_{page - 1}"))
    
    nav_row.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    
    if page + 1 < total_pages:
        nav_row.append(InlineKeyboardButton("បន្ទាប់ ▶️", callback_data=f"{prefix}_{page + 1}"))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ទៅមឺនុយដើម", callback_data="back_home")])
    return InlineKeyboardMarkup(keyboard)

def drama_detail_keyboard(
    drama: Dict[str, Any],
    episodes: List[Dict[str, Any]],
    is_admin: bool = False,
    has_access: bool = True,
    purchase_status: Optional[str] = None
) -> InlineKeyboardMarkup:
    """ផ្ទាំងលម្អិតនៃរឿង៖ បើមិនទាន់ទិញ បង្ហាញប៊ូតុងទិញ / បើទិញហើយ បង្ហាញភាគ"""
    keyboard = []
    drama_id = drama["id"]
    price = str(drama.get("price", "0")).strip()

    if not has_access:
        # User មិនទាន់មានសិទ្ធិមើលរឿងលក់
        if purchase_status == "pending":
            keyboard.append([InlineKeyboardButton("⏳ វិក្កយបត្រកំពុងស្ថិតក្នុងការត្រួតពិនិត្យ...", callback_data="noop")])
        else:
            keyboard.append([InlineKeyboardButton(f"💳 បង់ប្រាក់ទិញរឿង ({price}) & ផ្ញើវិក្កយបត្រ", callback_data=f"buy_drama_{drama_id}")])
    else:
        # មានសិទ្ធិមើល (រឿង Free ឬ បានទិញរួច ឬ Admin)
        if episodes:
            row = []
            for ep in episodes:
                ep_num = ep["episode_number"]
                row.append(InlineKeyboardButton(f"ភាគ {ep_num}", callback_data=f"ep_{drama_id}_{ep_num}"))
                if len(row) == 5:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
        else:
            keyboard.append([InlineKeyboardButton("⚠️ មិនទាន់មានភាគនៅឡើយទេ", callback_data="noop")])
        
    # Admin controls
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("➕ បន្ថែមភាគថ្មី", callback_data=f"admin_add_ep_{drama_id}"),
            InlineKeyboardButton("🗑 លុបរឿងនេះ", callback_data=f"admin_del_drama_{drama_id}")
        ])
        
    keyboard.append([
        InlineKeyboardButton("🎬 មើលរឿងផ្សេងទៀត", callback_data="dramas_page_0"),
        InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")
    ])
    return InlineKeyboardMarkup(keyboard)

def episode_detail_keyboard(drama_id: int, episode_number: int, video_url: str = "", total_episodes: int = 1) -> InlineKeyboardMarkup:
    """ផ្ទាំងព័ត៌មានភាគរឿង និងប៊ូតុងបញ្ជា"""
    keyboard = []
    
    if video_url:
        keyboard.append([InlineKeyboardButton("▶️ ចុចទីនេះដើម្បីទស្សនាវីដេអូ", url=video_url)])
        
    nav_row = []
    if episode_number > 1:
        nav_row.append(InlineKeyboardButton("⏮ ភាគមុន", callback_data=f"ep_{drama_id}_{episode_number - 1}"))
    if episode_number < total_episodes:
        nav_row.append(InlineKeyboardButton("ភាគបន្ទាប់ ⏭", callback_data=f"ep_{drama_id}_{episode_number + 1}"))
        
    if nav_row:
        keyboard.append(nav_row)
        
    keyboard.append([
        InlineKeyboardButton("📋 បញ្ជីភាគទាំងអស់", callback_data=f"view_drama_{drama_id}"),
        InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")
    ])
    return InlineKeyboardMarkup(keyboard)

def purchase_admin_approval_keyboard(purchase_id: int) -> InlineKeyboardMarkup:
    """ប៊ូតុងសម្រាប់ Admin អនុម័ត ឬបដិសេធវិក្កយបត្រ"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ អនុម័ត (Approve)", callback_data=f"admin_appr_pur_{purchase_id}"),
            InlineKeyboardButton("❌ បដិសេធ (Reject)", callback_data=f"admin_rej_pur_{purchase_id}")
        ]
    ])

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """ផ្ទាំងបញ្ជា Admin"""
    keyboard = [
        [InlineKeyboardButton("➕ បង្ហោះរឿងថ្មី (Add Drama & Set Price)", callback_data="admin_add_drama")],
        [InlineKeyboardButton("🎬 គ្រប់គ្រង និងបន្ថែមភាគរឿង", callback_data="admin_manage_dramas")],
        [InlineKeyboardButton("🏦 កំណត់ព័ត៌មានបង់ប្រាក់ (ABA / Wing)", callback_data="admin_set_payment")],
        [InlineKeyboardButton("📢 ផ្ញើសារ Broadcast ទៅកាន់សមាជិកទាំងអស់", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 ស្ថិតិទូទៅ (Stats & Purchases)", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 ត្រឡប់ទៅមឺនុយដើម", callback_data="back_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def force_sub_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ចូលរួម Channel (Join)", url=channel_link)],
        [InlineKeyboardButton("✅ ខ្ញុំបាន Join រួចហើយ (Check)", callback_data="check_sub")]
    ])

def cancel_keyboard(back_to: str = "admin_panel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ បោះបង់ (Cancel)", callback_data=back_to)]])
