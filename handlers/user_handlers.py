import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import BadRequest

import database as db
import keyboards as kb
from config import FORCE_SUB_CHANNEL, CHANNEL_LINK, ADMIN_IDS, is_admin

logger = logging.getLogger(__name__)

async def is_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """ពិនិត្យមើលថាតើអ្នកប្រើប្រាស់បាន Join Channel ឬនៅ"""
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        chat_member = await context.bot.get_chat_member(f"@{FORCE_SUB_CHANNEL}", user_id)
        return chat_member.status in ["creator", "administrator", "member", "restricted"]
    except Exception as e:
        logger.warning(f"Error checking channel subscription for user {user_id}: {e}")
        return True

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """បញ្ជា /start ពេលអ្នកប្រើប្រាស់បើក Bot ដំបូង"""
    user = update.effective_user
    if not user:
        return

    db.add_or_update_user(user.id, user.username, user.first_name)

    subscribed = await is_subscribed(context, user.id)
    if not subscribed:
        channel_url = CHANNEL_LINK if CHANNEL_LINK else f"https://t.me/{FORCE_SUB_CHANNEL}"
        await update.message.reply_text(
            f"👋 សួស្តី **{user.first_name}**!\n\n"
            f"⚠️ ដើម្បីអាចទស្សនារឿងក្នុង **RB Drama** បាន សូមចូលរួម (Join) ឆានែលរបស់យើងជាមុនសិន។\n\n"
            f"ចុចប៊ូតុងខាងក្រោមដើម្បីចូលរួម រួចចុច **ពិនិត្យឡើងវិញ** ៖",
            reply_markup=kb.force_sub_keyboard(channel_url),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    admin_status = is_admin(user.id)
    welcome_text = (
        f"🎬 **សូមស្វាគមន៍មកកាន់ RB Drama!** 🍿\n\n"
        f"សួស្តី {user.first_name}! យើងខ្ញុំមានរឿងភាគល្អៗ ទាំងរឿងភាគចិន កូរ៉េ ថៃ រឿងហ្វ្រី និងរឿង VIP ពិសេសៗជាច្រើន។\n\n"
        f"📌 សូមជ្រើសរើសជម្រើសខាងក្រោមដើម្បីចាប់ផ្តើមទស្សនា៖"
    )

    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=kb.main_menu_keyboard(admin_status),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=kb.main_menu_keyboard(admin_status),
            parse_mode=ParseMode.MARKDOWN
        )

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    subscribed = await is_subscribed(context, user_id)
    if subscribed:
        await query.answer("✅ អរគុណសម្រាប់ការចូលរួម!", show_alert=True)
        admin_status = is_admin(user_id)
        welcome_text = (
            f"🎬 **សូមស្វាគមន៍មកកាន់ RB Drama!** 🍿\n\n"
            f"សូមជ្រើសរើសជម្រើសខាងក្រោមដើម្បីចាប់ផ្តើមទស្សនា៖"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=kb.main_menu_keyboard(admin_status),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.answer("❌ អ្នកមិនទាន់បាន Join Channel នៅឡើយទេ!", show_alert=True)

async def back_home_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    admin_status = is_admin(user.id)

    welcome_text = (
        f"🎬 **មឺនុយដើម RB Drama**\n\n"
        f"សូមជ្រើសរើសជម្រើសខាងក្រោមដើម្បីស្វែងរក និងទស្សនារឿង៖"
    )
    try:
        await query.edit_message_text(
            welcome_text,
            reply_markup=kb.main_menu_keyboard(admin_status),
            parse_mode=ParseMode.MARKDOWN
        )
    except BadRequest:
        pass

async def dramas_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """បញ្ជីរឿងទាំងអស់"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[-1])
    page_size = 6
    offset = page * page_size

    dramas = db.get_dramas(limit=page_size, offset=offset)
    total_count = db.get_drama_count()

    if not dramas:
        text = "🎬 **បញ្ជីរឿងក្នុង RB Drama**\n\n⚠️ បច្ចុប្បន្នមិនទាន់មានរឿងនៅក្នុងប្រព័ន្ធនៅឡើយទេ។"
        await query.edit_message_text(
            text,
            reply_markup=kb.main_menu_keyboard(is_admin(query.from_user.id)),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = f"🎬 **បញ្ជីរឿងទាំងអស់ (សរុប {total_count} រឿង) ៖**\n\nសូមចុចលើចំណងជើងរឿងដើម្បីមើលព័ត៌មាន និងភាគរឿងនីមួយៗ៖"
    await query.edit_message_text(
        text,
        reply_markup=kb.drama_list_keyboard(dramas, page, total_count, page_size, prefix="dramas_page"),
        parse_mode=ParseMode.MARKDOWN
    )

async def paid_dramas_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """បង្ហាញតែរឿងសម្រាប់លក់ (VIP)"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[-1])
    page_size = 6
    offset = page * page_size

    dramas = db.get_dramas(limit=page_size, offset=offset, paid_only=True)
    total_count = db.get_drama_count(paid_only=True)

    if not dramas:
        text = "💎 **រឿងសម្រាប់លក់ / VIP**\n\n⚠️ បច្ចុប្បន្នមិនទាន់មានរឿង VIP នៅឡើយទេ។"
        await query.edit_message_text(
            text,
            reply_markup=kb.main_menu_keyboard(is_admin(query.from_user.id)),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = f"💎 **បញ្ជីរឿងសម្រាប់លក់ / VIP (សរុប {total_count} រឿង) ៖**\n\nរឿងទាំងនេះតម្រូវឱ្យបង់ប្រាក់ទិញមុននឹងអាចទស្សនាបាន ៖"
    await query.edit_message_text(
        text,
        reply_markup=kb.drama_list_keyboard(dramas, page, total_count, page_size, prefix="paid_dramas"),
        parse_mode=ParseMode.MARKDOWN
    )

async def free_dramas_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """បង្ហាញតែរឿងមើលហ្វ្រី (Free)"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[-1])
    page_size = 6
    offset = page * page_size

    dramas = db.get_dramas(limit=page_size, offset=offset, paid_only=False)
    total_count = db.get_drama_count(paid_only=False)

    if not dramas:
        text = "🎁 **រឿងមើលហ្វ្រី (Free)**\n\n⚠️ បច្ចុប្បន្នមិនទាន់មានរឿងហ្វ្រីនៅឡើយទេ។"
        await query.edit_message_text(
            text,
            reply_markup=kb.main_menu_keyboard(is_admin(query.from_user.id)),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = f"🎁 **បញ្ជីរឿងមើលហ្វ្រី (សរុប {total_count} រឿង) ៖**\n\nលោកអ្នកអាចចុចទស្សនាបានភ្លាមៗដោយឥតគិតថ្លៃ ៖"
    await query.edit_message_text(
        text,
        reply_markup=kb.drama_list_keyboard(dramas, page, total_count, page_size, prefix="free_dramas"),
        parse_mode=ParseMode.MARKDOWN
    )

async def recent_dramas_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dramas = db.get_dramas(limit=5, offset=0)
    total_count = db.get_drama_count()

    if not dramas:
        text = "⭐️ **រឿងថ្មីៗក្នុង RB Drama**\n\n⚠️ មិនទាន់មានរឿងថ្មីៗនៅឡើយទេ។"
        await query.edit_message_text(
            text,
            reply_markup=kb.main_menu_keyboard(is_admin(query.from_user.id)),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = "⭐️ **រឿងដែលបានដាក់បញ្ចូលថ្មីៗ ៖**\n\nសូមចុចដើម្បីទស្សនា៖"
    await query.edit_message_text(
        text,
        reply_markup=kb.drama_list_keyboard(dramas, 0, total_count, 6),
        parse_mode=ParseMode.MARKDOWN
    )

async def view_drama_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """បង្ហាញព័ត៌មានលម្អិតនៃរឿង និងផ្ទៀងផ្ទាត់សិទ្ធិទិញ"""
    query = update.callback_query
    await query.answer()

    drama_id = int(query.data.split("_")[-1])
    drama = db.get_drama_by_id(drama_id)

    if not drama:
        await query.edit_message_text(
            "❌ រឿងនេះមិនមានក្នុងប្រព័ន្ធ ឬត្រូវបានលុបចេញហើយ។",
            reply_markup=kb.main_menu_keyboard(is_admin(query.from_user.id))
        )
        return

    user_id = query.from_user.id
    admin_status = is_admin(user_id)
    has_access = db.has_user_access(user_id, drama_id, admin_status)
    purchase_status = db.get_user_purchase_status(user_id, drama_id)

    price_str = str(drama.get("price", "0")).strip()
    is_paid = db.is_drama_paid(drama)

    episodes = db.get_episodes(drama_id)

    price_badge = f"💎 {price_str} (VIP/លក់)" if is_paid else "🎁 មើលហ្វ្រី (Free)"
    
    caption = (
        f"🎬 **ចំណងជើង:** {drama['title']}\n"
        f"🎭 **ប្រភេទ:** {drama.get('genre', 'ទូទៅ')}\n"
        f"💰 **តម្លៃ:** {price_badge}\n"
        f"📌 **ស្ថានភាព:** {drama.get('status', 'កំពុងចាក់ផ្សាយ')}\n"
        f"🎞 **ភាគសរុប:** {len(episodes)} ភាគ\n\n"
        f"📝 **សង្ខេបរឿង:**\n{drama.get('description', 'គ្មានការពិពណ៌នា')}\n\n"
    )

    if not has_access:
        payment_info = db.get_setting("payment_info")
        if purchase_status == "pending":
            caption += (
                "⏳ **ស្ថានភាព ៖** វិក្កយបត្ររបស់អ្នកកំពុងស្ថិតក្នុងការពិនិត្យដោយ Admin។\n"
                "សូមរង់ចាំបន្តិច នៅពេល Admin អនុម័ត Bot នឹងផ្ញើសារជូនដំណឹងភ្លាមៗ!\n"
            )
        else:
            caption += (
                "🔒 **រឿងនេះជាប្រភេទរឿង VIP សម្រាប់លក់!**\n"
                "ដើម្បីទស្សនាភាគទាំងអស់ សូមធ្វើការផ្ញើប្រាក់តាមរយៈ ៖\n\n"
                f"{payment_info}\n\n"
                f"👉 រួចចុចប៊ូតុង **💳 បង់ប្រាក់ទិញរឿង ({price_str})** ខាងក្រោម ដើម្បីផ្ញើរូបភាពវិក្កយបត្រ (Slip)!"
            )
    else:
        caption += "👇 **សូមជ្រើសរើសភាគដើម្បីទស្សនា៖**"

    markup = kb.drama_detail_keyboard(drama, episodes, admin_status, has_access, purchase_status)

    poster = drama.get("poster_url")
    if poster:
        try:
            await query.message.delete()
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=poster,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        except Exception:
            pass

    await query.edit_message_text(
        caption,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def buy_drama_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ចាប់ផ្តើមសំណើទិញរឿង & សុំ Slip"""
    query = update.callback_query
    await query.answer()

    drama_id = int(query.data.replace("buy_drama_", ""))
    drama = db.get_drama_by_id(drama_id)

    if not drama:
        await query.answer("❌ រឿងនេះមិនមានទេ!", show_alert=True)
        return

    context.user_data["buying_drama_id"] = drama_id
    price_str = str(drama.get("price", "0")).strip()
    payment_info = db.get_setting("payment_info")

    text = (
        f"💳 **ការទិញរឿង ៖ {drama['title']}**\n"
        f"💰 **តម្លៃ ៖** {price_str}\n\n"
        f"🏦 **ព័ត៌មានផ្ទេរប្រាក់ ៖**\n"
        f"{payment_info}\n\n"
        f"📸 **ជំហានចុងក្រោយ ៖**\n"
        f"សូម **ផ្ញើរូបភាពវិក្កយបត្រ (Payment Slip/Screenshot)** នៃការផ្ទេរប្រាក់ ចូលមកកាន់ទីនេះផ្ទាល់!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ បោះបង់", callback_data=f"view_drama_{drama_id}")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def payment_slip_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ទទួលរូបភាពវិក្កយបត្រ Slip ពី User ហើយជូនដំណឹងទៅ Admin"""
    if not update.message or not update.message.photo:
        return

    buying_drama_id = context.user_data.get("buying_drama_id")
    if not buying_drama_id:
        return

    drama = db.get_drama_by_id(buying_drama_id)
    if not drama:
        return

    user = update.effective_user
    file_id = update.message.photo[-1].file_id

    # Record purchase in DB
    purchase_id = db.add_purchase_request(user.id, buying_drama_id, file_id)
    context.user_data.pop("buying_drama_id", None)

    # Notify User
    await update.message.reply_text(
        f"✅ **បានទទួលវិក្កយបត្រដោយជោគជ័យ!**\n\n"
        f"🎬 **រឿង ៖** {drama['title']}\n"
        f"💰 **តម្លៃ ៖** {drama.get('price')}\n\n"
        f"⏳ វិក្កយបត្ររបស់អ្នកត្រូវបានបញ្ជូនទៅកាន់ Admin ដើម្បីត្រួតពិនិត្យ។\n"
        f"នៅពេល Admin អនុម័តរួច Bot នឹងផ្ញើសារជូនដំណឹងភ្លាមៗ!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 មើលផ្ទាំងរឿង", callback_data=f"view_drama_{buying_drama_id}")],
            [InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

    # Notify ALL Admins with the Slip Photo
    admin_caption = (
        f"🔔 **មានសំណើទិញរឿងថ្មី! (ID: #{purchase_id})**\n\n"
        f"👤 **អ្នកទិញ:** {user.first_name} (@{user.username})\n"
        f"🆔 **Telegram ID:** `{user.id}`\n"
        f"🎬 **រឿង:** {drama['title']}\n"
        f"💰 **តម្លៃ:** {drama.get('price')}\n\n"
        f"សូមពិនិត្យវិក្កយបត្រខាងលើ រួចចុចអនុម័ត ឬបដិសេធ ៖"
    )
    admin_markup = kb.purchase_admin_approval_keyboard(purchase_id)

    for aid in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=aid,
                photo=file_id,
                caption=admin_caption,
                reply_markup=admin_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {aid} about purchase #{purchase_id}: {e}")

async def view_episode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    drama_id = int(parts[1])
    ep_num = int(parts[2])

    user_id = query.from_user.id
    admin_status = is_admin(user_id)

    # Security check: Has user paid?
    if not db.has_user_access(user_id, drama_id, admin_status):
        await query.answer("🔒 រឿងនេះជាប្រភេទរឿង VIP! សូមធ្វើការបង់ប្រាក់ជាមុនសិន។", show_alert=True)
        return

    drama = db.get_drama_by_id(drama_id)
    episodes = db.get_episodes(drama_id)
    total_episodes = len(episodes)
    episode = db.get_episode(drama_id, ep_num)

    if not episode:
        await query.answer("❌ ភាគនេះមិនទាន់ត្រូវបានបញ្ចូលនៅឡើយទេ!", show_alert=True)
        return

    title_text = f" ({episode['title']})" if episode.get('title') else ""
    caption = (
        f"🎬 **{drama['title'] if drama else 'RB Drama'}**\n"
        f"▶️ **ភាគទី {ep_num}{title_text}**\n\n"
    )

    video_url = episode.get("video_url", "").strip()
    file_id = episode.get("file_id", "").strip()

    if video_url:
        caption += f"🔗 **តំណភ្ជាប់ទស្សនា:** [ចុចទីនេះដើម្បីទស្សនា]({video_url})\n\n"
    caption += "រីករាយទស្សនាជាមួយ RB Drama! ✨"

    markup = kb.episode_detail_keyboard(drama_id, ep_num, video_url, total_episodes)

    if file_id:
        try:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=file_id,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        except Exception as e:
            logger.warning(f"Error sending video file {file_id}: {e}")

    await query.edit_message_text(
        caption,
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False
    )

async def prompt_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "🔍 **ស្វែងរករឿងក្នុង RB Drama**\n\n"
        "សូមវាយឈ្មោះរឿង ឬពាក្យគន្លឹះដែលអ្នកចង់ស្វែងរក ហើយផ្ញើមកកាន់ទីនេះផ្ទាល់!\n\n"
        "ឧទាហរណ៍៖ `ស្នេហា`, `The Glory`, `VIP`"
    )
    keyboard = kb.InlineKeyboardMarkup([
        [kb.InlineKeyboardButton("🔙 ត្រឡប់ទៅមឺនុយដើម", callback_data="back_home")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def search_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.message.text.startswith("/"):
        return

    query_str = update.message.text.strip()
    dramas = db.search_dramas(query_str, limit=8)

    if not dramas:
        await update.message.reply_text(
            f"🔍 មិនមានលទ្ធផលសម្រាប់ **\"{query_str}\"** នោះទេ។\n"
            f"សូមព្យាយាមវាយពាក្យគន្លឹះផ្សេងទៀត ឬមើលរឿងទាំងអស់តាមរយៈមឺនុយ។",
            reply_markup=kb.main_menu_keyboard(is_admin(update.effective_user.id)),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    text = f"🔍 **លទ្ធផលស្វែងរកសម្រាប់ \"{query_str}\" (រកឃើញ {len(dramas)} រឿង) ៖**"
    keyboard = []
    for drama in dramas:
        price = str(drama.get("price", "0")).strip()
        is_paid = db.is_drama_paid(drama)
        tag = f"💎 [{price}]" if is_paid else "🎁 [Free]"
        keyboard.append([kb.InlineKeyboardButton(f"{tag} {drama['title']} ({drama.get('episode_count', 0)} ភាគ)", callback_data=f"view_drama_{drama['id']}")])
    keyboard.append([kb.InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")])

    await update.message.reply_text(
        text,
        reply_markup=kb.InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def help_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payment_info = db.get_setting("payment_info")
    text = (
        "ℹ️ **ជំនួយ និងរបៀបទិញរឿងក្នុង RB Drama**\n\n"
        "🍿 **1. របៀបទស្សនារឿង Free ៖**\n"
        "• ចុចលើរឿងដែលមានសញ្ញា **🎁 [Free]** ដើម្បីមើលភ្លាមៗដោយឥតគិតថ្លៃ\n\n"
        "💎 **2. របៀបទិញរឿង VIP/លក់ ៖**\n"
        "• ចុចលើរឿងដែលមានសញ្ញា **💎 [តម្លៃ]**\n"
        "• ចុចប៊ូតុង **💳 បង់ប្រាក់ទិញរឿង**\n"
        "• ធ្វើការផ្ទេរប្រាក់តាមគណនីធនាគារខាងក្រោម រួចផ្ញើរូបភាពវិក្កយបត្រ (Slip) ចូលទីនេះផ្ទាល់ ៖\n\n"
        f"{payment_info}\n\n"
        "• Admin នឹងពិនិត្យ និងអនុម័តភ្លាមៗដើម្បីឱ្យអ្នកអាចចូលទស្សនាបាន!"
    )
    keyboard = kb.InlineKeyboardMarkup([
        [kb.InlineKeyboardButton("🔙 ត្រឡប់ទៅមឺនុយដើម", callback_data="back_home")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
