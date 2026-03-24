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

HOME_IMAGE = "D2C62FE2-483E-4CF2-B7B9-28518D74785D.png"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"


def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Buy Now", callback_data="buy_now")],
        [InlineKeyboardButton("View Previews", url=PREVIEWS_URL)],
        [InlineKeyboardButton("Support", url=SUPPORT_URL)],
    ])


def product_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Unlock Full Access (£15)", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("Back", callback_data="back_home")],
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

Unlock full access to all 10 VIP channels.

27 members joined in the last 24 hours.

What you get:
• Private VIP network access
• Daily updates & drops
• Exclusive content

Price: £15.00 (one-time)

Instant access delivered after payment.

Tap below to unlock access."""


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
