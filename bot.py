import os
import threading
import requests
import stripe

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ========= CONFIG =========
TOKEN = os.getenv("BOT_TOKEN")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

SUPPORT_URL = "https://t.me/StricklySupportbot"
BOT_URL = "https://t.me/StricklyVIPbot"
VIP_INVITE_LINK = "https://t.me/+P9aBNAzfo6szNmM8"
BANNER_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"

# ========= HELPERS =========
def send_telegram_message(chat_id: int, text: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15,
    )


def create_checkout_session(chat_id: int):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": 1500,  # £15.00
                        "product_data": {
                            "name": "Strickly VIP Access",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=BOT_URL,
            cancel_url=BOT_URL,
            metadata={"telegram_id": str(chat_id)},
        )
        return session.url
    except Exception as e:
        print("STRIPE ERROR:", str(e))
        return None


# ========= MENUS =========
def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Continue", callback_data="buy_now")],
        [InlineKeyboardButton("View previews", callback_data="previews")],
        [InlineKeyboardButton("Support", url=SUPPORT_URL)],
    ])


def product_menu(checkout_url: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Pay by Card", url=checkout_url)],
        [InlineKeyboardButton("Back", callback_data="back_home")],
    ])


def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Back", callback_data="back_home")]
    ])


def get_home_caption():
    return """Strickly VIP

Private network access.

19 members joined today.

• Instant access after payment
• Secure checkout
• Card accepted

Tap below to continue."""


def get_buy_caption():
    return """Strickly VIP

Private network access.

19 members joined today.

• £15.00 access
• Secure card checkout

Choose payment below."""


PREVIEW_TEXT = """Previews

Add screenshots, proof, or sample content here."""


# ========= TELEGRAM BOT =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(BANNER_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=get_home_caption(),
            reply_markup=home_menu(),
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_now":
        checkout_url = create_checkout_session(query.message.chat.id)

        if not checkout_url:
            await query.message.reply_text("Payment error. Try again in a moment.")
            return

        try:
            await query.message.delete()
        except Exception:
            pass

        with open(BANNER_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_buy_caption(),
                reply_markup=product_menu(checkout_url),
            )

    elif query.data == "previews":
        try:
            await query.edit_message_caption(
                caption=PREVIEW_TEXT,
                reply_markup=back_menu(),
            )
        except Exception:
            await query.message.reply_text(
                text=PREVIEW_TEXT,
                reply_markup=back_menu(),
            )

    elif query.data == "back_home":
        try:
            await query.message.delete()
        except Exception:
            pass

        with open(BANNER_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_home_caption(),
                reply_markup=home_menu(),
            )


def run_bot():
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.run_polling()


# ========= WEBHOOK =========
flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "Bot is running"


@flask_app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        return "Webhook error", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session.get("metadata", {}).get("telegram_id")

        if telegram_id:
            send_telegram_message(
                int(telegram_id),
                f"✅ Payment received!\n\n🔓 Your VIP access link:\n{VIP_INVITE_LINK}",
            )

    return "OK", 200


# ========= RUN BOTH =========
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    flask_app.run(host="0.0.0.0", port=8080)
