from telegram.ext import Application

from config import BOT_TOKEN

from plugins.start import photo_handler

from plugins.auto_index import auto_index
from plugins.search import search_handler
from plugins.callback import callback_handler
from plugins.broadcast import broadcast_handler
from plugins.request import request_handler
from plugins.stats import stats_handler
from plugins.start import start_handler, help_handler

from telegram.ext import MessageHandler, filters

# =========================
# GET PHOTO FILE ID
# =========================
async def get_photo_id(update, context):

    if update.message.photo:

        file_id = update.message.photo[-1].file_id

        await update.message.reply_text(
            f"{file_id}"
        )

photo_handler = MessageHandler(
    filters.PHOTO,
    get_photo_id
)

# from plugins.inline import inline_handler

app = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)

# AUTO INDEX
app.add_handler(auto_index)

# SEARCH
app.add_handler(search_handler)

# BUTTON CLICK
app.add_handler(callback_handler)

# BROADCAST
app.add_handler(broadcast_handler)

# REQUEST SYSTEM
app.add_handler(request_handler)

# STATS
app.add_handler(stats_handler)

# START & HELP
app.add_handler(start_handler)
app.add_handler(help_handler)
app.add_handler(photo_handler)

# INLINE SEARCH
# app.add_handler(inline_handler)

print("AutoFilter Bot Running 🔥")
print("Made By NAWIN 💖")

app.run_polling(
    drop_pending_updates=True
)
