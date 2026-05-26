# =========================
# search.py
# FULL OPTIMIZED VERSION
# =========================

from telegram.ext import MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import files_col, users_col

from plugins.force_sub import check_sub, force_sub_message
from plugins.imdb import get_movie

from rapidfuzz import process

import uuid
import time


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
# DELETE MESSAGE
# =========================
async def delete_message(context):

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
# CLEAR CACHE
# =========================
async def clear_cache(context):

    search_id = context.job.data

    try:

        del context.bot_data[search_id]

    except:

        pass


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

    user_id = msg.from_user.id


    # =========================
    # SAVE USER
    # =========================
    existing_user = await users_col.find_one({
        "user_id": user_id
    })

    if not existing_user:

        await users_col.insert_one({
            "user_id": user_id
        })


    # =========================
    # FORCE SUB
    # =========================
    joined = await check_sub(update, context)

    if not joined:

        await force_sub_message(msg)
        return


    # =========================
    # SEARCHING MESSAGE
    # =========================
    search_msg = await msg.reply_text(
        "🔍 Searching..."
    )


    # =========================
    # SEARCH PATTERN
    # =========================
    search_pattern = create_search_pattern(query)


    # =========================
    # DATABASE SEARCH
    # =========================
    results = await files_col.find({

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

    }).to_list(length=100)


    # =========================
    # NO RESULTS
    # =========================
    if not results:

        await search_msg.edit_text(
            "❌ No Results Found"
        )

        context.application.job_queue.run_once(
            delete_message,
            when=10,
            data={
                "chat_id": search_msg.chat_id,
                "message_id": search_msg.message_id
            }
        )

        # SUGGESTIONS
        all_files = await files_col.find(
            {},
            {"file_name": 1}
        ).to_list(length=300)

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
    # FOUND MESSAGE
    # =========================
    await search_msg.edit_text(
        f"✅ Found {len(results)} Results"
    )

    context.application.job_queue.run_once(
        delete_message,
        when=10,
        data={
            "chat_id": search_msg.chat_id,
            "message_id": search_msg.message_id
        }
    )


    # =========================
    # SEARCH ID
    # =========================
    search_id = uuid.uuid4().hex[:8]


    # =========================
    # SAVE CACHE
    # =========================
    context.bot_data[search_id] = {

        "results": results,

        "query": query,

        "user_id": msg.from_user.id,

        "time": time.time()

    }


    # =========================
    # AUTO CLEAR CACHE
    # =========================
    context.application.job_queue.run_once(
        clear_cache,
        when=600,
        data=search_id
    )


    # =========================
    # BUTTONS
    # =========================
    reply_markup = build_buttons(
        results,
        context.bot.username,
        search_id,
        page=0
    )


    # =========================
    # IMDb FIRST
    # =========================
    movie = await get_movie(query)


    # =========================
    # SEND IMDb + BUTTONS
    # =========================
    if movie:

        poster = movie.get("poster")

        caption = movie.get("caption")

        text = (

            f"{caption}\n\n"

            f"🔎 Search Results\n"

            f"📄 Page: 1"

        )

        if poster and poster != "N/A":

            sent_message = await msg.reply_photo(
                photo=poster,
                caption=text,
                reply_markup=reply_markup
            )

        else:

            sent_message = await msg.reply_text(
                text,
                reply_markup=reply_markup
            )

    else:

        sent_message = await msg.reply_text(
            "🔎 Search Results\n📄 Page: 1",
            reply_markup=reply_markup
        )


    # =========================
    # AUTO DELETE RESULTS
    # =========================
    context.application.job_queue.run_once(
        delete_message,
        when=180,
        data={
            "chat_id": sent_message.chat_id,
            "message_id": sent_message.message_id
        }
    )


    # =========================
    # AUTO DELETE USER SEARCH
    # =========================
    context.application.job_queue.run_once(
        delete_message,
        when=5,
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
