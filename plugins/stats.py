from telegram.ext import CommandHandler

from database import (
    files_col,
    users_col,
    requests_col
)

ADMIN_ID = 1864719844


# =========================
# STATS COMMAND
# =========================
async def stats(update, context):

    user_id = update.effective_user.id

    # ADMIN ONLY
    if user_id != ADMIN_ID:

        return


    # =========================
    # DATABASE COUNTS
    # =========================
    total_files = await files_col.count_documents({})

    total_users = await users_col.count_documents({})

    total_requests = await requests_col.count_documents({})


    # =========================
    # TEXT
    # =========================
    text = (

        "📊 Bot Statistics\n\n"

        f"👥 Users: {total_users}\n"

        f"📁 Files: {total_files}\n"

        f"📥 Requests: {total_requests}"

    )


    # =========================
    # SEND MESSAGE
    # =========================
    await update.message.reply_text(text)


# =========================
# HANDLER
# =========================
stats_handler = CommandHandler(
    "stats",
    stats
)
