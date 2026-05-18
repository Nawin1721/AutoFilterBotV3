from telegram.ext import InlineQueryHandler
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent
)

from uuid import uuid4

from database import files_col


async def inline_search(update, context):

    query = update.inline_query.query

    if not query:
        return

    # SEARCH DATABASE
    results_db = list(files_col.find({
        "file_name": {
            "$regex": query,
            "$options": "i"
        }
    }).limit(20))

    results = []

    for file in results_db:

        result = InlineQueryResultArticle(
            id=str(uuid4()),
            title=file["file_name"],
            description="Click To Get File",
            input_message_content=InputTextMessageContent(
                message_text=file.get("caption", file["file_name"])
            )
        )

        results.append(result)

    await update.inline_query.answer(
        results,
        cache_time=1
    )


inline_handler = InlineQueryHandler(
    inline_search
)