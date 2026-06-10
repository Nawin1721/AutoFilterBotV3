from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Forbidden


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

        if message.photo:

            await message.edit_caption(
                caption=text, reply_markup=reply_markup, parse_mode="HTML"
            )

        else:

            await message.edit_text(
                text=text, reply_markup=reply_markup, parse_mode="HTML"
            )

    except BadRequest as e:

        if "Message is not modified" in str(e):
            pass

        else:
            print(e)


# =========================
# BUILD BUTTONS
# =========================
def build_buttons(results, bot_username, search_id, page=0):

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # FILTER BUTTONS
    buttons.append(
        [
            InlineKeyboardButton("🌐 Language", callback_data=f"language_{search_id}"),
            InlineKeyboardButton("🎥 Quality", callback_data=f"quality_{search_id}"),
        ]
    )

    # FILE BUTTONS
    for file in current_results:

        size = human_size(file.get("file_size", 0))

        text = f"[{size}] {file['file_name'][:45]}"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=text, url=f"https://t.me/{bot_username}?start={file['_id']}"
                )
            ]
        )

    # SEND ALL
    buttons.append(
        [
            InlineKeyboardButton(
                "📥 Send All Files", callback_data=f"sendall_{search_id}_{page}"
            )
        ]
    )

    # PAGINATION
    total_pages = (len(results) - 1) // RESULTS_PER_PAGE + 1

    nav = []

    if page > 0:

        nav.append(
            InlineKeyboardButton("⬅️ Back", callback_data=f"page_{search_id}_{page-1}")
        )

    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="pages"))

    if end < len(results):

        nav.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"page_{search_id}_{page+1}")
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
            chat_id=data["chat_id"], message_id=data["message_id"]
        )

    except:

        pass


# =========================
# CALLBACK MAIN
# =========================
async def button_click(update, context):

    query = update.callback_query

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

        buttons = [[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]

        await safe_edit(query.message, text, InlineKeyboardMarkup(buttons))

        return

    # =========================
    # BACK TO START
    # =========================
    if data == "back_start":

        text = (
            f"👋 Hey Broh 🚩, Nice To Meet You\n\n"
            "Here You Can Get Movies And Series Inside The Bot,\n"
            "Just Send Movie Or Series Name With Proper Spelling..!!\n\n"
            "➤ Controlled By : "
            '<a href="https://t.me/max_Files7">Max_Files7💜</a>'
        )

        buttons = [
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/Max_Files77"),
                InlineKeyboardButton("❓ Help", callback_data="help_menu"),
            ],
            [
                InlineKeyboardButton(
                    "🎬 Search Movies", url="https://t.me/Movie_Request777"
                )
            ],
            [
                InlineKeyboardButton(
                    "💜 Contact Admin", url="https://t.me/Theadminor7_bot"
                )
            ],
        ]

        await safe_edit(query.message, text, InlineKeyboardMarkup(buttons))

        return

    # =========================
    # LANGUAGE FILTER MENU
    # =========================
    if data.startswith("language_"):

        search_id = data.split("_")[1]

        cache = context.bot_data.get(search_id)

        if not cache:

            await query.answer("⚠️ Search Expired", show_alert=True)

            return
        # owner check
        if cache["user_id"] != query.from_user.id:

            await query.answer("❌ This is not your request", show_alert=True)
            return

        results = cache["results"]

        languages = []

        for file in results:

            name = file["file_name"].lower()

            if "telugu" in name:
                languages.append("Telugu")

            if "tamil" in name:
                languages.append("Tamil")

            if "hindi" in name:
                languages.append("Hindi")

            if "malayalam" in name:
                languages.append("Malayalam")

            if "kannada" in name:
                languages.append("Kannada")

            if "english" in name:
                languages.append("English")

        languages = sorted(list(set(languages)))

        if not languages:

            await query.answer("No Languages Found", show_alert=True)

            return

        buttons = []

        for lang in languages:

            buttons.append(
                [
                    InlineKeyboardButton(
                        lang, callback_data=f"langfilter_{search_id}_{lang.lower()}"
                    )
                ]
            )

        buttons.append(
            [InlineKeyboardButton("⬅️ Back", callback_data=f"page_{search_id}_0")]
        )

        await safe_edit(
            query.message, "🌐 Select Language", InlineKeyboardMarkup(buttons)
        )

        return

    # =========================
    # LANGUAGE RESULT
    # =========================
    if data.startswith("langfilter_"):

        parts = data.split("_")

        search_id = parts[1]

        language = parts[2]

        cache = context.bot_data.get(search_id)

        if not cache:

            return
        # OWNER CHECK
        if cache["user_id"] != query.from_user.id:
            await query.answer("❌ This is not your request", show_alert=True)

            return

        results = cache["results"]

        filtered = []

        for file in results:

            if language in file["file_name"].lower():

                filtered.append(file)

        if not filtered:

            await query.answer("No Files Found", show_alert=True)

            return

        reply_markup = build_buttons(filtered, context.bot.username, search_id, 0)

        await safe_edit(query.message, f"🌐 {language.upper()} Files", reply_markup)

        return

    # =========================
    # QUALITY FILTER MENU
    # =========================
    if data.startswith("quality_"):

        search_id = data.split("_")[1]

        cache = context.bot_data.get(search_id)

        if not cache:

            await query.answer("⚠️ Search Expired", show_alert=True)

            return

        if cache["user_id"] != query.from_user.id:
            await query.answer("❌ This is not your request", show_alert=True)
            return

        results = cache["results"]

        qualities = []

        for file in results:

            name = file["file_name"].lower()

            if "480p" in name:
                qualities.append("480p")

            if "720p" in name:
                qualities.append("720p")

            if "1080p" in name:
                qualities.append("1080p")

            if "2160p" in name:
                qualities.append("2160p")

            if "x264" in name:
                qualities.append("x264")

            if "x265" in name:
                qualities.append("x265")

        qualities = sorted(list(set(qualities)))

        if not qualities:

            await query.answer("No Quality Found", show_alert=True)

            return

        buttons = []

        for q in qualities:

            buttons.append(
                [
                    InlineKeyboardButton(
                        q, callback_data=f"qualityfilter_{search_id}_{q.lower()}"
                    )
                ]
            )

        buttons.append(
            [InlineKeyboardButton("⬅️ Back", callback_data=f"page_{search_id}_0")]
        )

        await safe_edit(
            query.message, "🎥 Select Quality", InlineKeyboardMarkup(buttons)
        )

        return

    # =========================
    # QUALITY RESULT
    # =========================
    if data.startswith("qualityfilter_"):

        parts = data.split("_")

        search_id = parts[1]

        quality = parts[2]

        cache = context.bot_data.get(search_id)

        if not cache:

            return

        if cache["user_id"] != query.from_user.id:
            await query.answer("❌ This is not your request", show_alert=True)
            return

        results = cache["results"]

        filtered = []

        for file in results:

            if quality in file["file_name"].lower():

                filtered.append(file)

        if not filtered:

            await query.answer("No Files Found", show_alert=True)

            return

        reply_markup = build_buttons(filtered, context.bot.username, search_id, 0)

        await safe_edit(query.message, f"🎥 {quality.upper()} Files", reply_markup)

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

            await query.answer("⚠️ Search Expired", show_alert=True)

            return
        movie = cache.get("movie")

        if cache["user_id"] != query.from_user.id:

            await query.answer(
                "❌ This Search Belongs To Another User", show_alert=True
            )

            return

        results = cache["results"]

        reply_markup = build_buttons(results, context.bot.username, search_id, page)

        if movie:

            text = (
                f"{movie['caption']}\n\n"
                f"<b>🔎 Search Results</b>\n"
                f"<b>📄 Page:</b> {page+1}"
            )

        else:

            text = f"<b>🔎 Search Results</b>\n" f"<b>📄 Page:</b> {page+1}"

        await safe_edit(query.message, text, reply_markup)

        return

    # =========================
    # SEND ALL
    # =========================
    if data.startswith("sendall_"):
        parts = data.split("_", 2)
        if len(parts) != 3:
            await query.answer("⚠️ Invalid request", show_alert=True)
            return

        search_id = parts[1]

        page = int(parts[2])

        cache = context.bot_data.get(search_id)

        if not cache:
            await query.answer("⚠️ Search Expired", show_alert=True)
            return

        if cache["user_id"] != query.from_user.id:
            await query.answer("❌ This is not your request", show_alert=True)
            return

        results = cache["results"]

        start = page * RESULTS_PER_PAGE

        current_results = results[start : start + RESULTS_PER_PAGE]

        status_msg = None
        try:
            status_msg = await context.bot.send_message(
                chat_id=query.message.chat.id, text="📤 Sending Files In PM..."
            )
        except Exception as e:
            print(f"STATUS MSG ERROR: {e}")
        sent = 0
        failed = 0
        bot_not_started = False

        for file in current_results:
            try:
                sent_file = await context.bot.copy_message(
                    chat_id=query.from_user.id,
                    from_chat_id=file["chat_id"],
                    message_id=file["message_id"],
                )
                context.application.job_queue.run_once(
                    delete_pm_file,
                    when=180,
                    data={
                        "chat_id": query.from_user.id,
                        "message_id": sent_file.message_id,
                    },
                )

                sent += 1

                await asyncio.sleep(0.7)
            except Forbidden:
                bot_not_started = True
                break
            except Exception as e:

                print(f"SEND ERROR: {e}")

                failed += 1
        if bot_not_started:
            if status_msg:
                try:
                    await safe_edit(status_msg, "⚠️ Please start the bot in PM first.")
                except Exception as e:
                    print(f"EDIT ERROR: {e}")
            await query.answer("⚠️ First start the bot in PM", show_alert=True)
            return
        if sent == 0:
            if status_msg:
                try:
                    await safe_edit(status_msg, "⚠️ Failed to send files.")
                except Exception as e:
                    print(f"EDIT ERROR: {e}")
            await query.answer("⚠️ Unable to send files", show_alert=True)
            return
        try:
            warning_msg = await context.bot.send_message(
                chat_id=query.from_user.id,
                text=(
                    "🗑 Files will be deleted in 3 minutes.\n" "Forward them quickly."
                ),
            )
            context.application.job_queue.run_once(
                delete_pm_file,
                when=180,
                data={
                    "chat_id": query.from_user.id,
                    "message_id": warning_msg.message_id,
                },
            )
        except Exception as e:
            print(f"WARNING MSG ERROR: {e}")
        if status_msg:

            summary = f"✅ Sent {sent} file(s) in PM"

            if failed:
                summary += f" ({failed} failed)"
            await safe_edit(status_msg, summary)
            context.application.job_queue.run_once(
                delete_pm_file,
                when=10,
                data={
                    "chat_id": status_msg.chat_id,
                    "message_id": status_msg.message_id,
                },
            )

        return


# =========================
# HANDLER
# =========================
callback_handler = CallbackQueryHandler(button_click)

