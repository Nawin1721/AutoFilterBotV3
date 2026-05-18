from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import files_col

RESULTS_PER_PAGE = 10


# =========================
# CREATE BUTTONS FUNCTION
# =========================
def build_buttons(results, bot_username, page=0):

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # TOP MENU
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

        buttons.append([
            InlineKeyboardButton(
                text=file["file_name"][:40],
                url=f"https://t.me/{bot_username}?start={file['_id']}"
            )
        ])

    # PAGINATION
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅ Prev",
                callback_data=f"page_{page-1}"
            )
        )

    if end < len(results):
        nav_buttons.append(
            InlineKeyboardButton(
                "Next ➡",
                callback_data=f"page_{page+1}"
            )
        )

    if nav_buttons:
        buttons.append(nav_buttons)

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
    search_user = context.user_data.get("search_user")

    if search_user and search_user != query.from_user.id:

        await query.answer(
            "❌ This is another user's search.",
            show_alert=True
        )

        return

    # =========================
    # GET RESULTS SAFE
    # =========================
    results = context.user_data.get("results", [])

    # =========================
    # HELP MENU
    # =========================
    if data == "help_menu":

        text = (
            "📚 Bot Commands\n\n"
            "/start - Start Bot\n"
            "/help - Show Help\n"
            "/request - Request Movie\n"
            "/stats - Admin Stats\n"
            "/broadcast - Admin Broadcast\n\n"
            "🎬 Search Movie Names In Group"
        )

        await query.message.edit_text(text)
        return

    # =========================
    # LANGUAGE MENU
    # =========================
    if data == "language_menu":

        if not results:

            await query.answer(
                "⚠️ Search Expired. Search Again.",
                show_alert=True
            )

            return

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
                    "⬅ Back",
                    callback_data="back_results"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            "🌐 Choose Language",
            reply_markup=reply_markup
        )

        return

    # =========================
    # QUALITY MENU
    # =========================
    if data == "quality_menu":

        if not results:

            await query.answer(
                "⚠️ Search Expired. Search Again.",
                show_alert=True
            )

            return

        buttons = [

            [
                InlineKeyboardButton(
                    "480p",
                    callback_data="quality_480p"
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
                    "⬅ Back",
                    callback_data="back_results"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            "🎥 Choose Quality",
            reply_markup=reply_markup
        )

        return

    # =========================
    # BACK TO RESULTS
    # =========================
    if data == "back_results":

        if not results:

            await query.answer(
                "⚠️ Search Expired.",
                show_alert=True
            )

            return

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

        original_query = context.user_data.get("original_query")

        if not original_query:

            await query.answer(
                "⚠️ Search Expired.",
                show_alert=True
            )

            return

        language = data.split("_")[1]

        new_query = f"{original_query} {language}"

        results = list(files_col.find({
            "$or": [

                {
                    "file_name": {
                        "$regex": new_query,
                        "$options": "i"
                    }
                },

                {
                    "caption": {
                        "$regex": new_query,
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

        original_query = context.user_data.get("original_query")

        if not original_query:

            await query.answer(
                "⚠️ Search Expired.",
                show_alert=True
            )

            return

        quality = data.split("_")[1]

        new_query = f"{original_query} {quality}"

        results = list(files_col.find({
            "$or": [

                {
                    "file_name": {
                        "$regex": new_query,
                        "$options": "i"
                    }
                },

                {
                    "caption": {
                        "$regex": new_query,
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

        if not results:

            await query.answer(
                "⚠️ Search Expired.",
                show_alert=True
            )

            return

        page = int(data.split("_")[1])

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
# HANDLER
# =========================
callback_handler = CallbackQueryHandler(
    button_click
)