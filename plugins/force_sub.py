from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import FORCE_SUB_CHANNEL

async def check_sub(update, context):

    user_id = update.effective_user.id

    try:

        member = await context.bot.get_chat_member(
            chat_id=f"@{FORCE_SUB_CHANNEL}",
            user_id=user_id
        )

        # USER JOINED
        if member.status in ["member", "administrator", "creator"]:
            return True

        return False

    except:

        return False

# FORCE SUB MESSAGE
async def force_sub_message(message):

    button = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=f"https://t.me/{FORCE_SUB_CHANNEL}"
            )
        ]
    ])

    await message.reply_text(
        "⚠ You Must Join Our Channel First",
        reply_markup=button
    )