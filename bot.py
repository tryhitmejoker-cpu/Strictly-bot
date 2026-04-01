import os
import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8080"))
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")

HOME_ANIMATION = "pika-video.mp4"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"
PREVIEWS_URL = "https://t.me/+EM4JGufTMKE2OWRk"
SUPPORT_URL = "https://t.me/StricklySupportbot"
REVIEWS_CHANNEL = "https://t.me/nuvouches"

JOINS_FILE = "joins.json"


# ---------------- JOINS ----------------
def load_joins():
    if Path(JOINS_FILE).exists():
        with open(JOINS_FILE, "r") as f:
            return json.load(f)
    return []


def save_joins(joins):
    with open(JOINS_FILE, "w") as f:
        json.dump(joins, f)


def record_join():
    joins = load_joins()
    joins.append(int(time.time()))
    cutoff = int(time.time()) - 86400
    joins = [x for x in joins if x >= cutoff]
    save_joins(joins)


def joins_last_hour():
    now = int(time.time())
    return sum(1 for x in load_joins() if x >= now - 3600)


# ---------------- HOME ----------------
def get_home_caption():
    joined = joins_last_hour()

    join_text = ""
    if joined > 0:
        join_text = f"🔥 {joined} {'person' if joined == 1 else 'people'} joined recently\n\n"

    return (
        join_text +
        "Private network access.\n\n"
        "Unlock access to all 10 VIP channels.\n\n"
        "• Instant access after payment\n"
        "• Secure checkout\n"
        "• Card accepted\n\n"
        "✅ 256-bit SSL encrypted"
    )


def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Unlock Access", callback_data="buy")],
        [InlineKeyboardButton("⭐ Reviews", callback_data="reviews")],
        [InlineKeyboardButton("👀 View Previews", url=PREVIEWS_URL)],
        [InlineKeyboardButton("💬 Support", url=SUPPORT_URL)],
    ])


async def send_home(message):
    with open(HOME_ANIMATION, "rb") as vid:
        await message.reply_animation(
            animation=vid,
            caption=get_home_caption(),
            reply_markup=home_menu(),
        )


async def send_home_to_chat(chat):
    with open(HOME_ANIMATION, "rb") as vid:
        await chat.send_animation(
            animation=vid,
            caption=get_home_caption(),
            reply_markup=home_menu(),
        )


# ---------------- BUY PAGE ----------------
def get_buy_caption():
    return (
        "🔐 PRIVATE NETWORK ACCESS\n\n"
        "Unlock access to all 10 VIP channels.\n\n"
        "What will you get joining VIP?\n\n"
        "• 320K of UK data\n"
        "• All new and upcoming channels\n"
        "• Exclusive members-only channel\n"
        "• Full Strickly VIP folder (10 channels)\n\n"
        "💰 Price: £15.00 (one-time)\n\n"
        "⚡ Instant access after payment\n"
        "🔒 Secure checkout\n"
        "💳 Card accepted"
    )


def buy_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy Now", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
    ])


# ---------------- REVIEWS ----------------
USERNAMES = [
    "Jack Thomas",
    "N/A",
    "ClaFo",
    "A",
    "Joel Miller",
    "Jay",
    "Frankie King",
    "C W",
    "U",
    "E M",
    "F",
    "BNF",
    "Johnlad",
    "John wick",
    "Kieran",
    "Rich",
    "L",
    "Aj",
    "seb",
    "benzino",
]

BASE_REVIEWS = [
    "Cl banging content always the best",
    "Been with strictly for a year now never let me down best in the game",
    "Best in the game",
    "Yh I joined thinking it was another bs channel but definitely changed my mind",
    "Worth it 100%",
    "10/10 tbf",
    "Content is mad on here",
    "Not gonna lie this is the best one I’ve joined",
    "Joined yesterday already worth it",
    "Love this group so much content",
    "Actually legit surprised",
    "Didn’t expect it to be this good",
    "Good group very good",
    "Unreal group",
    "Top tier content",
    "Proper value for money",
    "Best £15 spent",
    "Consistent uploads which is rare",
    "No other group compares",
    "Worth every penny",
]


def generate_review_data():
    now = datetime.now()
    mins = random.randint(60, 60 * 24 * 30)
    past = now - timedelta(minutes=mins)

    if mins <= 1440:
        views = random.randint(20, 60)
    elif mins <= 4320:
        views = random.randint(40, 90)
    elif mins <= 10080:
        views = random.randint(70, 130)
    else:
        views = random.randint(100, 180)

    time_txt = past.strftime("%d %b %H:%M")
    return str(views), time_txt


def generate_all_reviews():
    data = []

    for text in BASE_REVIEWS:
        if random.random() < 0.3:
            header = "Forwarded message"
        else:
            name = random.choice(USERNAMES)
            header = f"Forwarded from {name}"

        views, time_txt = generate_review_data()

        if random.random() < 0.25:
            text = text.lower()

        if random.random() < 0.2:
            text += random.choice([" 😂", " 🔥", " 👌", ""])

        full = f"{header}\n\n{text}\n\n👁 {views}   {time_txt}"
        data.append(full)

    return data


ALL_REVIEWS = generate_all_reviews()


def build_review(index):
    return ALL_REVIEWS[index]


def review_menu(index):
    total = len(ALL_REVIEWS)
    prev_index = total - 1 if index == 0 else index - 1
    next_index = 0 if index == total - 1 else index + 1

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️", callback_data=f"review_{prev_index}"),
            InlineKeyboardButton("▶️", callback_data=f"review_{next_index}")
        ],
        [InlineKeyboardButton("Unlock Access", callback_data="buy")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_home")]
    ])


async def send_reviews(chat, index=0):
    total = len(ALL_REVIEWS)
    text = (
        f"⭐ Reviews\n\n"
        f"{build_review(index)}\n\n"
        f"Review {index + 1} of {total}"
    )
    await chat.send_message(text, reply_markup=review_menu(index))


# ---------------- POPUP ----------------
async def delayed_vouch_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    await asyncio.sleep(30)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Check out our Reviews channel! 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Click here", url=REVIEWS_CHANNEL)]
        ]),
    )


# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    record_join()

    await update.message.reply_text(
        "Welcome to Strictly VIP 🔥\n\n"
        "Unlock access to all VIP channels instantly.\n\n"
        "Browse below 👇"
    )

    await send_home(update.message)

    asyncio.create_task(
        delayed_vouch_message(context, update.effective_chat.id)
    )


# ---------------- BUTTONS ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "reviews":
        try:
            await q.message.delete()
        except Exception:
            pass

        await send_reviews(q.message.chat, 0)

    elif q.data.startswith("review_"):
        index = int(q.data.split("_")[1])
        total = len(ALL_REVIEWS)

        if index < 0:
            index = total - 1
        elif index >= total:
            index = 0

        try:
            await q.message.delete()
        except Exception:
            pass

        await send_reviews(q.message.chat, index)

    elif q.data == "buy":
        try:
            await q.message.delete()
        except Exception:
            pass

        with open(BUY_IMAGE, "rb") as img:
            await q.message.chat.send_photo(
                photo=img,
                caption=get_buy_caption(),
                reply_markup=buy_menu(),
            )

    elif q.data == "back_home":
        try:
            await q.message.delete()
        except Exception:
            pass

        await send_home_to_chat(q.message.chat)


# ---------------- WEBHOOK ----------------
async def health(request):
    return web.Response(text="ok")


async def telegram_webhook(request):
    application = request.app["telegram_app"]
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return web.Response(text="ok")


async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")
    if not RAILWAY_PUBLIC_DOMAIN:
        raise ValueError("RAILWAY_PUBLIC_DOMAIN is not set")

    print("BOT TOKEN LOADED:", bool(TOKEN))
    print("HOME_ANIMATION EXISTS:", Path(HOME_ANIMATION).exists())
    print("BUY_IMAGE EXISTS:", Path(BUY_IMAGE).exists())

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))

    await application.initialize()
    await application.start()

    webhook_url = f"https://{RAILWAY_PUBLIC_DOMAIN}/webhook"
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(webhook_url)

    web_app = web.Application()
    web_app["telegram_app"] = application
    web_app.router.add_get("/", health)
    web_app.router.add_post("/webhook", telegram_webhook)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print("Webhook set:", webhook_url)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
