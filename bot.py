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


def generate_join_feed(count: int) -> str:
    actions = [
        "Someone just joined",
        "New member joined",
        "User unlocked access",
        "New VIP member joined",
        "Someone just got access",
    ]
    times = ["just now", "1m ago", "2m ago", "3m ago", "5m ago"]

    lines = []
    for _ in range(min(count, 3)):
        lines.append(f"🟢 {random.choice(actions)} ({random.choice(times)})")
    return "\n".join(lines)


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
    "Best 🇮🇪&🇬🇧 group around",
    "Amazing group, worth it 👌🏻",
    "Easily the best group around definitely worth it",
    "100% worth it best group",
    "Best group on Telegram",
    "By far telegrams best groups",
    "The best group. No others compare and the ones that do come close nicked all their shit from here anyway 😂",
    "12 out of 10 points for this group",
    "Absolutely outstanding stuff! Well worth it 👏",
    "Wonderful group 🔥",
    "Good group very good",
    "The group and channels are amazing",
    "Legit and well worth it",
    "Best group I’ve ever been in 🔥",
    "Best group on tele for sure",
    "The best, regularly updates",
    "Consistent group",
    "Dayyum this group is good",
    "Great group, 10/10 content",
    "10/10 best group about",
    "This is a fire group so much content 🔥",
    "Best group on tele by far stacked with content",
    "Yh great group tbf worth it",
    "Great groups and an absolute bargain",
    "Love this group so worth it",
    "Good chat. Good price",
    "Top group 👌",
    "Legit 🔥",
    "10/10 🔥",
    "Best group on the app 🫡",
    "100 percent best group 👌",
    "Definitely worth it 100%",
    "Very worth it 👌",
    "Brilliant group",
    "Good group",
    "Very good group!",
    "Best about",
    "Awesome",
    "Love this group",
    "Best group I’ve been on",
    "100% worth it. Top tier 👌",
    "Excellent group 🔥",
    "Not a better group around!",
    "Class group!!",
    "Best telegram group",
    "Certi group 😮‍💨",
    "Worth every penny",
    "Absolutely brilliant group",
    "Great group lots of content 🔥",
    "Group is excellent 👌",
    "Group is brilliant 👍",
    "Great groups",
    "The best group",
    "Great group",
    "Unreal group",
    "Best about 👏🏻",
]


def generate_review_data():
    now = datetime.now()
    mins = random.randint(1, 60 * 24 * 14)
    past = now - timedelta(minutes=mins)

    if mins <= 2:
        time_text = "just now"
        views = random.randint(2, 6)
    elif mins <= 15:
        time_text = f"{mins}m ago"
        views = random.randint(10, 17)
    elif mins <= 1440:
        time_text = past.strftime("%H:%M")
        views = random.randint(40, 90)
    elif mins <= 2880:
        time_text = f"Yesterday {past.strftime('%H:%M')}"
        views = random.randint(80, 130)
    else:
        time_text = past.strftime("%d %b %H:%M")
        views = random.randint(120, 180)

    views += random.randint(-2, 2)
    return str(max(1, views)), time_text


def build_review(index: int) -> str:
    if random.random() < 0.35:
        name = "Deleted Account"
    else:
        name = random.choice(USERNAMES)

    if name == "Deleted Account" and random.random() < 0.3:
        header = "Forwarded message"
    else:
        header = f"Forwarded from {name}"

    views, time_txt = generate_review_data()
    return f"{header}\n\n{BASE_REVIEWS[index]}\n\n👁 {views}   {time_txt}"


def build_home_caption(index: int) -> str:
    total = len(BASE_REVIEWS)
    joins = joins_last_hour()

    join_text = ""
    if joins > 0:
        join_text = (
            f"🔥 {joins} {'person' if joins == 1 else 'people'} joined recently\n\n"
            f"{generate_join_feed(joins)}\n\n"
        )

    return (
        f"{join_text}"
        f"⭐ Reviews\n\n"
        f"{build_review(index)}\n\n"
        f"Review {index + 1} of {total}"
    )


def home_menu(index: int) -> InlineKeyboardMarkup:
    total = len(BASE_REVIEWS)
    prev_index = total - 1 if index == 0 else index - 1
    next_index = 0 if index == total - 1 else index + 1

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️", callback_data=f"review_{prev_index}"),
            InlineKeyboardButton("▶️", callback_data=f"review_{next_index}"),
        ],
        [InlineKeyboardButton("Unlock Access", callback_data="buy_now")],
    ])


def buy_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy Now", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
        [InlineKeyboardButton("◀️ Back", callback_data="back_home")],
    ])


# ---------------- HOME ----------------
async def send_home(chat, index: int = 0):
    caption = build_home_caption(index)

    with open(HOME_ANIMATION, "rb") as vid:
        await chat.send_animation(
            animation=vid,
            caption=caption,
            reply_markup=home_menu(index),
        )


async def edit_home(query, index: int):
    caption = build_home_caption(index)

    await query.edit_message_caption(
        caption=caption,
        reply_markup=home_menu(index),
    )


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
    await send_home(update.message, 0)

    asyncio.create_task(
        delayed_vouch_message(context, update.effective_chat.id)
    )


# ---------------- BUTTONS ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data.startswith("review_"):
        index = int(q.data.split("_")[1])
        await edit_home(q, index)

    elif q.data == "buy_now":
        try:
            await q.message.delete()
        except Exception:
            pass

        with open(BUY_IMAGE, "rb") as img:
            await q.message.chat.send_photo(
                photo=img,
                caption=(
                    "Strickly VIP\n\n"
                    "Unlock full access to all 10 VIP channels.\n\n"
                    "What will you get joining VIP?\n\n"
                    "• 320K of UK data\n"
                    "• All new and upcoming channels\n"
                    "• Exclusive members-only channel\n"
                    "• Full Strickly VIP folder (10 channels)\n\n"
                    "Price: £15.00 (one-time)\n\n"
                    "⚡ Instant access after payment\n"
                    "🔒 Secure checkout"
                ),
                reply_markup=buy_menu(),
            )

    elif q.data == "back_home":
        try:
            await q.message.delete()
        except Exception:
            pass

        await send_home(q.message.chat, 0)


# ---------------- WEB ----------------
async def health(request):
    return web.Response(text="ok")


async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")
    if not RAILWAY_PUBLIC_DOMAIN:
        raise ValueError("RAILWAY_PUBLIC_DOMAIN is not set")

    print("BOT TOKEN LOADED:", bool(TOKEN))
    print("HOME_ANIMATION EXISTS:", Path(HOME_ANIMATION).exists())
    print("BUY_IMAGE EXISTS:", Path(BUY_IMAGE).exists())

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    await app.initialize()
    await app.start()

    webhook_url = f"https://{RAILWAY_PUBLIC_DOMAIN}/telegram"
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_webhook(webhook_url)

    aio_app = web.Application()
    aio_app.router.add_get("/", health)
    aio_app.router.add_post("/telegram", app.webhook_update_handler)

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    print("Webhook set:", webhook_url)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
