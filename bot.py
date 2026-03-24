from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os
import random

TOKEN = os.getenv("BOT_TOKEN")

STRIPE_URL = "https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D"
CRYPTO_URL = "https://your-crypto-link.com"
SUPPORT_URL = "https://t.me/yourusername"
BANNER_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"


def get_fake_activity():
    messages = [
        "🔥 Someone just joined",
        "⚡ New member unlocked access",
        "👑 VIP access purchased",
        "🚀 Another user joined",
    ]
    return random.choice(messages)


def home_menu():
    keyboard = [
        [InlineKeyboardButton("🔥 Unlock Access", callback_data="buy_now")],
        [InlineKeyboardButton("👀 View Previews", callback_data="previews")],
        [InlineKeyboardButton("💬 Contact Support", url=SUPPORT_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)


def product_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Buy Access (Card)", url=STRIPE_URL)],
        [InlineKeyboardButton("₿ Buy Access (Crypto)", url=CRYPTO_URL)],
        [InlineKeyboardButton("← Back", callback_data="back_home")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    keyboard = [
        [InlineKeyboardButton("← Back", callback_data="back_home")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_home_caption():
    return f"""🚨 LIMITED ACCESS 🚨

👑 Strickly VIP

Exclusive private network access.

🔥 19 members joined today — limited spots remaining
{get_fake_activity()}

━━━━━━━━━━━━━━━

💳 Card & crypto accepted
⚡ Instant access after payment
🔒 Fully secure & private

━━━━━━━━━━━━━━━

Tap below to unlock access."""


def get_buy_caption():
    return """👑 Strickly VIP

Exclusive private network access.

🔥 19 members joined today — limited spots remaining

━━━━━━━━━━━━━━━

💳 Instant card checkout
₿ Crypto accepted
⚡ Access delivered after payment

━━━━━━━━━━━━━━━

Choose your payment method below."""


PREVIEW_TEXT = """👀 VIP Previews

See what members get access to:

• Premium content
• Private channels
• Daily updates
• Exclusive drops

━━━━━━━━━━━━━━━

Upgrade to unlock full access."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(BANNER_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=get_home_caption(),
            reply_markup=home_menu()
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_now":
        try:
            await query.message.delete()
        except Exception:
            pass

        with open(BANNER_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_buy_caption(),
                reply_markup=product_menu()
            )

    elif query.data == "previews":
        await query.edit_message_caption(
            caption=PREVIEW_TEXT,
            reply_markup=back_menu()
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
                reply_markup=home_menu()
            )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
