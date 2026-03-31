# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import os
import sys 
import math
import re
import time
import asyncio 
import logging
from .utils import STS
from database import db 
from .test import CLIENT , start_clone_bot
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

CLIENT = CLIENT()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = Translation.TEXT

def get_size(size_in_bytes):
    """Convert bytes to human readable format."""
    if not size_in_bytes:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    
    return f"{size_in_bytes:.2f} PB"

def custom_caption(msg, old_caption_from_db, caption_configs):
    """
    Applies various caption modifications based on user settings.
    
    Args:
        msg (Message): The Pyrogram Message object.
        old_caption_from_db (str): The legacy single custom caption from DB (if any).
        caption_configs (dict): A dictionary containing all caption-related settings.
    
    Returns:
        str: The modified caption.
    """
    try:
        # Get the original caption
        original_caption = ""
        if hasattr(msg, 'caption') and msg.caption:
            if hasattr(msg.caption, 'html'):
                original_caption = msg.caption.html
            elif isinstance(msg.caption, str):
                original_caption = msg.caption
        
        # Get file details if media exists
        file_name = ""
        file_size = 0
        
        if hasattr(msg, 'document') and msg.document:
            file_name = getattr(msg.document, 'file_name', 'file')
            file_size = getattr(msg.document, 'file_size', 0)
        elif hasattr(msg, 'video') and msg.video:
            file_name = getattr(msg.video, 'file_name', 'video')
            file_size = getattr(msg.video, 'file_size', 0)
        elif hasattr(msg, 'audio') and msg.audio:
            file_name = getattr(msg.audio, 'file_name', 'audio')
            file_size = getattr(msg.audio, 'file_size', 0)
        elif hasattr(msg, 'photo') and msg.photo:
            file_name = 'photo'
            file_size = getattr(msg.photo, 'file_size', 0)
        
        # If no caption settings enabled, use old system
        if not caption_configs or not caption_configs.get('caption_enabled', False):
            if old_caption_from_db:
                try:
                    return old_caption_from_db.format(
                        filename=file_name or 'file',
                        size=get_size(file_size),
                        caption=original_caption
                    )
                except (KeyError, ValueError):
                    return original_caption
            return original_caption
        
        # Start with original caption
        final_caption = original_caption
        
        # 1. HEADER - Add at the very beginning
        header = caption_configs.get('caption_header')
        if header:
            final_caption = f"{header}\n{final_caption}" if final_caption else header
        
        # 2. PREFIX - Add to the beginning of each line
        prefix = caption_configs.get('caption_prefix')
        if prefix:
            lines = final_caption.split('\n')
            final_caption = '\n'.join([f"{prefix}{line}" for line in lines])
        
        # 3. SUFFIX - Add to the end of each line
        suffix = caption_configs.get('caption_suffix')
        if suffix:
            lines = final_caption.split('\n')
            final_caption = '\n'.join([f"{line}{suffix}" for line in lines])
        
        # 4. FOOTER - Add at the very end
        footer = caption_configs.get('caption_footer')
        if footer:
            final_caption = f"{final_caption}\n{footer}" if final_caption else footer
        
        # 5. DELETE BEFORE - Delete everything before a word (inclusive)
        delete_before_word = caption_configs.get('caption_delete_before_word')
        if delete_before_word and delete_before_word in final_caption:
            idx = final_caption.find(delete_before_word)
            final_caption = final_caption[idx:]
        
        # 6. DELETE AFTER - Delete everything after a word (inclusive)
        delete_after_word = caption_configs.get('caption_delete_after_word')
        if delete_after_word and delete_after_word in final_caption:
            idx = final_caption.find(delete_after_word)
            final_caption = final_caption[:idx + len(delete_after_word)]
        
        # 7. DELETE WORDS - Remove specific words from caption
        delete_words_list = caption_configs.get('caption_delete_words_list')
        if delete_words_list:
            words_to_delete = delete_words_list.split()
            for word in words_to_delete:
                final_caption = final_caption.replace(word, '')
        
        # 8. REPLACE WORDS - Replace words with other words
        replace_words_map = caption_configs.get('caption_replace_words_map')
        if replace_words_map:
            pairs = replace_words_map.split('\n')
            for pair in pairs:
                if '=' in pair:
                    old_word, new_word = pair.split('=', 1)
                    final_caption = final_caption.replace(old_word.strip(), new_word.strip())
        
        # 9. LINK REMOVE - Remove all links (http/https/t.me)
        link_remove = caption_configs.get('caption_link_remove', False)
        if link_remove:
            # Remove http/https links
            final_caption = re.sub(r'https?://\S+|www\.\S+', '', final_caption)
            # Remove t.me links
            final_caption = re.sub(r't\.me/\S+', '', final_caption)
        
        # 10. LINK REPLACE - Replace one link with another
        link_replace_pair = caption_configs.get('caption_link_replace_pair')
        if link_replace_pair and '=' in link_replace_pair:
            old_link, new_link = link_replace_pair.split('=', 1)
            final_caption = final_caption.replace(old_link.strip(), new_link.strip())
        
        # 11. USERNAME REMOVE - Remove all @usernames
        username_remove = caption_configs.get('caption_username_remove', False)
        if username_remove:
            final_caption = re.sub(r'@\w+', '', final_caption)
        
        # 12. USERNAME REPLACE - Replace @username with another
        username_replace_pair = caption_configs.get('caption_username_replace_pair')
        if username_replace_pair and '=' in username_replace_pair:
            old_username, new_username = username_replace_pair.split('=', 1)
            final_caption = final_caption.replace(old_username.strip(), new_username.strip())
        
        # 13. CAPTION LENGTH - Limit caption length
        caption_length_limit = caption_configs.get('caption_length_limit')
        if caption_length_limit and isinstance(caption_length_limit, int):
            if len(final_caption) > caption_length_limit:
                final_caption = final_caption[:caption_length_limit] + "..."
        
        # Try to format with file details if placeholders exist
        try:
            final_caption = final_caption.format(
                filename=file_name or 'file',
                size=get_size(file_size),
                caption=original_caption
            )
        except (KeyError, ValueError):
            pass
        
        return final_caption if final_caption else original_caption
    
    except Exception as e:
        logger.error(f"Error in custom_caption: {e}")
        return original_caption if isinstance(original_caption, str) else ""


@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user)) == "True":
        return await message.answer("Please Wait Until Previous Task Complete", show_alert=True)
    
    sts = STS(frwd_id)
    if not sts.verify():
        await message.answer("Your Are Clicking On My Old Button", show_alert=True)
        return await message.message.delete()
    
    i = sts.get(full=True)
    if i.TO in temp.IS_FRWD_CHAT:
        return await message.answer("In Target Chat A Task Is Progressing. Please Wait Until Task Complete", show_alert=True)
    
    m = await msg_edit(message.message, "Verifying Your Data's, Please Wait.")
    _bot, caption, forward_tag, data, protect, button, pinning, caption_configs = await sts.get_data(user)
    
    if not _bot:
        return await msg_edit(m, "You Didn't Added Any Bot. Please Add A Bot Using /settings !", wait=True)
    
    try:
        client = await start_clone_bot(CLIENT.client(_bot))
    except Exception as e:
        return await m.edit(e)
    
    await msg_edit(m, "Processing...")
    try:
        await client.get_messages(sts.get("FROM"), sts.get("limit"))
    except:
        await msg_edit(m, f"Source Chat May Be A Private Channel / Group. Use Userbot (User Must Be Member Over There) Or If Make Your [Bot](t.me/{_bot['username']}) An Admin Over There", retry_btn(frwd_id), True)
        return await stop(client, user)
    
    try:
        k = await client.send_message(i.TO, "Testing")
        await k.delete()
    except:
        await msg_edit(m, f"Please Make Your [UserBot / Bot](t.me/{_bot['username']}) Admin In Target Channel With Full Permissions", retry_btn(frwd_id), True)
        return await stop(client, user)
    
    temp.forwardings += 1
    await db.add_frwd(user)
    await send(client, user, "🩷 Forwarding Started")
    sts.add(time=True)
    sleep = 1 if _bot['is_bot'] else 10
    await msg_edit(m, "Processing...")
    temp.IS_FRWD_CHAT.append(i.TO)
    temp.lock[user] = locked = True
    
    if locked:
        try:
            MSG = []
            pling = 0
            await edit(m, 'Progressing', 10, sts)
            print(f"Starting Forwarding Process... From :{sts.get('FROM')} To: {sts.get('TO')} Total: {sts.get('limit')} Stats : {sts.get('skip')}")
            
            async for message in client.iter_messages(
                client,
                chat_id=sts.get('FROM'),
                limit=int(sts.get('limit')),
                offset=int(sts.get('skip')) if sts.get('skip') else 0
            ):
                if await is_cancelled(client, user, m, sts):
                    return
                
                if pling % 20 == 0:
                    await edit(m, 'Progressing', 10, sts)
                
                pling += 1
                sts.add('fetched')
                
                if message == "DUPLICATE":
                    sts.add('duplicate')
                    continue
                elif message == "FILTERED":
                    sts.add('filtered')
                    continue
                
                # Apply custom caption if enabled
                if caption_configs.get('caption_enabled', False):
                    original_caption = message.caption.html if message.caption else ""
                    modified_caption = custom_caption(message, caption, caption_configs)
                    if modified_caption and modified_caption != original_caption:
                        # Edit message caption (only if caption is different)
                        # This would be done when forwarding the message
                        pass
                
                # Forward message with optional caption modification
                try:
                    # Copy message to destination
                    msg = await message.copy(
                        chat_id=i.TO,
                        caption=custom_caption(message, caption, caption_configs) if caption_configs.get('caption_enabled') else None
                    )
                    
                    # Handle pinning if enabled
                    if pinning and message.pinned:
                        try:
                            await client.pin_chat_message(i.TO, msg.id)
                        except:
                            pass  # Fail silently if can't pin
                    
                    sts.add('total')
                    MSG.append(msg.id)
                    await asyncio.sleep(sleep)
                
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception as e:
                    logger.error(f"Error forwarding message: {e}")
                    sts.add('deleted')
            
            await finish(m, sts, user, MSG)
        
        except Exception as e:
            logger.error(f"Error in forwarding task: {e}")
            await msg_edit(m, f"❌ Error: {str(e)}")
        
        finally:
            temp.lock[user] = False
            if i.TO in temp.IS_FRWD_CHAT:
                temp.IS_FRWD_CHAT.remove(i.TO)
            await stop(client, user)


async def msg_edit(m, text, reply_markup=None, wait=False):
    """Edit message safely."""
    try:
        return await m.edit(text, reply_markup=reply_markup)
    except MessageNotModified:
        return m
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return m


async def edit(m, status, time_gap, sts):
    """Edit status message."""
    try:
        text = f"""
<b>⏱️ Forwarding Status</b>

<b>Status:</b> {status}
<b>Total:</b> {sts.get('limit')}
<b>Fetched:</b> {sts.get('fetched')}
<b>Forwarded:</b> {sts.get('total')}
<b>Filtered:</b> {sts.get('filtered')}
<b>Duplicates:</b> {sts.get('duplicate')}
<b>Deleted:</b> {sts.get('deleted')}
"""
        await m.edit(text)
    except:
        pass


async def finish(m, sts, user, msgs):
    """Show completion message."""
    try:
        text = f"""
<b>✅ Forwarding Completed</b>

<b>Total:</b> {sts.get('limit')}
<b>Forwarded:</b> {sts.get('total')}
<b>Filtered:</b> {sts.get('filtered')}
<b>Duplicates:</b> {sts.get('duplicate')}
<b>Deleted:</b> {sts.get('deleted')}
"""
        await m.edit(text)
    except:
        pass


async def is_cancelled(client, user, m, sts):
    """Check if forwarding was cancelled."""
    if temp.CANCEL.get(user):
        await m.edit("❌ Forwarding Cancelled")
        return True
    return False


async def stop(client, user):
    """Stop the client."""
    try:
        await client.stop()
    except:
        pass


async def send(client, user, text):
    """Send message to user."""
    try:
        await client.send_message(user, text)
    except:
        pass


def retry_btn(frwd_id):
    """Return retry button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('🔄 Retry', callback_data=f'start_public_{frwd_id}')]
    ])


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
