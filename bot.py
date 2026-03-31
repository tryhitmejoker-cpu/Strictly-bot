from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from aiohttp import web
import asyncio
import os
import json
import httpx
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8633029909
OXAPAY_API_KEY = os.getenv("OXAPAY_API_KEY")
FOLDER_LINK = "https://t.me/addlist/fi8vlP6OlSs0MGFk"
SUPPORT_URL = "https://t.me/StricklySupportbot"
PREVIEWS_URL = "https://t.me/+EM4JGufTMKE2OWRk"
HOME_IMAGE = "3B02192C-77A1-49E4-9A12-31F2759144D6.png"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"
STATS_FILE = "stats.json"
PENDING_PAYMENTS_FILE = "pending_payments.json"
OXAPAY_API_URL = "https://api.oxapay.com/merchants/request"


# ---------------- STATS ----------------
def load_stats():
    if Path(STATS_FILE).exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"starts": 0, "buy_clicks": 0, "crypto_clicks": 0}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def increment_stat(key):
    stats = load_stats()
    stats[key] = stats.get(key, 0) + 1
    save_stats(stats)


# ---------------- PAYMENTS ----------------
def load_pending():
    if Path(PENDING_PAYMENTS_FILE).exists():
        with open(PENDING_PAYMENTS_FILE) as f:
            return json.load(f)
    return {}


def save_pending(data):
    with open(PENDING_PAYMENTS_FILE, "w") as f:
        json.dump(data, f)


def add_pending(track_id, user_id):
    data = load_pending()
    data[str(track_id)] = str(user_id)
    save_pending(data)


def get_and_remove_pending(track_id):
    data = load_pending()
    user_id = data.pop(str(track_id), None)
    save_pending(data)
    return user_id


# ---------------- MENUS ----------------
def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Buy Now", callback_data="buy_now")],
        [InlineKeyboardButton("👀 View Previews", url=PREVIEWS_URL)],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_URL)],
    ])


def product_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay with Card — £15", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("₿ Pay with Crypto", callback_data="pay_crypto")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
    ])


# ---------------- TEXT ----------------
def get_home_caption():
    return (
        "💎 <b>Strickly VIP Network</b>\n\n"
        "Unlock access to all 10 exclusive VIP channels.\n\n"
        "✅ Instant access after payment\n"
        "✅ Secure checkout\n"
        "✅ Card & Crypto accepted\n\n"
        "<tg-emoji emoji-id=\"6276239815633540328\">✔️</tg-emoji> 256-bit SSL encrypted"
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
        "🔒 Secure checkout — Card & Crypto accepted"
    )


# ---------------- CRYPTO ----------------
async def create_crypto_payment(user_id: int) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            OXAPAY_API_URL,
            json={
                "merchant": OXAPAY_API_KEY,
                "amount": 19,
                "currency": "USD",
                "lifeTime": 60,
                "orderId": str(user_id),
                "description": "Strickly VIP Full Access",
            }
        )
        return response.json()


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    increment_stat("starts")

    with open(HOME_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=get_home_caption(),
            reply_markup=home_menu(),
            parse_mode="HTML"
        )


# ---------------- BUTTONS ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "buy_now":
        increment_stat("buy_clicks")

        try:
            await query.message.delete()
        except:
            pass

        with open(BUY_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_buy_caption(),
                reply_markup=product_menu(),
                parse_mode="Markdown"
            )

    elif query.data == "pay_crypto":
        increment_stat("crypto_clicks")

        await query.message.edit_text("⏳ Creating your payment...")

        result = await create_crypto_payment(user_id)

        if result.get("result") == 1:
            track_id = result.get("trackId")
            pay_link = result.get("paymentUrl") or result.get("url")

            add_pending(track_id, user_id)

            await query.message.edit_text(
                f"₿ *Crypto Payment*\n\n"
                f"💰 Amount: $19\n\n"
                f"⏰ Expires in 60 minutes.\n\n"
                f"Tap below to pay:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Complete Payment", url=pay_link)],
                    [InlineKeyboardButton("◀️ Back", callback_data="buy_now")]
                ])
            )

    elif query.data == "back_home":
        try:
            await query.message.delete()
        except:
            pass

        with open(HOME_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_home_caption(),
                reply_markup=home_menu(),
                parse_mode="HTML"
            )


# ---------------- WEBHOOK ----------------
bot_app = None

async def oxapay_webhook(request):
    data = await request.json()
    track_id = data.get("trackId")

    user_id = get_and_remove_pending(track_id)

    if user_id:
        await bot_app.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ *Payment Confirmed!*\n\n🔗 {FOLDER_LINK}",
            parse_mode="Markdown"
        )

    return web.Response(text="OK")


async def run_webhook_server():
    app = web.Application()
    app.router.add_post("/webhook", oxapay_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()


# ---------------- MAIN ----------------
def main():
    global bot_app

    bot_app = ApplicationBuilder().token(TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_handler))

    async def run():
        await run_webhook_server()
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        await asyncio.Event().wait()

    asyncio.run(run())


if __name__ == "__main__":
    main()
