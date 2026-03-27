from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os
import json
from pathlib import Path
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8633029909
STATS_CHANNEL_ID = -5153258212

SUPPORT_URL = "https://t.me/StricklySupportbot"
PREVIEWS_URL = "https://t.me/+EM4JGufTMKE2OWRk"

HOME_IMAGE = "3B02192C-77A1-49E4-9A12-31F2759144D6.png"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"

STATS_FILE = "stats.json"

def load_stats() -> dict:
    if Path(STATS_FILE).exists():
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"starts": 0, "buy_clicks": 0, "preview_clicks": 0}

def save_stats(stats: dict):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def increment_stat(key: str):
    stats = load_stats()
    stats[key] = stats.get(key, 0) + 1
    save_stats(stats)

def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Buy Now", callback_data="buy_now")],
        [InlineKeyboardButton("👀 View Previews", url=PREVIEWS_URL)],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_URL)],
    ])

def product_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Unlock Full Access — £15", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
    ])

def get_home_caption():
    return (
        "💎 *Strickly VIP Network*\n\n"
        "Unlock access to all 10 exclusive VIP channels.\n\n"
        "✅ Instant access after payment\n"
        "✅ Secure checkout\n"
        "✅ Card accepted\n\n"
        "🔒 256-bit SSL encrypted"
    )

def get_buy_caption():
    return (
        "💎 *Strickly VIP — Full Access*\n\n"
        "Unlock all 10 VIP channels instantly.\n\n"
        "*What's included:*\n"
        "• 320K+ UK data\n"
        "• All new and upcoming channels\n"
        "• Exclusive members-only channel\n"
        "• Full Strickly VIP folder (10 channels)\n\n"
        "*Price: £15.00 (one-time payment)*\n\n"
        "⚡ Instant access after payment\n"
        "🔒 Secure checkout — Card accepted"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    increment_stat("starts")

    if not Path(HOME_IMAGE).exists():
        await update.message.reply_text(
            get_home_caption(),
            reply_markup=home_menu(),
            parse_mode="Markdown"
        )
        return

    with open(HOME_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=get_home_caption(),
            reply_markup=home_menu(),
            parse_mode="Markdown"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    s = load_stats()
    await update.message.reply_text(
        f"📊 *Bot Stats*\n\n"
        f"👥 Total starts: {s.get('starts', 0)}\n"
        f"💎 Buy Now clicks: {s.get('buy_clicks', 0)}\n"
        f"👀 Preview clicks: {s.get('preview_clicks', 0)}",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_now":
        increment_stat("buy_clicks")
        stats = load_stats()

        # Get user info
        user = query.from_user
        user_name = user.first_name or "Unknown"
        username = f"@{user.username}" if user.username else "no username"
        user_id = user.id
        time_now = datetime.now().strftime("%d %B %Y %H:%M")

        # Send to stats channel
        try:
            await context.bot.send_message(
                chat_id=STATS_CHANNEL_ID,
                text=f"💎 *Buy Now Clicked!*\n\n"
                     f"👤 {user_name} ({username})\n"
                     f"🆔 {user_id}\n"
                     f"⏰ {time_now}\n\n"
                     f"💎 Total buy clicks: {stats.get('buy_clicks', 0)}",
                parse_mode="Markdown"
            )
        except Exception as e:
            pass

        try:
            await query.message.delete()
        except Exception:
            pass

        if not Path(BUY_IMAGE).exists():
            await query.message.chat.send_message(
                get_buy_caption(),
                reply_markup=product_menu(),
                parse_mode="Markdown"
            )
            return

        with open(BUY_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_buy_caption(),
                reply_markup=product_menu(),
                parse_mode="Markdown"
            )

    elif query.data == "back_home":
        try:
            await query.message.delete()
        except Exception:
            pass

        if not Path(HOME_IMAGE).exists():
            await query.message.chat.send_message(
                get_home_caption(),
                reply_markup=home_menu(),
                parse_mode="Markdown"
            )
            return

        with open(HOME_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_home_caption(),
                reply_markup=home_menu(),
                parse_mode="Markdown"
            )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
