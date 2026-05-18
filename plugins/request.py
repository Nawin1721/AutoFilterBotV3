from telegram.ext import CommandHandler
from database import requests_col

ADMIN_ID = 1864719844


async def request_movie(update, context):
    user = update.effective_user

    # CHECK REQUEST TEXT
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/request movie name"
        )
        return

    movie_name = " ".join(context.args)
    request_text = (
        f"🎬 New Movie Request\n\n"
        f"👤 User: {user.first_name}\n"
        f"🆔 ID: {user.id}\n\n"
        f"📥 Requested:\n{movie_name}"
    )

    # SAVE REQUEST
    requests_col.insert_one({
        "user_id": user.id,
        "movie_name": movie_name
    })

    # SEND TO ADMIN
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=request_text
    )
    # USER MESSAGE
    await update.message.reply_text(
        "✅ Your Request Sent To Admin"
    )


request_handler = CommandHandler(
    "request",
    request_movie
)