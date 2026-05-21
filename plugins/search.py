from telegram.ext import MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import files_col, users_col
from config import GROUP_ID

from plugins.force_sub import check_sub, force_sub_message
from plugins.imdb import get_movie

from rapidfuzz import process

RESULTS_PER_PAGE = 10


# =========================
# FORMAT FILE SIZE
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
# SMART SEARCH PATTERN
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
# DELETE MESSAGE
# =========================
async def delete_message(context):

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
# DELETE USER MESSAGE
# =========================
async def delete_user_message(context):

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
# BUILD BUTTONS
# =========================
def build_buttons(results, bot_username, page=0):

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # TOP BUTTONS
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

        buttons.append([

            InlineKeyboardButton(
                text=f"[{size}] {file['file_name'][:45]}",
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
# SEARCH FILES
# =========================
async def search_files(update, context):

    msg = update.message

    if not msg:
        return

    query = msg.text.strip()

    if not query:
        return

    print(f"Searching: {query}")

    # SAVE USER
    user_id = msg.from_user.id

    existing_user = users_col.find_one({
        "user_id": user_id
    })

    if not existing_user:

        users_col.insert_one({
            "user_id": user_id
        })

    # FORCE SUB
    joined = await check_sub(update, context)

    if not joined:

        await force_sub_message(msg)
        return

    # SEARCHING MESSAGE
    search_msg = await msg.reply_text(
        "🔍 Searching..."
    )

    # SEARCH PATTERN
    search_pattern = create_search_pattern(query)

    # DATABASE SEARCH
    results = list(files_col.find({

        "$or": [

            {
                "search_text": {
                    "$regex": search_pattern,
                    "$options": "i"
                }
            },

            {
                "caption": {
                    "$regex": search_pattern,
                    "$options": "i"
                }
            }

        ]

    }))

    # =========================
    # NO RESULTS
    # =========================
    if not results:

        await search_msg.edit_text(
            "❌ No Results Found"
        )

        # AUTO DELETE NO RESULT
        context.application.job_queue.run_once(
            delete_message,
            when=20,
            data={
                "chat_id": search_msg.chat_id,
                "message_id": search_msg.message_id
            }
        )

        all_files = list(files_col.find())

        movie_names = [
            x["file_name"]
            for x in all_files
        ]

        match = process.extractOne(
            query,
            movie_names
        )

        if match:

            suggestion = match[0]

            suggest_msg = await msg.reply_text(
                f"❓ Did You Mean:\n\n{suggestion}"
            )

            # AUTO DELETE SUGGESTION
            context.application.job_queue.run_once(
                delete_message,
                when=20,
                data={
                    "chat_id": suggest_msg.chat_id,
                    "message_id": suggest_msg.message_id
                }
            )

        return

    # =========================
    # IMDb FIRST
    # =========================

    try:

        movie = await get_movie(query)

        if movie:

            poster = movie.get("poster")

            caption = movie.get("caption")

            # SEND PHOTO
            if poster:

                imdb_msg = await context.bot.send_photo(
                    chat_id=msg.chat.id,
                    photo=poster,
                    caption=caption[:1024]
                )

            # SEND TEXT
            else:

                imdb_msg = await context.bot.send_message(
                    chat_id=msg.chat.id,
                    text=caption[:4096]
                )

            # AUTO DELETE IMDb
            context.application.job_queue.run_once(
                delete_message,
                when=305,
                data={
                    "chat_id": imdb_msg.chat_id,
                    "message_id": imdb_msg.message_id
                }
            )

    except Exception as e:

        print(f"IMDb Error: {e}")

    # =========================
    # FOUND RESULTS
    # =========================

    await search_msg.edit_text(
        f"✅ Found {len(results)} Results"
    )

    # AUTO DELETE FOUND MESSAGE
    context.application.job_queue.run_once(
        delete_message,
        when=20,
        data={
            "chat_id": search_msg.chat_id,
            "message_id": search_msg.message_id
        }
    )

    # =========================
    # BUTTONS AFTER IMDb
    # =========================

    reply_markup = build_buttons(
        results,
        context.bot.username,
        page=0
    )

    # RESULT MESSAGE
    sent_message = await msg.reply_text(
        "🔍 Search Results\n📄 Page: 1",
        reply_markup=reply_markup
    )

    # SAVE RESULTS
    context.bot_data[
        str(sent_message.message_id)
    ] = results

    # SAVE ORIGINAL QUERY
    context.bot_data[
        f"query_{sent_message.message_id}"
    ] = query

    # SAVE SEARCH USER
    context.user_data[
        "search_user"
    ] = msg.from_user.id

    # AUTO DELETE RESULT
    context.application.job_queue.run_once(
        delete_message,
        when=305,
        data={
            "chat_id": sent_message.chat_id,
            "message_id": sent_message.message_id
        }
    )

    # AUTO DELETE USER QUERY
    context.application.job_queue.run_once(
        delete_user_message,
        when=305,
        data={
            "chat_id": msg.chat.id,
            "message_id": msg.message_id
        }
    )


# =========================
# HANDLER
# =========================
search_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    search_files
)
