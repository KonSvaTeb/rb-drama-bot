import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.constants import ParseMode

import database as db
import keyboards as kb
from config import is_admin, ADMIN_IDS

logger = logging.getLogger(__name__)

# Conversation States for Adding Drama
(
    DRAMA_TITLE,
    DRAMA_GENRE,
    DRAMA_PRICE,
    DRAMA_DESC,
    DRAMA_POSTER,
    DRAMA_STATUS
) = range(6)

# Conversation States for Adding Episode
(
    EP_DRAMA_ID,
    EP_NUMBER,
    EP_SOURCE
) = range(6, 9)

# Conversation State for Broadcast
BROADCAST_MESSAGE = 9

# Conversation State for Payment Info Setting
SETTING_PAYMENT = 10

# --- Admin Panel Entry ---
async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        text = "⛔️ អ្នកមិនមានសិទ្ធិចូលកាន់ផ្ទាំងគ្រប់គ្រង Admin នេះទេ។"
        if update.message:
            await update.message.reply_text(text)
        elif update.callback_query:
            await update.callback_query.answer(text, show_alert=True)
        return

    text = (
        "👑 **ផ្ទាំងគ្រប់គ្រង Admin (RB Drama Panel)**\n\n"
        "សូមជ្រើសរើសមុខងារគ្រប់គ្រងខាងក្រោម ៖\n"
        "• បង្ហោះរឿងថ្មី & កំណត់តម្លៃលក់ (Free ឬ VIP)\n"
        "• បន្ថែមភាគរឿង និងគ្រប់គ្រងភាគ\n"
        "• កំណត់ព័ត៌មានកុងធនាគារ (ABA / Wing)\n"
        "• ផ្ញើសារប្រកាសដំណឹង (Broadcast) ទៅកាន់សមាជិកទាំងអស់\n"
        "• មើលស្ថិតិចំនួនអ្នកប្រើប្រាស់ និងចំនួនទិញរឿង"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text,
            reply_markup=kb.admin_panel_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    elif update.message:
        await update.message.reply_text(
            text,
            reply_markup=kb.admin_panel_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )

async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔️ គ្មានសិទ្ធិ!", show_alert=True)
        return

    stats = db.get_stats()
    text = (
        "📊 **ស្ថិតិទូទៅនៃ RB Drama Bot**\n\n"
        f"👥 **ចំនួនអ្នកប្រើប្រាស់សរុប:** {stats['users']} នាក់\n"
        f"🎬 **ចំនួនរឿងសរុប:** {stats['dramas']} រឿង\n"
        f"🎞 **ចំនួនភាគសរុប:** {stats['episodes']} ភាគ\n"
        f"💰 **ចំនួនការទិញរឿងដែលបានអនុម័ត:** {stats['purchases']} ដង\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ត្រឡប់ទៅផ្ទាំង Admin", callback_data="admin_panel")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

# --- Add Drama Conversation ---
async def start_add_drama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    context.user_data["new_drama"] = {}
    await query.edit_message_text(
        "🎬 **ជំហានទី 1/6 ៖ បញ្ចូលចំណងជើងរឿង**\n\n"
        "សូមវាយបញ្ចូល **ឈ្មោះរឿង** (ឧ. ស្នេហ៍ឆ្លងវេហា, The Glory) ៖",
        reply_markup=kb.cancel_keyboard()
    )
    return DRAMA_TITLE

async def set_drama_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text.strip()
    context.user_data["new_drama"]["title"] = title

    await update.message.reply_text(
        f"✅ ឈ្មោះរឿង៖ **{title}**\n\n"
        "🎭 **ជំហានទី 2/6 ៖ ប្រភេទរឿង (Genre)**\n"
        "សូមវាយប្រភេទរឿង (ឧ. មនោសញ្ចេតនា, កំប្លែង, សកម្មភាព) ឬវាយ /skip ៖",
        parse_mode=ParseMode.MARKDOWN
    )
    return DRAMA_GENRE

async def set_drama_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genre = update.message.text.strip()
    if genre == "/skip":
        genre = "ទូទៅ"
    context.user_data["new_drama"]["genre"] = genre

    await update.message.reply_text(
        f"✅ ប្រភេទរឿង៖ **{genre}**\n\n"
        "💰 **ជំហានទី 3/6 ៖ តម្លៃរឿង (Price)**\n"
        "សូមវាយតម្លៃរឿងសម្រាប់លក់ (ឧ. `$1.00`, `4000៛`, `5000៛`)\n"
        "ឬវាយ `0` ឬ `/skip` ប្រសិនបើរឿងនេះដាក់ឱ្យ **មើលហ្វ្រី (Free)** ៖",
        parse_mode=ParseMode.MARKDOWN
    )
    return DRAMA_PRICE

async def set_drama_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text.strip()
    if price_text in ["/skip", "0", "0$", "$0", "free", "Free", "ហ្វ្រី"]:
        price_text = "0"
    context.user_data["new_drama"]["price"] = price_text

    display_price = "🎁 មើលហ្វ្រី (Free)" if price_text == "0" else f"💎 {price_text}"
    await update.message.reply_text(
        f"✅ តម្លៃរឿង៖ **{display_price}**\n\n"
        "📝 **ជំហានទី 4/6 ៖ សេចក្តីសង្ខេបរឿង (Description)**\n"
        "សូមវាយសេចក្តីសង្ខេបដំណើររឿង ឬវាយ /skip ៖",
        parse_mode=ParseMode.MARKDOWN
    )
    return DRAMA_DESC

async def set_drama_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = update.message.text.strip()
    if desc == "/skip":
        desc = "គ្មានការពិពណ៌នា"
    context.user_data["new_drama"]["desc"] = desc

    await update.message.reply_text(
        "🖼 **ជំហានទី 5/6 ៖ រូបភាព Poster**\n\n"
        "📸 សូមជ្រើសរើស និង **ផ្ញើរូបភាព (Photo) ពីទូរស័ព្ទ ឬកុំព្យូទ័ររបស់អ្នក ចូលមកទីនេះផ្ទាល់**!\n\n"
        "👉 ឬវាយ **/skip** ប្រសិនបើមិនទាន់ចង់ដាក់រូបភាព ៖",
        parse_mode=ParseMode.MARKDOWN
    )
    return DRAMA_POSTER

async def set_drama_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poster = ""
    if update.message.photo:
        poster = update.message.photo[-1].file_id
    elif update.message.text:
        text = update.message.text.strip()
        if text == "/skip":
            poster = ""
        else:
            await update.message.reply_text(
                "⚠️ សូមជ្រើសរើស និង **ផ្ញើជារូបភាព (Photo)** ពីទូរស័ព្ទរបស់អ្នកផ្ទាល់\n"
                "ឬវាយ **/skip** ប្រសិនបើមិនចង់ដាក់រូបភាព ៖",
                parse_mode=ParseMode.MARKDOWN
            )
            return DRAMA_POSTER

    context.user_data["new_drama"]["poster"] = poster

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("កំពុងចាក់ផ្សាយ (Ongoing)", callback_data="status_កំពុងចាក់ផ្សាយ"),
            InlineKeyboardButton("ចប់ (Completed)", callback_data="status_ចប់")
        ]
    ])
    await update.message.reply_text(
        "📌 **ជំហានទី 6/6 ៖ ស្ថានភាពរឿង**\n\n"
        "សូមជ្រើសរើសស្ថានភាពនៃរឿងនេះ ៖",
        reply_markup=keyboard
    )
    return DRAMA_STATUS

async def set_drama_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    status = query.data.replace("status_", "")
    drama_data = context.user_data.get("new_drama", {})

    drama_id = db.add_drama(
        title=drama_data.get("title", "គ្មានចំណងជើង"),
        genre=drama_data.get("genre", "ទូទៅ"),
        description=drama_data.get("desc", ""),
        poster_url=drama_data.get("poster", ""),
        status=status,
        price=drama_data.get("price", "0")
    )

    price_str = drama_data.get("price", "0")
    display_price = "🎁 មើលហ្វ្រី (Free)" if price_str == "0" else f"💎 {price_str} (VIP/លក់)"

    confirm_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ បន្ថែមភាគទី 1 ឥឡូវនេះ", callback_data=f"admin_add_ep_{drama_id}")],
        [InlineKeyboardButton("👑 ត្រឡប់ទៅផ្ទាំង Admin", callback_data="admin_panel")]
    ])

    await query.edit_message_text(
        f"🎉 **បានបង្កើតរឿងជោគជ័យ!**\n\n"
        f"🎬 **រឿង:** {drama_data.get('title')}\n"
        f"🎭 **ប្រភេទ:** {drama_data.get('genre')}\n"
        f"💰 **តម្លៃ:** {display_price}\n"
        f"📌 **ស្ថានភាព:** {status}\n\n"
        f"តើអ្នកចង់បន្ថែមភាគទី 1 សម្រាប់រឿងនេះតែម្តងទេ?",
        reply_markup=confirm_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

# --- Add Episode Conversation ---
async def start_add_episode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    drama_id = None
    if "admin_add_ep_" in query.data:
        try:
            drama_id = int(query.data.replace("admin_add_ep_", ""))
        except ValueError:
            pass

    if drama_id:
        context.user_data["ep_drama_id"] = drama_id
        drama = db.get_drama_by_id(drama_id)
        existing_eps = db.get_episodes(drama_id)
        next_ep = len(existing_eps) + 1

        await query.edit_message_text(
            f"🎬 **បន្ថែមភាគសម្រាប់រឿង៖** {drama['title'] if drama else ''}\n"
            f"បច្ចុប្បន្នមាន៖ {len(existing_eps)} ភាគ\n\n"
            f"🔢 សូមវាយ **លេខភាគ** ដែលត្រូវបញ្ចូល (ឧ. `{next_ep}`) ៖",
            reply_markup=kb.cancel_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return EP_NUMBER

    dramas = db.get_dramas(limit=20)
    if not dramas:
        await query.edit_message_text(
            "⚠️ មិនទាន់មានរឿងនៅក្នុងប្រព័ន្ធទេ។ សូមបង្កើតរឿងជាមុនសិន!",
            reply_markup=kb.admin_panel_keyboard()
        )
        return ConversationHandler.END

    keyboard = []
    for d in dramas:
        keyboard.append([InlineKeyboardButton(f"🎬 {d['title']}", callback_data=f"sel_drama_{d['id']}")])
    keyboard.append([InlineKeyboardButton("❌ បោះបង់", callback_data="admin_panel")])

    await query.edit_message_text(
        "🎬 **សូមជ្រើសរើសរឿងដែលអ្នកចង់បន្ថែមភាគ ៖**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EP_DRAMA_ID

async def select_drama_for_ep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    drama_id = int(query.data.replace("sel_drama_", ""))
    context.user_data["ep_drama_id"] = drama_id
    drama = db.get_drama_by_id(drama_id)
    existing_eps = db.get_episodes(drama_id)
    next_ep = len(existing_eps) + 1

    await query.edit_message_text(
        f"🎬 **រឿង៖** {drama['title'] if drama else ''}\n"
        f"បច្ចុប្បន្នមាន៖ {len(existing_eps)} ភាគ\n\n"
        f"🔢 សូមវាយ **លេខភាគ** ដែលត្រូវបញ្ចូល (ឧ. `{next_ep}`) ៖",
        reply_markup=kb.cancel_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    return EP_NUMBER

async def set_ep_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("⚠️ សូមវាយជាលេខ (ឧ. 1, 2, 3...) ៖")
        return EP_NUMBER

    ep_num = int(text)
    context.user_data["ep_number"] = ep_num

    await update.message.reply_text(
        f"✅ ភាគទី **{ep_num}**\n\n"
        "🔗 **សូមផ្ញើតំណភ្ជាប់ (Link) ឬផ្ញើវីដេអូ Telegram ចូលទីនេះ ៖**\n\n"
        "• អ្នកអាចផ្ញើជា Link (Google Drive, YouTube, Stream Link...)\n"
        "• ឬអាច Upload វីដេអូ Telegram ចូលទីនេះដោយផ្ទាល់",
        parse_mode=ParseMode.MARKDOWN
    )
    return EP_SOURCE

async def set_ep_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drama_id = context.user_data.get("ep_drama_id")
    ep_num = context.user_data.get("ep_number", 1)

    video_url = ""
    file_id = ""

    if update.message.video:
        file_id = update.message.video.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    elif update.message.text:
        video_url = update.message.text.strip()

    db.add_episode(
        drama_id=drama_id,
        episode_number=ep_num,
        title=f"ភាគ {ep_num}",
        video_url=video_url,
        file_id=file_id
    )

    drama = db.get_drama_by_id(drama_id)
    next_ep = ep_num + 1

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ បន្តបន្ថែមភាគ {next_ep}", callback_data=f"admin_add_ep_{drama_id}")],
        [InlineKeyboardButton("🎬 មើលផ្ទាំងរឿងនេះ", callback_data=f"view_drama_{drama_id}")],
        [InlineKeyboardButton("👑 ត្រឡប់ទៅផ្ទាំង Admin", callback_data="admin_panel")]
    ])

    await update.message.reply_text(
        f"🎉 **បានរក្សាទុកភាគទី {ep_num} ដោយជោគជ័យ!**\n\n"
        f"🎬 **រឿង:** {drama['title'] if drama else ''}\n"
        f"🎞 **ភាគ:** {ep_num}",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

# --- Purchase Approvals / Rejections ---
async def approve_purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin ចុច Approve លើ Slip ទិញរឿង"""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔️ គ្មានសិទ្ធិ!", show_alert=True)
        return

    purchase_id = int(query.data.replace("admin_appr_pur_", ""))
    purchase = db.get_purchase_by_id(purchase_id)

    if not purchase:
        await query.edit_message_caption(caption="❌ មិនមានទិន្នន័យសំណើនេះទេ!")
        return

    db.update_purchase_status(purchase_id, "approved")

    # Update admin caption
    admin_done_caption = (
        f"✅ **បានអនុម័តជោគជ័យ! (ID: #{purchase_id})**\n\n"
        f"👤 អ្នកទិញ៖ {purchase.get('first_name')} (@{purchase.get('username')})\n"
        f"🎬 រឿង៖ {purchase.get('drama_title')}\n"
        f"💰 តម្លៃ៖ {purchase.get('drama_price')}\n"
        f"✔️ អនុម័តដោយ៖ Admin @{query.from_user.username or query.from_user.first_name}"
    )
    try:
        await query.edit_message_caption(caption=admin_done_caption, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

    # Notify Buyer User!
    buyer_user_id = purchase["user_id"]
    drama_id = purchase["drama_id"]
    try:
        await context.bot.send_message(
            chat_id=buyer_user_id,
            text=(
                f"🎉 **សូមអបអរសាទរ! សំណើទិញរឿងរបស់អ្នកត្រូវបានអនុម័តហើយ!**\n\n"
                f"🎬 **រឿង ៖** {purchase.get('drama_title')}\n"
                f"💰 **តម្លៃ ៖** {purchase.get('drama_price')}\n\n"
                f"ឥឡូវនេះ លោកអ្នកអាចចូលទស្សនាភាគទាំងអស់បានហើយ! សូមចុចប៊ូតុងខាងក្រោម ៖"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ ចូលមើលរឿងឥឡូវនេះ", callback_data=f"view_drama_{drama_id}")],
                [InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.warning(f"Could not notify buyer {buyer_user_id}: {e}")

async def reject_purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin ចុច Reject លើ Slip"""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔️ គ្មានសិទ្ធិ!", show_alert=True)
        return

    purchase_id = int(query.data.replace("admin_rej_pur_", ""))
    purchase = db.get_purchase_by_id(purchase_id)

    if not purchase:
        await query.edit_message_caption(caption="❌ មិនមានទិន្នន័យសំណើនេះទេ!")
        return

    db.update_purchase_status(purchase_id, "rejected")

    admin_reject_caption = (
        f"❌ **បានបដិសេធសំណើទិញ! (ID: #{purchase_id})**\n\n"
        f"👤 អ្នកទិញ៖ {purchase.get('first_name')} (@{purchase.get('username')})\n"
        f"🎬 រឿង៖ {purchase.get('drama_title')}\n"
        f"❌ បដិសេធដោយ៖ Admin"
    )
    try:
        await query.edit_message_caption(caption=admin_reject_caption, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        pass

    # Notify Buyer User
    buyer_user_id = purchase["user_id"]
    drama_id = purchase["drama_id"]
    try:
        await context.bot.send_message(
            chat_id=buyer_user_id,
            text=(
                f"❌ **សំណើទិញរឿង \"{purchase.get('drama_title')}\" មិនត្រូវបានអនុម័តទេ។**\n\n"
                f"សូមពិនិត្យមើលរូបភាពវិក្កយបត្រឡើងវិញ ឬទាក់ទងមកកាន់ Admin ប្រសិនបើមានចម្ងល់។"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 មើលផ្ទាំងរឿងឡើងវិញ", callback_data=f"view_drama_{drama_id}")],
                [InlineKeyboardButton("🔙 មឺនុយដើម", callback_data="back_home")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.warning(f"Could not notify buyer {buyer_user_id}: {e}")

# --- Set Payment Info Conversation ---
async def start_set_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    current_info = db.get_setting("payment_info")
    text = (
        "🏦 **កំណត់ព័ត៌មានបង់ប្រាក់ (Payment Info)**\n\n"
        f"📌 **ព័ត៌មានបច្ចុប្បន្ន ៖**\n{current_info}\n\n"
        "✍️ សូមវាយបញ្ចូលព័ត៌មានគណនីធនាគារថ្មី (ABA, Wing, ACLEDA...) ដែលអ្នកចង់ឱ្យ User ផ្ទេរប្រាក់មក ៖"
    )
    await query.edit_message_text(text, reply_markup=kb.cancel_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return SETTING_PAYMENT

async def save_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_info = update.message.text.strip()
    db.set_setting("payment_info", new_info)

    await update.message.reply_text(
        f"✅ **បានកែប្រែព័ត៌មានបង់ប្រាក់ដោយជោគជ័យ!**\n\n"
        f"📌 **ព័ត៌មានថ្មី ៖**\n{new_info}",
        reply_markup=kb.admin_panel_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

# --- Delete Drama ---
async def delete_drama_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("⛔️ គ្មានសិទ្ធិ!", show_alert=True)
        return

    drama_id = int(query.data.replace("admin_del_drama_", ""))
    drama = db.get_drama_by_id(drama_id)

    if not drama:
        await query.edit_message_text("❌ រឿងនេះមិនមានទេ!", reply_markup=kb.admin_panel_keyboard())
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚠️ បាទ/ចាស លុបចេញ", callback_data=f"admin_confirm_del_{drama_id}")],
        [InlineKeyboardButton("❌ ទេ ទុកវិញ", callback_data=f"view_drama_{drama_id}")]
    ])

    await query.edit_message_text(
        f"⚠️ **តើអ្នកប្រាកដជាចង់លុបរឿង \"{drama['title']}\" និងភាគទាំងអស់របស់វាទេ?**\n"
        "ទិន្នន័យដែលបានលុប មិនអាចយកមកវិញបានឡើយ!",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

async def confirm_delete_drama_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    drama_id = int(query.data.replace("admin_confirm_del_", ""))
    success = db.delete_drama(drama_id)

    if success:
        await query.edit_message_text(
            "✅ **បានលុបរឿងនេះចេញពីប្រព័ន្ធដោយជោគជ័យ!**",
            reply_markup=kb.admin_panel_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await query.edit_message_text(
            "❌ បរាជ័យក្នុងការលុបរឿង។",
            reply_markup=kb.admin_panel_keyboard()
        )

# --- Broadcast ---
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return ConversationHandler.END

    total_users = db.get_user_count()
    await query.edit_message_text(
        f"📢 **ផ្ញើសារប្រកាសដំណឹង (Broadcast)**\n\n"
        f"👥 ចំនួនសមាជិកដែលនឹងទទួលបាន៖ **{total_users} នាក់**\n\n"
        f"សូមផ្ញើសារជាអក្សរ រូបភាព ឬ Forward សារដែលអ្នកចង់ Broadcast មកកាន់ទីនេះ ៖",
        reply_markup=kb.cancel_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    return BROADCAST_MESSAGE

async def execute_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids = db.get_all_user_ids()
    total = len(user_ids)

    status_msg = await update.message.reply_text(f"⏳ កំពុងផ្ញើសារទៅកាន់សមាជិកទាំង {total} នាក់...")

    success = 0
    failed = 0

    for uid in user_ids:
        try:
            await update.message.copy(chat_id=uid)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.info(f"Broadcast failed to user {uid}: {e}")

    await status_msg.edit_text(
        f"✅ **ការផ្ញើសារ Broadcast បានបញ្ចប់!**\n\n"
        f"👥 សរុប៖ {total} នាក់\n"
        f"✔️ ជោគជ័យ៖ {success} នាក់\n"
        f"❌ បរាជ័យ (Block/Inactive)៖ {failed} នាក់",
        reply_markup=kb.admin_panel_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

async def admin_manage_dramas_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dramas = db.get_dramas(limit=20)
    if not dramas:
        await query.edit_message_text(
            "⚠️ មិនទាន់មានរឿងនៅក្នុងប្រព័ន្ធទេ។",
            reply_markup=kb.admin_panel_keyboard()
        )
        return

    keyboard = []
    for d in dramas:
        price = str(d.get("price", "0")).strip()
        tag = f"💎 [{price}]" if db.is_drama_paid(d) else "🎁 [Free]"
        keyboard.append([InlineKeyboardButton(f"{tag} {d['title']} ({d.get('episode_count', 0)} ភាគ)", callback_data=f"view_drama_{d['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 ត្រឡប់ទៅផ្ទាំង Admin", callback_data="admin_panel")])

    await query.edit_message_text(
        "📋 **សូមជ្រើសរើសរឿងដើម្បីបន្ថែមភាគ ឬលុបចេញ ៖**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "❌ បានបោះបង់សកម្មភាព។",
            reply_markup=kb.admin_panel_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ បានបោះបង់សកម្មភាព។",
            reply_markup=kb.admin_panel_keyboard()
        )
    return ConversationHandler.END
