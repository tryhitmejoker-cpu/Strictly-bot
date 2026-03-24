from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os

TOKEN = os.getenv("BOT_TOKEN")

SUPPORT_URL = "https://t.me/StricklySupportbot"
PREVIEWS_URL = "https://t.me/+EM4JGufTMKE2OWRk"

HOME_IMAGE = "3B02192C-77A1-49E4-9A12-31F2759144D6.png"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"


def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Buy Now", callback_data="buy_now")],
        [InlineKeyboardButton("View Previews", url=PREVIEWS_URL)],
        [InlineKeyboardButton("Support", url=SUPPORT_URL)],
    ])


def product_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Unlock Full Access", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("Back", callback_data="back_home")],
    ])


def get_home_caption():
    return """Private network access.

Unlock access to all 10 VIP channels.

• Instant access after payment
• Secure checkout
• Card accepted

🔒 256-bit SSL encrypted"""


def get_buy_caption():
    return """Strickly VIP

Unlock full access to all 10 VIP channels.

What will you get joining VIP?

• 320K of UK data
• All new and upcoming channels
• Exclusive members-only channel
• Full Strickly VIP folder (10 channels)

Price: £15.00 (one-time)

⚡ Instant access after payment
🔒 Secure checkout"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(HOME_IMAGE, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=get_home_caption(),
            reply_markup=home_menu(),
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy_now":
        try:
            await query.message.delete()
        except Exception:
            pass

        with open(BUY_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_buy_caption(),
                reply_markup=product_menu(),
            )

    elif query.data == "back_home":
        try:
            await query.message.delete()
        except Exception:
            pass

        with open(HOME_IMAGE, "rb") as photo:
            await query.message.chat.send_photo(
                photo=photo,
                caption=get_home_caption(),
                reply_markup=home_menu(),
            )


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
