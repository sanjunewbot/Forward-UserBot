import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, ChatAdminRequired, ChannelPrivate

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ====== HELPERS ======
def get_user_filters(user_id):
    return {k: True for k in ["Videos", "Photos", "Audios", "Text", "Stickers", "Animations", "Documents"]}

def get_readable_file_size(size):
    for unit in ["B","KB","MB","GB"]:
        if size < 1024:
            return f"{size:.2f}{unit}"
        size /= 1024
    return f"{size:.2f}TB"

USER_CAPTIONS = {}

# ====== YOUR FUNCTION (FIXED) ======
async def frwd(dest_chat_id, msg, user_id: int = None) -> str:
    try:
        if not msg or msg.empty:
            return "skipped"

        filters_map = get_user_filters(user_id)

        kwargs = {"chat_id": dest_chat_id, "disable_notification": True}

        def resolve_caption(media_obj):
            template = USER_CAPTIONS.get(user_id)
            if template is None:
                return msg.caption, msg.caption_entities
            file_name = getattr(media_obj, "file_name", None) or "file"
            file_size = get_readable_file_size(getattr(media_obj, "file_size", 0))
            caption_text = template.replace("{file_name}", file_name).replace("{file_size}", file_size)
            return caption_text, None

        if msg.text:
            if not filters_map["Text"]:
                return "skipped"
            await app.send_message(**kwargs, text=msg.text, entities=msg.entities)

        elif msg.photo:
            if not filters_map["Photos"]:
                return "skipped"
            cap, ent = resolve_caption(msg.photo)
            await app.send_photo(**kwargs, photo=msg.photo.file_id, caption=cap or "", caption_entities=ent)

        elif msg.video:
            if not filters_map["Videos"]:
                return "skipped"
            cap, ent = resolve_caption(msg.video)
            await app.send_video(**kwargs, video=msg.video.file_id, caption=cap or "", caption_entities=ent)

        elif msg.document:
            if not filters_map["Documents"]:
                return "skipped"
            cap, ent = resolve_caption(msg.document)
            await app.send_document(**kwargs, document=msg.document.file_id, caption=cap or "", caption_entities=ent)

        elif msg.audio:
            if not filters_map["Audios"]:
                return "skipped"
            cap, ent = resolve_caption(msg.audio)
            await app.send_audio(**kwargs, audio=msg.audio.file_id, caption=cap or "", caption_entities=ent)

        elif msg.voice:
            if not filters_map["Audios"]:
                return "skipped"
            cap, ent = resolve_caption(msg.voice)
            await app.send_voice(**kwargs, voice=msg.voice.file_id, caption=cap or "", caption_entities=ent)

        elif msg.video_note:
            if not filters_map["Videos"]:
                return "skipped"
            await app.send_video_note(**kwargs, video_note=msg.video_note.file_id)

        elif msg.sticker:
            if not filters_map["Stickers"]:
                return "skipped"
            await app.send_sticker(**kwargs, sticker=msg.sticker.file_id)

        elif msg.animation:
            if not filters_map["Animations"]:
                return "skipped"
            cap, ent = resolve_caption(msg.animation)
            await app.send_animation(**kwargs, animation=msg.animation.file_id, caption=cap or "", caption_entities=ent)

        else:
            return "skipped"

        return "ok"

    except (ChatAdminRequired, ChannelPrivate) as e:
        return f"fatal:{e}"
    except FloodWait as f:
        LOGGER.warning(f"FloodWait {f.value}s")
        await asyncio.sleep(f.value + 2)
        return await frwd(dest_chat_id, msg, user_id)  # FIXED
    except Exception as e:
        return f"error:{e}"

# ====== COMMAND ======
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("Bot Running ✅")

# ====== AUTO FORWARD EXAMPLE ======
# Replace SOURCE_CHAT_ID and DEST_CHAT_ID with your IDs
SOURCE_CHAT_ID = int(os.getenv("SOURCE_CHAT_ID", "0"))
DEST_CHAT_ID = int(os.getenv("DEST_CHAT_ID", "0"))

@app.on_message(filters.chat(SOURCE_CHAT_ID))
async def auto_forward(client, message):
    if DEST_CHAT_ID != 0:
        await frwd(DEST_CHAT_ID, message)

# ====== START ======
print("Bot Started...")
app.run()
