from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from database import files_col

import asyncio

RESULTS_PER_PAGE = 10


# =========================
# FORMAT SIZE
# =========================
def human_size(size):

    try:

        size = int(size)

        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

        elif size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"

        elif size >= 1024:
            return f"{size / 1024:.2f} KB"

        else:
            return f"{size} B"

    except:

        return "Unknown"


# =========================
# SAFE EDIT
# =========================
async def safe_edit(message, text, reply_markup=None):

    try:

        # PHOTO MESSAGE
        if message.photo:

            await message.edit_caption(
                caption=text,
                reply_markup=reply_markup
            )

        # NORMAL MESSAGE
        else:

            await message.edit_text(
                text=text,
                reply_markup=reply_markup
            )

    except BadRequest as e:

        if "Message is not modified" in str(e):
            pass

        else:
            print(e)


# =========================
# BUILD BUTTONS
# =========================
def build_buttons(
    results,
    bot_username,
    search_id,
    page=0
):

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # FILTER BUTTONS
    buttons.append([

        InlineKeyboardButton(
            "🌐 Language",
            callback_data=f"language_{search_id}"
        ),

        InlineKeyboardButton(
            "🎥 Quality",
            callback_data=f"quality_{search_id}"
        )

    ])

    # FILE BUTTONS
    for file in current_results:

        size = human_size(
            file.get("file_size", 0)
        )

        text = f"[{size}] {file['file_name'][:45]}"

        buttons.append([

            InlineKeyboardButton(
                text=text,
                url=f"https://t.me/{bot_username}?start={file['_id']}"
            )

        ])

    # SEND ALL
    buttons.append([

        InlineKeyboardButton(
            "📥 Send All Files",
            callback_data=f"sendall_{search_id}_{page}"
        )

    ])

    # PAGINATION
    total_pages = (
        len(results) - 1
    ) // RESULTS_PER_PAGE + 1

    nav = []

    if page > 0:

        nav.append(

            InlineKeyboardButton(
                "⬅️ Back",
                callback_data=f"page_{search_id}_{page-1}"
            )

        )

    nav.append(

        InlineKeyboardButton(
            f"{page+1}/{total_pages}",
            callback_data="pages"
        )

    )

    if end < len(results):

        nav.append(

            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"page_{search_id}_{page+1}"
            )

        )

    buttons.append(nav)

    return InlineKeyboardMarkup(buttons)


# =========================
# DELETE PM FILE
# =========================
async def delete_pm_file(context):

    if not context.job:
        return

    data = context.job.data

    try:

        await context.bot.delete_message(
            chat_id=data["chat_id"],
            message_id=data["message_id"]
        )

    except:

        pass


# =========================
# CALLBACK MAIN
# =========================
async def button_click(update, context):

    query = update.callback_query

    await query.answer()

    data = query.data


    # =========================
    # HELP MENU
    # =========================
    if data == "help_menu":

        text = (

            "📚 Bot Help Menu\n\n"

            "🎬 Search Movie Names In Group\n"

            "📥 Files Will Be Sent In PM\n"

            "📤 Send All = Current Page Files\n"

            "🗑 Files Auto Delete After 5 Minutes\n\n"

            "⚡ Features:\n"

            "• IMDb Posters\n"

            "• Smart Search\n"

            "• Pagination\n"

            "• Multi-user Support\n"

            "• Fast AutoFilter"

        )

        buttons = [

            [

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="back_start"
                )

            ]

        ]

        try:

            await query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        except:

            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        return


    # =========================
    # BACK TO START
    # =========================
    if data == "back_start":

        text = (

            "🔥 Welcome To Our AutoFilter Bot 🔥\n\n"

            "🎬 Search Any Movie Name In Group\n"

            "📥 Files Will Be Sent In PM\n"

            "⚡ Fast & Smart Search\n"

            "🎭 IMDb Posters & Details\n"

            "📄 Pagination + Filters\n"

            "📤 Send All Files Feature"

        )

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

            ]

        ]

        try:

            await query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        except:

            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        return


    # =========================
    # PAGINATION
    # =========================
    if data.startswith("page_"):

        parts = data.split("_")

        search_id = parts[1]

        page = int(parts[2])

        cache = context.bot_data.get(search_id)

        if not cache:

            await query.answer(
                "⚠️ Search Expired",
                show_alert=True
            )

            return

        # USER PROTECTION
        if cache["user_id"] != query.from_user.id:

            await query.answer(
                "❌ This Search Belongs To Another User",
                show_alert=True
            )

            return

        results = cache["results"]

        reply_markup = build_buttons(
            results,
            context.bot.username,
            search_id,
            page
        )

        await safe_edit(
            query.message,
            f"🔍 Search Results\n📄 Page: {page+1}",
            reply_markup
        )

        return


    # =========================
    # SEND ALL
    # =========================
    if data.startswith("sendall_"):

        parts = data.split("_")

        search_id = parts[1]

        page = int(parts[2])

        cache = context.bot_data.get(search_id)

        if not cache:

            await query.answer(
                "⚠️ Search Expired",
                show_alert=True
            )

            return

        # USER PROTECTION
        if cache["user_id"] != query.from_user.id:

            await query.answer(
                "❌ This Search Belongs To Another User",
                show_alert=True
            )

            return

        results = cache["results"]

        start = page * RESULTS_PER_PAGE
        end = start + RESULTS_PER_PAGE

        current_results = results[start:end]

        status_msg = await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📤 Sending Files In PM..."
        )

        sent = 0

        for file in current_results:

            try:

                sent_file = await context.bot.copy_message(
                    chat_id=query.from_user.id,
                    from_chat_id=file["chat_id"],
                    message_id=file["message_id"]
                )

                context.application.job_queue.run_once(
                    delete_pm_file,
                    when=305,
                    data={
                        "chat_id": query.from_user.id,
                        "message_id": sent_file.message_id
                    }
                )

                sent += 1

                await asyncio.sleep(0.3)

            except Exception as e:

                print(e)

        warning_msg = await context.bot.send_message(
            chat_id=query.from_user.id,
            text="🗑 Deleting in 5Min, forward quickly…"
        )

        context.application.job_queue.run_once(
            delete_pm_file,
            when=305,
            data={
                "chat_id": query.from_user.id,
                "message_id": warning_msg.message_id
            }
        )

        await safe_edit(
            status_msg,
            f"✅ Sent {sent} Files In PM"
        )

        context.application.job_queue.run_once(
            delete_pm_file,
            when=20,
            data={
                "chat_id": status_msg.chat_id,
                "message_id": status_msg.message_id
            }
        )

        return


# =========================
# HANDLER
# =========================
callback_handler = CallbackQueryHandler(
    button_click
)
