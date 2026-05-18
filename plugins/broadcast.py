from telegram.ext import CommandHandler

from database import users_col

ADMIN_ID = 1864719844


async def broadcast(update, context):

    user_id = update.effective_user.id

    # ADMIN CHECK
    if user_id != ADMIN_ID:

        return

    # MESSAGE CHECK
    if not context.args:

        await update.message.reply_text(
            "Usage:\n/broadcast your message"
        )

        return

    message = " ".join(context.args)

    users = users_col.find()

    success = 0
    failed = 0

    # SEND TO ALL USERS
    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user["user_id"],
                text=message
            )

            success += 1

        except:

            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast Completed\n\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )


broadcast_handler = CommandHandler(
    "broadcast",
    broadcast
)