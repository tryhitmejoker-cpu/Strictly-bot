from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import os

TOKEN = os.getenv("BOT_TOKEN")


def main_menu():
    keyboard = [
        [InlineKeyboardButton("💳 Pay by Card", url="https://your-stripe-link.com")],
        [InlineKeyboardButton("₿ Pay by Crypto", url="https://your-crypto-link.com")],
        [InlineKeyboardButton("👀 Previews", callback_data="previews")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/yourusername")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="back_home")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """👋 Welcome to Strickly Shop

Premium digital access with instant delivery.

⚡ Fast & secure checkout
💳 Pay by card
₿ Crypto accepted
🔐 Fully encrypted access

👇 Choose an option below"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "previews":
        text = """👀 Previews

Here you can add:
• product screenshots
• sample results
• proof of quality
• customer feedback

Replace this text with your real preview details."""
        await query.edit_message_text(
            text=text,
            reply_markup=back_menu()
        )

    elif query.data == "back_home":
        text = """👋 Welcome to Strickly Shop

Premium digital access with instant delivery.

⚡ Fast & secure checkout
💳 Pay by card
₿ Crypto accepted
🔐 Fully encrypted access

👇 Choose an option below"""
        await query.edit_message_text(
            text=text,
            reply_markup=main_menu()
        )


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
