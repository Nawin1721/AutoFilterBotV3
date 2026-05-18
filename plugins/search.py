from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bson import ObjectId

from config import FORCE_SUB_CHANNEL
from database import files_col


# =========================
# START COMMAND
# =========================
async def start(update, context):

    msg = update.message

    args = context.args

    # =========================
    # FILE START PARAMETER
    # =========================
    if args:

        file_id = args[0]

        try:

            file = files_col.find_one({
                "_id": ObjectId(file_id)
            })

            if not file:

                await msg.reply_text(
                    "❌ File Not Found"
                )

                return

            # SEND FILE USING COPY MESSAGE
            sent_file = await context.bot.copy_message(
                chat_id=msg.chat.id,
                from_chat_id=file["chat_id"],
                message_id=file["message_id"]
            )

            # AUTO DELETE AFTER 30 MINUTES
            context.job_queue.run_once(
                delete_pm_file,
                when=1800,
                data={
                    "chat_id": msg.chat.id,
                    "message_id": sent_file.message_id
                }
            )

            return

        except Exception as e:

            print(e)

            await msg.reply_text(
                f"ERROR:\n{e}"
            )

            return

    # =========================
    # NORMAL START
    # =========================
    buttons = [
        [
            InlineKeyboardButton(
                "📢 Updates Channel",
                url=f"https://t.me/{FORCE_SUB_CHANNEL}"
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Help",
                callback_data="help_menu"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    text = (
        "<b>🔥 Welcome To AutoFilter Bot 🔥</b>\n\n"
        "🎬 Search Any Movie In Group\n"
        "📥 Files Will Be Sent In PM\n\n"
        "⚡ Fast Search\n"
        "🎭 IMDb Posters\n"
        "📄 Pagination System"
    )

    await msg.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


# =========================
# HELP COMMAND
# =========================
async def help_command(update, context):

    text = (
        "<b>📚 Bot Commands</b>\n\n"
        "/start - Start Bot\n"
        "/help - Show Help\n"
        "/request - Request Movie\n"
        "/stats - Admin Stats\n"
        "/broadcast - Admin Broadcast\n\n"
        "🎬 Simply Search Movie Names In Group"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================
# DELETE PM FILE
# =========================
async def delete_pm_file(context):

    job = context.job

    data = job.data

    try:

        await context.bot.delete_message(
            chat_id=data["chat_id"],
            message_id=data["message_id"]
        )

    except:

        pass


# =========================
# HANDLERS
# =========================
start_handler = CommandHandler(
    "start",
    start
)

help_handler = CommandHandler(
    "help",
    help_command
)
