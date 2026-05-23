from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bson import ObjectId

from config import FORCE_SUB_CHANNEL
from database import files_col

import random


# =========================
# RANDOM START IMAGES
# =========================
START_IMAGES = [

    "AgACAgUAAyEFAASWGOh9AAEMYlxqEIOUXM0ss2QU9RMz-Sz9CRl0EQACNRJrG55mgFSlqRVvcxeaIgEAAwIAA3cAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYl1qEIOiO6Lv-1UXo2GcB3p7yTXx6AACNhJrG55mgFTu5RNfoR4MWAEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYl5qEIOt6SjuDaMcfX1X45G9o0MzogACOBJrG55mgFTQmiq7z4hRawEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYl9qEIO38Nrfag95T7YE5YOLiB35KQACORJrG55mgFS3ggT4RSIMrwEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmBqEIPIokSpZDF0YZFv1juuQ8uJ0wACOhJrG55mgFTCHS7ujov83wEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmFqEIPs-SX9ybEiLUZfTl0T-O2xaQACPBJrG55mgFQqKPF_Wx4wmQEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmJqEIP3wNYY6X9dfWAVHU6CDL9GtgACPRJrG55mgFSiv5HdDNhIxAEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmNqEIQDZHrL2jMebA3_8RIzzo5jewACPxJrG55mgFQ3hRYIdcw5SAEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmRqEIQNeJn-_ObAYub2dyIQ2zB2BAACQBJrG55mgFQu-sLn4oUFkQEAAwIAA3kAAzsE",

    "AgACAgUAAyEFAASWGOh9AAEMYmVqEIZJ1Pgxb6-LAc1_aA1zTJ-tPgACVBJrG55mgFSTYD178h4_VgEAAwIAA3kAAzsE"

]


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
                    "❌ *File Not Found*",
                    parse_mode="Markdown"
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
                    "*🗑 Deleting in 5Min, forward quickly…*"   
                ),
                parse_mode="Markdown"
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
                "❌ *Bot Unblocked Cheshi Malli Try Cheyyandi.*",
                parse_mode="Markdown"
            )

            return

    # =========================
    # NORMAL START
    # =========================
    buttons = [

        [
            InlineKeyboardButton(
                "📢 Updates",
                url="https://t.me/Max_Files77"
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
        ],

        [
            InlineKeyboardButton(
                "💜 Contact Admin",
                url="https://t.me/Theadminor7_bot"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    text = (
        "🔥 *Welcome To Our AutoFilter Bot* 🔥\n\n"

        "🎬 *Search Any Movie Name In Group*\n"
        "📥 *Files Will Be Sent In PM*\n"
        "⚡ *Fast & Smart Search*\n"
        "🎭 *IMDb Posters & Details*\n"
        "📄 *Pagination + Filters*\n"
        "📤 *Send All Files Feature*\n\n"

        "⚠️ *PM Files Will Be Auto Deleted After Some Time.*\n"
        "📌 *Forward / Save Important Files Immediately.*"
    )

    # =========================
    # RANDOM IMAGE
    # =========================
    PHOTO_ID = random.choice(
        START_IMAGES
    )

    # =========================
    # SEND START PHOTO
    # =========================
    await msg.reply_photo(
        photo=PHOTO_ID,
        caption=text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# =========================
# HELP COMMAND
# =========================
async def help_command(update, context):

    text = (
        "📚 *Bot Commands*\n\n"

        "/start - Start Bot\n"
        "/help - Show Help\n"
        "/request - Request Movie\n"
        "/stats - Admin Stats\n"
        "/broadcast - Admin Broadcast\n\n"

        "🎬 *Simply Search Movie Names In Group*\n"
        "📥 *Files Will Be Delivered In PM*\n"
        "📤 *Use Send All Button To Get Full Page Files*"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


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
