from telegram.ext import MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database import files_col, users_col
from config import GROUP_ID

from plugins.force_sub import check_sub, force_sub_message
from plugins.imdb import get_movie

from rapidfuzz import process

RESULTS_PER_PAGE = 10


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
# SEARCH FILES
# =========================
async def search_files(update, context):

    msg = update.message

    if not msg:
        return

    # SAVE USER
    user_id = msg.from_user.id

    existing_user = users_col.find_one({
        "user_id": user_id
    })

    if not existing_user:

        users_col.insert_one({
            "user_id": user_id
        })

    # FORCE SUB CHECK
    joined = await check_sub(update, context)

    if not joined:

        await force_sub_message(msg)
        return

    # ONLY GROUP
    if msg.chat.id != GROUP_ID:
        return

    query = msg.text

    if not query:
        return

    print(f"Searching: {query}")

    # SEARCH MESSAGE
    search_msg = await context.bot.send_message(
        chat_id=msg.chat.id,
        text="🔍 Searching..."
    )

    # AUTO DELETE SEARCH MESSAGE
    context.application.job_queue.run_once(
        delete_message,
        when=300,
        data={
            "chat_id": search_msg.chat_id,
            "message_id": search_msg.message_id
        }
    )

    # SMART SEARCH
    search_pattern = create_search_pattern(query)

    # SEARCH DATABASE
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

    # NO RESULTS
    if not results:

        await search_msg.edit_text(
            "❌ No Results Found"
        )

        # SPELL CHECK
        all_files = files_col.find()

        movie_names = []

        for file in all_files:

            movie_names.append(file["file_name"])

        match = process.extractOne(
            query,
            movie_names
        )

        if match:

            suggestion = match[0]

            suggestion_msg = await context.bot.send_message(
                chat_id=msg.chat.id,
                text=f"❓ Did You Mean:\n\n{suggestion}"
            )

            # AUTO DELETE SUGGESTION
            context.application.job_queue.run_once(
                delete_message,
                when=300,
                data={
                    "chat_id": suggestion_msg.chat_id,
                    "message_id": suggestion_msg.message_id
                }
            )

        # DELETE USER MESSAGE
        context.application.job_queue.run_once(
            delete_message,
            when=300,
            data={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id
            }
        )

        return

    # RESULT COUNT
    await search_msg.edit_text(
        f"✅ Found {len(results)} Results"
    )

    # SAVE RESULTS
    context.user_data["results"] = results
    context.user_data["query"] = query
    context.user_data["original_query"] = query
    context.user_data["search_user"] = update.effective_user.id

    # IMDb INFO
    movie = await get_movie(query)

    if movie:

        try:

            imdb_msg = await context.bot.send_photo(
                chat_id=msg.chat.id,
                photo=movie["poster"],
                caption=movie["caption"]
            )

            # AUTO DELETE IMDb MESSAGE
            context.application.job_queue.run_once(
                delete_message,
                when=300,
                data={
                    "chat_id": imdb_msg.chat_id,
                    "message_id": imdb_msg.message_id
                }
            )

        except:

            pass

    # SEND PAGE 1
    await send_page(
        msg,
        context,
        page=0
    )


# =========================
# SEND PAGE
# =========================
async def send_page(msg, context, page):

    results = context.user_data.get("results", [])

    if not results:
        return

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE

    current_results = results[start:end]

    buttons = []

    # TOP FILTER BUTTONS
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

        button = [
            InlineKeyboardButton(
                text=file["file_name"][:40],
                url=f"https://t.me/{context.bot.username}?start={file['_id']}"
            )
        ]

        buttons.append(button)

    # PAGINATION BUTTONS
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

    reply_markup = InlineKeyboardMarkup(buttons)

    sent_message = await context.bot.send_message(
        chat_id=msg.chat.id,
        text=f"🔍 Search Results\n📄 Page: {page+1}",
        reply_markup=reply_markup
    )

    # AUTO DELETE RESULT MESSAGE
    context.application.job_queue.run_once(
        delete_message,
        when=300,
        data={
            "chat_id": sent_message.chat_id,
            "message_id": sent_message.message_id
        }
    )

    # AUTO DELETE USER MESSAGE
    context.application.job_queue.run_once(
        delete_message,
        when=300,
        data={
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }
    )


# =========================
# DELETE MESSAGE
# =========================
async def delete_message(context):

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
# HANDLER
# =========================
search_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    search_files
)
