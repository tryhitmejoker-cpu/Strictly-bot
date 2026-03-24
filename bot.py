from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os

TOKEN = os.getenv("BOT_TOKEN")

STRIPE_URL = "https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D"
CRYPTO_URL = "https://your-crypto-link.com"
SUPPORT_URL = "https://t.me/yourusername"
BANNER_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"


def home_menu():
    keyboard = [
        [InlineKeyboardButton("🛍 Buy Now", callback_data="buy_now")],
        [InlineKeyboardButton("👀 Previews", callback_data="previews")],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)


def product_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Pay by Card", url=STRIPE_URL)],
        [InlineKeyboardButton("₿ Pay by Crypto", url=CRYPTO_URL)],
        [InlineKeyboardButton("← Back", callback_data="back_home")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    keyboard = [
        [InlineKeyboardButton("← Back", callback_data="back_home")]
    ]
    return InlineKeyboardMarkup(keyboard)


HOME_TEXT = """Welcome to Strickly VIP

Private access with instant delivery.

• Card & crypto accepted
• Secure checkout
• Instant access

Choose an option below."""

PREVIEW_TEXT = """Previews

Add screenshots, proof, or sample content here."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=HOME_TEXT,
        reply_markup=home_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_now":
        await query.message.delete()
        with open(BANNER_IMAGE, "rb") as photo_file:
            await query.message.chat.send_photo(
                photo=photo_file,
                caption="""Strickly VIP

Private access with instant delivery.

• Secure checkout
• Instant access
• Card & crypto accepted

Choose payment below.""",
                reply_markup=product_menu()
            )

    elif query.data == "previews":
        await query.edit_message_text(
            text=PREVIEW_TEXT,
            reply_markup=back_menu()
        )

    elif query.data == "back_home":
        try:
            await query.message.delete()
        except Exception:
            pass

        await query.message.chat.send_message(
            text=HOME_TEXT,
            reply_markup=home_menu()
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
