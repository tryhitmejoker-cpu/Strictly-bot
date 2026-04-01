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
REVIEWS_CHANNEL = "https://t.me/nuvouches"

JOINS_FILE = "joins.json"


# ---------------- JOINS ----------------
def load_joins():
    if Path(JOINS_FILE).exists():
        with open(JOINS_FILE, "r") as f:
            return json.load(f)
    return []


def save_joins(j):
    with open(JOINS_FILE, "w") as f:
        json.dump(j, f)


def record_join():
    j = load_joins()
    j.append(int(time.time()))
    cutoff = int(time.time()) - 86400
    j = [x for x in j if x >= cutoff]
    save_joins(j)


def joins_last_hour():
    now = int(time.time())
    return sum(1 for x in load_joins() if x >= now - 3600)


def generate_join_feed(count):
    actions = ["Someone just joined", "New member joined"]
    times = ["just now", "1m ago", "2m ago", "3m ago"]

    return "\n".join(
        f"🟢 {random.choice(actions)} ({random.choice(times)})"
        for _ in range(min(count, 3))
    )


# ---------------- REVIEWS ----------------
REVIEWS = [
    "Best group on Telegram",
    "Amazing group, worth it 👌",
    "100% worth it best group",
    "Easily the best group around",
    "Top group 🔥",
    "Very worth it 👌",
    "Brilliant group",
    "Best about",
    "Love this group",
    "10/10 🔥",
]


def generate_review(index):
    now = datetime.now()
    mins = random.randint(1, 1440)

    if mins <= 2:
        time_txt = "just now"
        views = random.randint(2, 6)
    elif mins <= 10:
        time_txt = f"{mins}m ago"
        views = random.randint(10, 17)
    else:
        time_txt = now.strftime("%H:%M")
        views = random.randint(40, 120)

    return f"{REVIEWS[index]}\n\n👁 {views}   {time_txt}"


def build_caption(index):
    joins = joins_last_hour()

    join_text = ""
    if joins > 0:
        join_text = f"🔥 {joins} joined recently\n\n{generate_join_feed(joins)}\n\n"

    return (
        f"{join_text}"
        f"⭐ Reviews\n\n"
        f"{generate_review(index)}\n\n"
        f"Review {index+1} of {len(REVIEWS)}"
    )


def home_menu(index):
    total = len(REVIEWS)
    prev_i = total - 1 if index == 0 else index - 1
    next_i = 0 if index == total - 1 else index + 1

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️", callback_data=f"r_{prev_i}"),
            InlineKeyboardButton("▶️", callback_data=f"r_{next_i}"),
        ],
        [InlineKeyboardButton("Unlock Access", callback_data="buy")],
    ])


def buy_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy Now", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("◀️ Back", callback_data="back")],
    ])


# ---------------- HOME ----------------
async def send_home(message, index=0):
    caption = build_caption(index)

    with open(HOME_ANIMATION, "rb") as vid:
        await message.reply_animation(
            animation=vid,
            caption=caption,
            reply_markup=home_menu(index),
        )


async def edit_home(query, index):
    await query.edit_message_caption(
        caption=build_caption(index),
        reply_markup=home_menu(index),
    )


# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record_join()
    await send_home(update.message, 0)


# ---------------- BUTTONS ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data.startswith("r_"):
        i = int(q.data.split("_")[1])
        await edit_home(q, i)

    elif q.data == "buy":
        try:
            await q.message.delete()
        except:
            pass

        with open(BUY_IMAGE, "rb") as img:
            await q.message.chat.send_photo(
                photo=img,
                caption="Unlock full VIP access\n\n£15 one-time",
                reply_markup=buy_menu(),
            )

    elif q.data == "back":
        try:
            await q.message.delete()
        except:
            pass

        await send_home(q.message, 0)


# ---------------- WEBHOOK ----------------
async def webhook_handler(request):
    app = request.app["bot"]
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.update_queue.put(update)
    return web.Response()


async def main():
    if not TOKEN:
        raise Exception("No BOT_TOKEN")
    if not RAILWAY_PUBLIC_DOMAIN:
        raise Exception("No DOMAIN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    await app.initialize()
    await app.start()

    webhook = f"https://{RAILWAY_PUBLIC_DOMAIN}/webhook"
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(webhook)

    web_app = web.Application()
    web_app["bot"] = app
    web_app.router.add_post("/webhook", webhook_handler)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print("RUNNING:", webhook)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
