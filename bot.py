# (same imports as before)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from aiohttp import web
import asyncio, os, json, httpx, random, time
from datetime import datetime, timedelta
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8633029909
OXAPAY_API_KEY = os.getenv("OXAPAY_API_KEY")

FOLDER_LINK = "https://t.me/addlist/fi8vlP6OlSs0MGFk"
SUPPORT_URL = "https://t.me/StricklySupportbot"
PREVIEWS_URL = "https://t.me/+EM4JGufTMKE2OWRk"
REVIEWS_CHANNEL_URL = "https://t.me/nuvouches"

HOME_ANIMATION = "pika-video.mp4"
BUY_IMAGE = "5A808E7F-E9B5-4E98-A0F0-FB9D46BD4182.png"

STATS_FILE = "stats.json"
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
    "Frankie King","C W","U","E M","F","BNF","Johnlad",
    "John wick","Kieran","Rich","L","Aj","seb","benzino"
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

def build_review(i):
    name = "Deleted Account" if random.random()<0.35 else random.choice(USERNAMES)
    header = "Forwarded message" if name=="Deleted Account" and random.random()<0.3 else f"Forwarded from {name}"
    views,time_txt = generate_review_data()

    return f"{header}\n\n{BASE_REVIEWS[i]}\n\n👁 {views}   {time_txt}"

async def send_review_burst(chat, start=0):
    for i in range(random.choice([2,3,4])):
        idx=(start+i)%len(BASE_REVIEWS)
        await chat.send_message(build_review(idx))
        await asyncio.sleep(random.uniform(0.4,0.9))

    await chat.send_message(
        "⭐ Live Reviews",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️",callback_data="reviews"),
             InlineKeyboardButton("▶️",callback_data="reviews")],
            [InlineKeyboardButton("Unlock Access",callback_data="buy_now")]
        ])
    )

# ---------------- CAPTION ----------------
def get_home_caption():
    j=joins_last_hour()
    if j>0:
        return f"🔥 {j} {'person' if j==1 else 'people'} joined recently\n\n{generate_join_feed(j)}\n\nPrivate network access.\n\nUnlock access to all VIP channels."
    return "Private network access.\n\nUnlock access to all VIP channels."

# ---------------- MENU ----------------
def home_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Unlock Access",callback_data="buy_now")],
        [InlineKeyboardButton("⭐ Reviews",callback_data="reviews")],
        [InlineKeyboardButton("👀 Previews",url=PREVIEWS_URL)],
    ])

# ---------------- POPUP ----------------
async def delayed_vouch_message(ctx,chat_id):
    await asyncio.sleep(random.randint(25,40))
    await ctx.bot.send_message(
        chat_id=chat_id,
        text="Check out our Reviews channel! 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Click here",url=REVIEWS_CHANNEL_URL)]
        ])
    )

# ---------------- COMMANDS ----------------
async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    record_join()

    with open(HOME_ANIMATION,"rb") as vid:
        await update.message.reply_animation(
            vid,
            caption=get_home_caption(),
            reply_markup=home_menu()
        )

    asyncio.create_task(delayed_vouch_message(ctx,update.effective_chat.id))

# ---------------- BUTTONS ----------------
async def buttons(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query
    await q.answer()

    if q.data=="reviews":
        await send_review_burst(q.message.chat,random.randint(0,len(BASE_REVIEWS)-1))

    elif q.data=="buy_now":
        with open(BUY_IMAGE,"rb") as img:
            await q.message.reply_photo(img,caption="Unlock full access below.")

# ---------------- RUN ----------------
app=ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()
