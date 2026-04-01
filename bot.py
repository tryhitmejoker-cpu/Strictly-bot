from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio, random, time, json
from datetime import datetime, timedelta
from pathlib import Path

TOKEN = "YOUR_BOT_TOKEN"

HOME_ANIMATION = "pika-video.mp4"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"
REVIEWS_CHANNEL = "https://t.me/nuvouches"

JOINS_FILE = "joins.json"

# ---------------- JOINS ----------------
def load_joins():
    if Path(JOINS_FILE).exists():
        return json.load(open(JOINS_FILE))
    return []

def save_joins(j):
    json.dump(j, open(JOINS_FILE, "w"))

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
    actions = ["Someone just joined", "New member joined", "User unlocked access"]
    times = ["just now", "2m ago", "5m ago"]

    return "\n".join(
        f"🟢 {random.choice(actions)} ({random.choice(times)})"
        for _ in range(min(count, 3))
    )

# ---------------- REVIEWS ----------------
USERNAMES = [
    "Jack Thomas","N/A","ClaFo","A","Joel Miller","Jay",
    "Frankie King","C W","U","E M","F","BNF",
    "Johnlad","John wick","Kieran","Rich","L","Aj","seb","benzino"
]

BASE_REVIEWS = [
    "Best group on Telegram",
    "100% worth it best group",
    "Great group lots of content 🔥",
    "Absolutely brilliant group",
    "Top group 👌",
    "Legit 🔥",
    "Worth every penny",
    "Best group I’ve been on",
    "Consistent group",
    "Unreal group",
]

def generate_review_data():
    now = datetime.now()
    mins = random.randint(1, 60*24*14)
    past = now - timedelta(minutes=mins)

    if mins <= 2:
        return str(random.randint(2,6)), "just now"
    elif mins <= 15:
        return str(random.randint(10,17)), f"{mins}m ago"
    elif mins <= 1440:
        return str(random.randint(40,90)), past.strftime("%H:%M")
    elif mins <= 2880:
        return str(random.randint(80,130)), f"Yesterday {past.strftime('%H:%M')}"
    else:
        return str(random.randint(120,180)), past.strftime("%d %b %H:%M")

def build_review(index):
    name = "Deleted Account" if random.random() < 0.35 else random.choice(USERNAMES)
    header = "Forwarded message" if name == "Deleted Account" and random.random() < 0.3 else f"Forwarded from {name}"
    views, time_txt = generate_review_data()

    return f"{header}\n\n{BASE_REVIEWS[index]}\n\n👁 {views}   {time_txt}"

# ---------------- HOME ----------------
async def send_home(chat, index=0):
    total = len(BASE_REVIEWS)
    joins = joins_last_hour()

    join_text = ""
    if joins > 0:
        join_text = f"🔥 {joins} {'person' if joins==1 else 'people'} joined recently\n\n{generate_join_feed(joins)}\n\n"

    caption = (
        f"{join_text}"
        f"⭐ Reviews\n\n"
        f"{build_review(index)}\n\n"
        f"Review {index+1} of {total}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️", callback_data=f"review_{index-1}"),
            InlineKeyboardButton("▶️", callback_data=f"review_{index+1}")
        ],
        [InlineKeyboardButton("Unlock Access", callback_data="buy_now")]
    ])

    with open(HOME_ANIMATION, "rb") as vid:
        await chat.send_animation(vid, caption=caption, reply_markup=keyboard)

# ---------------- EDIT ----------------
async def edit_home(query, index):
    total = len(BASE_REVIEWS)
    joins = joins_last_hour()

    join_text = ""
    if joins > 0:
        join_text = f"🔥 {joins} {'person' if joins==1 else 'people'} joined recently\n\n{generate_join_feed(joins)}\n\n"

    caption = (
        f"{join_text}"
        f"⭐ Reviews\n\n"
        f"{build_review(index)}\n\n"
        f"Review {index+1} of {total}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◀️", callback_data=f"review_{index-1}"),
            InlineKeyboardButton("▶️", callback_data=f"review_{index+1}")
        ],
        [InlineKeyboardButton("Unlock Access", callback_data="buy_now")]
    ])

    await query.edit_message_caption(caption=caption, reply_markup=keyboard)

# ---------------- POPUP ----------------
async def delayed_vouch_message(ctx, chat_id):
    await asyncio.sleep(random.randint(25,40))

    await ctx.bot.send_message(
        chat_id=chat_id,
        text="Check out our Reviews channel! 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Click here", url=REVIEWS_CHANNEL)]
        ])
    )

# ---------------- START ----------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    record_join()
    await send_home(update.message, 0)

    asyncio.create_task(
        delayed_vouch_message(ctx, update.effective_chat.id)
    )

# ---------------- BUTTONS ----------------
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data.startswith("review_"):
        index = int(q.data.split("_")[1])
        total = len(BASE_REVIEWS)

        if index < 0:
            index = total - 1
        elif index >= total:
            index = 0

        await edit_home(q, index)

    elif q.data == "buy_now":
        try:
            await q.message.delete()
        except:
            pass

        with open(BUY_IMAGE, "rb") as img:
            await q.message.chat.send_photo(
                photo=img,
                caption="Unlock full access below.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 Buy Now", url="https://buy.stripe.com/aFadR2diP8qV67D5HY4gg0D")],
                    [InlineKeyboardButton("◀️ Back", callback_data="back_home")]
                ])
            )

    elif q.data == "back_home":
        try:
            await q.message.delete()
        except:
            pass

        await send_home(q.message.chat, 0)

# ---------------- RUN ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
