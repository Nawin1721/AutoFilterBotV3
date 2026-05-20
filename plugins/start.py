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

            # =========================
            # SEND FILE USING COPY MESSAGE
            # =========================
            sent_file = await context.bot.copy_message(
                chat_id=msg.chat.id,
                from_chat_id=file["chat_id"],
                message_id=file["message_id"]
            )

            # =========================
            # WARNING MESSAGE
            # =========================
            warning_msg = await context.bot.send_message(
                chat_id=msg.chat.id,
                text=(
                    "⚠️ Please Forward / Save This File Immediately.\n\n"
                    "🗑 This File Will Be Automatically Deleted After Some Time."
                )
            )

            # =========================
            # AUTO DELETE FILE
            # =========================
            context.application.job_queue.run_once(
                delete_pm_file,
                when=305,
                data={
                    "chat_id": msg.chat.id,
                    "message_id": sent_file.message_id
                }
            )

            # =========================
            # AUTO DELETE WARNING
            # =========================
            context.application.job_queue.run_once(
                delete_pm_file,
                when=305,
                data={
                    "chat_id": msg.chat.id,
                    "message_id": warning_msg.message_id
                }
            )

            return

        except Exception as e:

            print(f"ERROR: {e}")

            await msg.reply_text(
                "❌ Bot Unblocked Cheshi Malli Try Cheyyandi."
            )

            return

    # =========================
    # NORMAL START
    # =========================
    buttons = [

        [
            InlineKeyboardButton(
                "📢 Updates",
                url=f"https://t.me/{FORCE_SUB_CHANNEL}"
            ),

            InlineKeyboardButton(
                "❓ Help",
                callback_data="help_menu"
            )
        ],

        [
            InlineKeyboardButton(
                "🎬 Search Movies",
                url="https://t.me/Movie_Request777"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    text = (
        "🔥 Welcome To Professional AutoFilter Bot 🔥\n\n"

        "🎬 Search Any Movie Name In Group\n"
        "📥 Files Will Be Sent In PM\n"
        "⚡ Fast & Smart Search\n"
        "🎭 IMDb Posters & Details\n"
        "📄 Pagination + Filters\n"
        "📤 Send All Files Feature\n\n"

        "⚠️ PM Files Will Be Auto Deleted After Some Time.\n"
        "📌 Forward / Save Important Files Immediately."
    )

    await msg.reply_text(
        text,
        reply_markup=reply_markup
    )


# =========================
# HELP COMMAND
# =========================
async def help_command(update, context):

    text = (
        "📚 Bot Commands\n\n"

        "/start - Start Bot\n"
        "/help - Show Help\n"
        "/request - Request Movie\n"
        "/stats - Admin Stats\n"
        "/broadcast - Admin Broadcast\n\n"

        "🎬 Simply Search Movie Names In Group\n"
        "📥 Files Will Be Delivered In PM\n"
        "📤 Use Send All Button To Get Full Page Files"
    )

    await update.message.reply_text(text)


# =========================
# DELETE PM FILE
# =========================
async def delete_pm_file(context):

    if not context.job:
        return

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
