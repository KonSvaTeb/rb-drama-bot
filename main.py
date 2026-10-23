import logging
import sys
import os
import glob
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure current directory and all site-packages on Linux/Render are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

for p in glob.glob("/root/.local/lib/python*/site-packages") + \
         glob.glob("/home/*/.local/lib/python*/site-packages") + \
         glob.glob("/opt/render/**/site-packages", recursive=True):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

import database as db
from config import BOT_TOKEN
from handlers import user_handlers, admin_handlers

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """ឆ្លើយតប HTTP 200 សម្រាប់ Cloud Platform (Render/Koyeb) Health Check"""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"RB Drama Bot is running 24/7!")

    def log_message(self, format, *args):
        return

def start_health_check_server():
    """ដំណើរការ HTTP Server ក្នុង Thread មួយទៀតសម្រាប់ Cloud Port Binding"""
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"🌐 Health check HTTP server started on port {port}")
    except Exception as e:
        logger.warning(f"Could not start health check server on port {port}: {e}")

def create_application():
    """បង្កើត និងកំណត់រចនាសម្ព័ន្ធ Telegram Bot Application"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ សូមកំណត់ BOT_TOKEN ក្នុងឯកសារ .env ជាមុនសិន!")
        return None

    # Initialize SQLite Database
    db.init_db()

    # Build Application
    app = Application.builder().token(BOT_TOKEN).build()

    # 1. Conversation Handler សម្រាប់ Add Drama (រួមទាំងកំណត់តម្លៃ Price)
    add_drama_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_handlers.start_add_drama, pattern="^admin_add_drama$")],
        states={
            admin_handlers.DRAMA_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.set_drama_title)],
            admin_handlers.DRAMA_GENRE: [MessageHandler(filters.TEXT, admin_handlers.set_drama_genre)],
            admin_handlers.DRAMA_PRICE: [MessageHandler(filters.TEXT, admin_handlers.set_drama_price)],
            admin_handlers.DRAMA_DESC: [MessageHandler(filters.TEXT, admin_handlers.set_drama_desc)],
            admin_handlers.DRAMA_POSTER: [
                MessageHandler(filters.PHOTO | filters.TEXT, admin_handlers.set_drama_poster)
            ],
            admin_handlers.DRAMA_STATUS: [CallbackQueryHandler(admin_handlers.set_drama_status, pattern="^status_")]
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.cancel_conversation, pattern="^admin_panel$"),
            CommandHandler("cancel", admin_handlers.cancel_conversation)
        ],
        per_message=False
    )
    app.add_handler(add_drama_conv)

    # 2. Conversation Handler សម្រាប់ Add Episode
    add_ep_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_handlers.start_add_episode, pattern="^admin_add_ep")
        ],
        states={
            admin_handlers.EP_DRAMA_ID: [CallbackQueryHandler(admin_handlers.select_drama_for_ep, pattern="^sel_drama_")],
            admin_handlers.EP_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.set_ep_number)],
            admin_handlers.EP_SOURCE: [
                MessageHandler(filters.TEXT | filters.VIDEO | filters.Document.ALL, admin_handlers.set_ep_source)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.cancel_conversation, pattern="^admin_panel$"),
            CommandHandler("cancel", admin_handlers.cancel_conversation)
        ],
        per_message=False
    )
    app.add_handler(add_ep_conv)

    # 3. Conversation Handler សម្រាប់ Broadcast Message
    broadcast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_handlers.start_broadcast, pattern="^admin_broadcast$")],
        states={
            admin_handlers.BROADCAST_MESSAGE: [
                MessageHandler(filters.ALL & ~filters.COMMAND, admin_handlers.execute_broadcast)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.cancel_conversation, pattern="^admin_panel$"),
            CommandHandler("cancel", admin_handlers.cancel_conversation)
        ],
        per_message=False
    )
    app.add_handler(broadcast_conv)

    # 4. Conversation Handler សម្រាប់កំណត់ព័ត៌មានបង់ប្រាក់ Payment Info
    payment_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_handlers.start_set_payment, pattern="^admin_set_payment$")],
        states={
            admin_handlers.SETTING_PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handlers.save_payment_info)
            ]
        },
        fallbacks=[
            CallbackQueryHandler(admin_handlers.cancel_conversation, pattern="^admin_panel$"),
            CommandHandler("cancel", admin_handlers.cancel_conversation)
        ],
        per_message=False
    )
    app.add_handler(payment_conv)

    # 5. Commands
    app.add_handler(CommandHandler("start", user_handlers.start_command))
    app.add_handler(CommandHandler("admin", admin_handlers.admin_panel_handler))
    app.add_handler(CommandHandler("help", user_handlers.help_menu_callback))

    # 6. Admin Callbacks
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_panel_handler, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_stats_callback, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_manage_dramas_callback, pattern="^admin_manage_dramas$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.delete_drama_callback, pattern="^admin_del_drama_"))
    app.add_handler(CallbackQueryHandler(admin_handlers.confirm_delete_drama_callback, pattern="^admin_confirm_del_"))
    app.add_handler(CallbackQueryHandler(admin_handlers.approve_purchase_callback, pattern="^admin_appr_pur_"))
    app.add_handler(CallbackQueryHandler(admin_handlers.reject_purchase_callback, pattern="^admin_rej_pur_"))

    # 7. User Callbacks
    app.add_handler(CallbackQueryHandler(user_handlers.back_home_callback, pattern="^back_home$"))
    app.add_handler(CallbackQueryHandler(user_handlers.dramas_page_callback, pattern="^dramas_page_"))
    app.add_handler(CallbackQueryHandler(user_handlers.paid_dramas_callback, pattern="^paid_dramas_"))
    app.add_handler(CallbackQueryHandler(user_handlers.free_dramas_callback, pattern="^free_dramas_"))
    app.add_handler(CallbackQueryHandler(user_handlers.recent_dramas_callback, pattern="^recent_dramas$"))
    app.add_handler(CallbackQueryHandler(user_handlers.view_drama_callback, pattern="^view_drama_"))
    app.add_handler(CallbackQueryHandler(user_handlers.buy_drama_callback, pattern="^buy_drama_"))
    app.add_handler(CallbackQueryHandler(user_handlers.view_episode_callback, pattern="^ep_"))
    app.add_handler(CallbackQueryHandler(user_handlers.prompt_search_callback, pattern="^search_drama$"))
    app.add_handler(CallbackQueryHandler(user_handlers.help_menu_callback, pattern="^help_menu$"))
    app.add_handler(CallbackQueryHandler(user_handlers.check_sub_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(user_handlers.noop_callback, pattern="^noop$"))

    # 8. Photo Message Handler (សម្រាប់ទទួល Payment Slip ពេលទិញរឿង)
    app.add_handler(MessageHandler(filters.PHOTO, user_handlers.payment_slip_message_handler))

    # 9. Text Messages (Search Drama by Name)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_handlers.search_message_handler))

    return app

def main():
    print("🚀 កំពុងដំណើរការ RB Drama Telegram Bot...")
    start_health_check_server()

    app = create_application()
    if app:
        print("✅ Bot បានចាប់ផ្តើមដំណើរការ Polling ដោយជោគជ័យ! (ចុច Ctrl+C ដើម្បីបញ្ឈប់)")
        app.run_polling()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
