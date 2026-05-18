from telegram.ext import CommandHandler

from database import files_col
from database import users_col
from database import requests_col

ADMIN_ID = 1864719844


async def stats(update, context):

    user_id = update.effective_user.id

    # ADMIN ONLY
    if user_id != ADMIN_ID:

        return

    total_files = files_col.count_documents({})
    total_users = users_col.count_documents({})
    total_requests = requests_col.count_documents({})

    text = (
        f"📊 Bot Statistics\n\n"
        f"👥 Users: {total_users}\n"
        f"📁 Files: {total_files}\n"
        f"📥 Requests: {total_requests}"
    )

    await update.message.reply_text(text)


stats_handler = CommandHandler(
    "stats",
    stats
)