from telegram.ext import CommandHandler

from database import users_col

ADMIN_ID = 1864719844


# =========================
# BROADCAST
# =========================
async def broadcast(update, context):

    user_id = update.effective_user.id

    # ADMIN CHECK
    if user_id != ADMIN_ID:

        return

    message = update.message

    # =========================
    # REPLY CHECK
    # =========================
    if not message.reply_to_message:

        await message.reply_text(
            "❌ Reply To Any Message / Photo / Video\n\n"
            "Then Use:\n"
            "/broadcast"
        )

        return

    users = users_col.find()

    success = 0
    failed = 0

    status = await message.reply_text(
        "📢 Broadcasting Started..."
    )

    # =========================
    # SEND TO ALL USERS
    # =========================
    for user in users:

        try:

            await context.bot.copy_message(

                chat_id=user["user_id"],

                from_chat_id=message.chat.id,

                message_id=message.reply_to_message.message_id

            )

            success += 1

        except Exception:

            failed += 1

    # =========================
    # COMPLETED
    # =========================
    await status.edit_text(

        f"✅ Broadcast Completed\n\n"

        f"✅ Success : {success}\n"

        f"❌ Failed : {failed}"

    )


# =========================
# HANDLER
# =========================
broadcast_handler = CommandHandler(
    "broadcast",
    broadcast
)
