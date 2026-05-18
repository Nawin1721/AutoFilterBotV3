from telegram.ext import MessageHandler, filters

from database import files_col
from config import DB_CHANNEL_ID


async def save_media(update, context):

    # CHANNEL POSTS
    msg = update.channel_post

    if not msg:
        return

    print("CHANNEL POST RECEIVED 🔥")

    print("CHAT ID:", msg.chat.id)

    # CHECK DB CHANNEL
    if msg.chat.id != DB_CHANNEL_ID:

        print("WRONG CHANNEL ❌")
        return

    file_id = None
    file_name = None
    file_size = None

    # DOCUMENT
    if msg.document:

        file_id = msg.document.file_id
        file_name = msg.document.file_name
        file_size = msg.document.file_size

    # VIDEO
    elif msg.video:

        file_id = msg.video.file_id
        file_size = msg.video.file_size

        if msg.video.file_name:

            file_name = msg.video.file_name

        else:

            file_name = "video.mp4"

    # AUDIO
    elif msg.audio:

        file_id = msg.audio.file_id
        file_name = msg.audio.file_name
        file_size = msg.audio.file_size

    # PHOTO
    elif msg.photo:

        file_id = msg.photo[-1].file_id
        file_name = "photo.jpg"

    # SAVE TO DATABASE
    if file_id:

        # ORIGINAL CHANNEL CAPTION
        caption = msg.caption if msg.caption else file_name

        # BETTER SEARCH TEXT
        search_text = f"{file_name} {caption}".lower()

        search_text = (
            search_text
            .replace(".", " ")
            .replace("_", " ")
            .replace("-", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("(", " ")
            .replace(")", " ")
        )

        # DUPLICATE CHECK
        existing = files_col.find_one({
            "file_id": file_id
        })

        if existing:

            print("ALREADY INDEXED ⚠️")
            return

        data = {

            "file_name": file_name,

            "file_id": file_id,

            "file_size": file_size,

            "caption": caption,

            "search_text": search_text,

            # IMPORTANT FOR COPY MESSAGE
            "chat_id": msg.chat.id,

            "message_id": msg.message_id
        }

        files_col.insert_one(data)

        print(f"Indexed: {file_name} ✅")

    else:

        print("NO MEDIA FOUND ❌")


# HANDLER
auto_index = MessageHandler(
    filters.ChatType.CHANNEL,
    save_media
)
