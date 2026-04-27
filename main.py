import os  
API_ID = int(os.environ["API_ID"])  
API_HASH = os.environ["API_HASH"]  
BOT_TOKEN = os.environ["BOT_TOKEN"]

async def frwd(dest_chat_id, msg, user_id: int = None) -> str:
try:
if not msg or msg.empty:
return "skipped"

filters = get_user_filters(user_id) if user_id else {k: True for k in ["Videos", "Photos", "Audios", "Text", "Stickers", "Animations"]}  

    kwargs = {"chat_id": dest_chat_id, "disable_notification": True}  

    def resolve_caption(media_obj) -> tuple:  
        template = USER_CAPTIONS.get(user_id) if user_id else None  
        if template is None:  
            return msg.caption, msg.caption_entities  
        file_name = getattr(media_obj, "file_name", None) or "file"  
        file_size = get_readable_file_size(getattr(media_obj, "file_size", 0))  
        caption_text = (  
            template  
            .replace("{file_name}", file_name)  
            .replace("{file_size}", file_size)  
        )  
        return caption_text, None  

    if msg.text:  
        if not filters["Text"]:  
            return "skipped"  
        await TgClient.bot.send_message(**kwargs, text=msg.text, entities=msg.entities)  

    elif msg.photo:  
        if not filters["Photos"]:  
            return "skipped"  
        cap, ent = (msg.caption, msg.caption_entities)  
        if user_id and user_id in USER_CAPTIONS:  
            template = USER_CAPTIONS[user_id]  
            cap = template.replace("{file_name}", "photo").replace("{file_size}", "")  
            ent = None  
        await TgClient.bot.send_photo(**kwargs, photo=msg.photo.file_id, caption=cap, caption_entities=ent)  

    elif msg.video:  
        if not filters["Videos"]:  
            return "skipped"  
        cap, ent = resolve_caption(msg.video)  
        await TgClient.bot.send_video(**kwargs, video=msg.video.file_id, caption=cap, caption_entities=ent)  

    elif msg.document:  
        if not filters["Videos"]:  
            return "skipped"  
        cap, ent = resolve_caption(msg.document)  
        await TgClient.bot.send_document(**kwargs, document=msg.document.file_id, caption=cap, caption_entities=ent)  

    elif msg.audio:  
        if not filters["Audios"]:  
            return "skipped"  
        cap, ent = resolve_caption(msg.audio)  
        await TgClient.bot.send_audio(**kwargs, audio=msg.audio.file_id, caption=cap, caption_entities=ent)  

    elif msg.voice:  
        if not filters["Audios"]:  
            return "skipped"  
        cap, ent = resolve_caption(msg.voice)  
        await TgClient.bot.send_voice(**kwargs, voice=msg.voice.file_id, caption=cap, caption_entities=ent)  

    elif msg.video_note:  
        if not filters["Videos"]:  
            return "skipped"  
        await TgClient.bot.send_video_note(**kwargs, video_note=msg.video_note.file_id)  

    elif msg.sticker:  
        if not filters["Stickers"]:  
            return "skipped"  
        await TgClient.bot.send_sticker(**kwargs, sticker=msg.sticker.file_id)  

    elif msg.animation:  
        if not filters["Animations"]:  
            return "skipped"  
        cap, ent = resolve_caption(msg.animation)  
        await TgClient.bot.send_animation(**kwargs, animation=msg.animation.file_id, caption=cap, caption_entities=ent)  

    elif msg.poll:  
        return "skipped"  

    else:  
        return "skipped"  

    return "ok"  

except (ChatAdminRequired, ChannelPrivate) as e:  
    return f"fatal:{e}"  
except FloodWait as f:  
    LOGGER.warning(f"FloodWait during send, sleeping {f.value}s")  
    await sleep(f.value + 2)  
    return await send_single(dest_chat_id, msg, user_id)  
except Exception as e:  
    return f"error:{e}"
