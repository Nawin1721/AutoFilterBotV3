from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import files_col

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
# SEARCH PATTERN
# =========================
def create_search_pattern(query):

    query = query.lower()

    query = (
        query
        .replace("(", " ")
        .replace(")", " ")
        .replace("[", " ")
        .replace("]", " ")
        .replace(".", " ")
        .replace("_", " ")
        .replace("-", " ")
    )

    words = query.split()

    pattern = ".*".join(words)

    return pattern


# =========================
# BUILD BUTTONS
# =========================
def build_buttons(results, bot_username, page=0):

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # FILTER BUTTONS
    buttons.append([

        InlineKeyboardButton(
            "🌐 Language",
            callback_data="language_menu"
        ),

        InlineKeyboardButton(
            "🎥 Quality",
            callback_data="quality_menu"
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
            callback_data=f"sendall_{page}"
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
                callback_data=f"page_{page-1}"
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
                callback_data=f"page_{page+1}"
            )

        )

    buttons.append(nav)

    return InlineKeyboardMarkup(buttons)


# =========================
# CALLBACK MAIN
# =========================
async def button_click(update, context):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =========================
    # USER PROTECTION
    # =========================
    search_user = context.user_data.get(
        "search_user"
    )

    if search_user:

        if search_user != query.from_user.id:

            await query.answer(
                "❌ This Search Belongs To Another User",
                show_alert=True
            )

            return

    # =========================
    # GET RESULTS
    # =========================
    results = context.user_data.get(
        "results",
        []
    )

    # =========================
    # HELP MENU
    # =========================
    if data == "help_menu":

        text = (
            "📚 Bot Commands\n\n"
            "/start - Start Bot\n"
            "/help - Help Menu\n"
            "/request - Request Movie\n"
            "/stats - Bot Stats\n"
            "/broadcast - Broadcast\n\n"
            "🎬 Search Movie Names In Group"
        )

        await query.message.edit_text(text)

        return

    # =========================
    # SEND ALL
    # =========================
    if data.startswith("sendall_"):

        if not results:

            await query.answer(
                "⚠️ Search Expired",
                show_alert=True
            )

            return

        page = int(
            data.split("_")[1]
        )

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

                # AUTO DELETE PM FILE
                context.application.job_queue.run_once(
                    delete_pm_file,
                    when=305,
                    data={
                        "chat_id": query.from_user.id,
                        "message_id": sent_file.message_id
                    }
                )

                sent += 1

            except Exception as e:

                print(e)

        # WARNING MESSAGE
        warning_msg = await context.bot.send_message(
            chat_id=query.from_user.id,
            text=(
                "⚠️ Please Save / Forward Files Immediately.\n\n"
                "🗑 Files Will Be Deleted Automatically."
            )
        )

        # AUTO DELETE WARNING
        context.application.job_queue.run_once(
            delete_pm_file,
            when=305,
            data={
                "chat_id": query.from_user.id,
                "message_id": warning_msg.message_id
            }
        )

        await status_msg.edit_text(
            f"✅ Sent {sent} Files In PM"
        )

        return

    # =========================
    # LANGUAGE MENU
    # =========================
    if data == "language_menu":

        buttons = [

            [

                InlineKeyboardButton(
                    "English",
                    callback_data="lang_english"
                ),

                InlineKeyboardButton(
                    "Hindi",
                    callback_data="lang_hindi"
                )

            ],

            [

                InlineKeyboardButton(
                    "Tamil",
                    callback_data="lang_tamil"
                ),

                InlineKeyboardButton(
                    "Telugu",
                    callback_data="lang_telugu"
                )

            ],

            [

                InlineKeyboardButton(
                    "🗑️ Clear",
                    callback_data="clear_results"
                ),

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="back_results"
                )

            ]

        ]

        await query.message.edit_text(
            "🌐 Choose Language",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    # =========================
    # QUALITY MENU
    # =========================
    if data == "quality_menu":

        buttons = [

            [

                InlineKeyboardButton(
                    "360p",
                    callback_data="quality_360p"
                ),

                InlineKeyboardButton(
                    "480p",
                    callback_data="quality_480p"
                )

            ],

            [

                InlineKeyboardButton(
                    "576p",
                    callback_data="quality_576p"
                ),

                InlineKeyboardButton(
                    "720p",
                    callback_data="quality_720p"
                )

            ],

            [

                InlineKeyboardButton(
                    "1080p",
                    callback_data="quality_1080p"
                ),

                InlineKeyboardButton(
                    "2160p",
                    callback_data="quality_2160p"
                )

            ],

            [

                InlineKeyboardButton(
                    "🗑️ Clear",
                    callback_data="clear_results"
                ),

                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="back_results"
                )

            ]

        ]

        await query.message.edit_text(
            "🎥 Choose Quality",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        return

    # =========================
    # CLEAR RESULTS
    # =========================
    if data == "clear_results":

        reply_markup = build_buttons(
            results,
            context.bot.username,
            page=0
        )

        await query.message.edit_text(
            "🔍 Search Results\n📄 Page: 1",
            reply_markup=reply_markup
        )

        return

    # =========================
    # BACK RESULTS
    # =========================
    if data == "back_results":

        reply_markup = build_buttons(
            results,
            context.bot.username,
            page=0
        )

        await query.message.edit_text(
            "🔍 Search Results\n📄 Page: 1",
            reply_markup=reply_markup
        )

        return

    # =========================
    # LANGUAGE FILTER
    # =========================
    if data.startswith("lang_"):

        original_query = context.user_data.get(
            "original_query"
        )

        language = data.split("_")[1]

        new_query = f"{original_query} {language}"

        pattern = create_search_pattern(
            new_query
        )

        results = list(files_col.find({

            "$or": [

                {
                    "search_text": {
                        "$regex": pattern,
                        "$options": "i"
                    }
                },

                {
                    "caption": {
                        "$regex": pattern,
                        "$options": "i"
                    }
                }

            ]

        }))

        if not results:

            await query.answer(
                "❌ No Results Found",
                show_alert=True
            )

            return

        context.user_data["results"] = results

        reply_markup = build_buttons(
            results,
            context.bot.username,
            page=0
        )

        await query.message.edit_text(
            f"🌐 Results For: {language.upper()}\n📄 Page: 1",
            reply_markup=reply_markup
        )

        return

    # =========================
    # QUALITY FILTER
    # =========================
    if data.startswith("quality_"):

        original_query = context.user_data.get(
            "original_query"
        )

        quality = data.split("_")[1]

        new_query = f"{original_query} {quality}"

        pattern = create_search_pattern(
            new_query
        )

        results = list(files_col.find({

            "$or": [

                {
                    "search_text": {
                        "$regex": pattern,
                        "$options": "i"
                    }
                },

                {
                    "caption": {
                        "$regex": pattern,
                        "$options": "i"
                    }
                }

            ]

        }))

        if not results:

            await query.answer(
                "❌ No Results Found",
                show_alert=True
            )

            return

        context.user_data["results"] = results

        reply_markup = build_buttons(
            results,
            context.bot.username,
            page=0
        )

        await query.message.edit_text(
            f"🎥 Results For: {quality}\n📄 Page: 1",
            reply_markup=reply_markup
        )

        return

    # =========================
    # PAGINATION
    # =========================
    if data.startswith("page_"):

        page = int(
            data.split("_")[1]
        )

        reply_markup = build_buttons(
            results,
            context.bot.username,
            page=page
        )

        await query.message.edit_text(
            f"🔍 Search Results\n📄 Page: {page+1}",
            reply_markup=reply_markup
        )

        return


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

    except Exception as e:

        print(e)


# =========================
# HANDLER
# =========================
callback_handler = CallbackQueryHandler(
    button_click
)
