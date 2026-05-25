from telegram.ext import Application

from config import BOT_TOKEN

from database import create_indexes

from plugins.auto_index import auto_index
from plugins.search import search_handler
from plugins.callback import callback_handler
from plugins.broadcast import broadcast_handler
from plugins.request import request_handler
from plugins.stats import stats_handler
from plugins.start import start_handler, help_handler

import asyncio


# =========================
# STARTUP FUNCTION
# =========================
async def startup(app):

    print("Starting Bot...")

    # CREATE INDEXES
    await create_indexes()

    print("MongoDB Ready ✅")

    print("Bot Started Successfully 🚀")


# =========================
# BUILD APPLICATION
# =========================
app = (
    Application.builder()
    .token(BOT_TOKEN)
    .concurrent_updates(True)
    .build()
)


# =========================
# STARTUP CALLBACK
# =========================
app.post_init = startup


# =========================
# AUTO INDEX
# =========================
app.add_handler(auto_index)


# =========================
# SEARCH
# =========================
app.add_handler(search_handler)


# =========================
# CALLBACKS
# =========================
app.add_handler(callback_handler)


# =========================
# BROADCAST
# =========================
app.add_handler(broadcast_handler)


# =========================
# REQUEST
# =========================
app.add_handler(request_handler)


# =========================
# STATS
# =========================
app.add_handler(stats_handler)


# =========================
# START & HELP
# =========================
app.add_handler(start_handler)

app.add_handler(help_handler)


# =========================
# BOT START
# =========================
print("AutoFilter Bot Running 🔥")

print("Made By NAWIN 💖")


app.run_polling(
    drop_pending_updates=True
)
