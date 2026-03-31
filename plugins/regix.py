# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import os
import sys 
import math
import re # Added re import for caption processing
import time
import asyncio 
import logging
from .utils import STS
from database import db 
from .test import CLIENT , start_clone_bot
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
#from pyropatch.utils import unpack_new_file_id
from pyrogram.errors import FloodWait, MessageNotModified, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

CLIENT = CLIENT()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = Translation.TEXT





@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user))=="True":
      return await message.answer("Please Wait Until Previous Task Complete", show_alert=True)
    sts = STS(frwd_id)
    if not sts.verify():
      await message.answer("Your Are Clicking On My Old Button", show_alert=True)
      return await message.message.delete()
    i = sts.get(full=True)
    if i.TO in temp.IS_FRWD_CHAT:
      return await message.answer("In Target Chat A Task Is Progressing. Please Wait Until Task Complete", show_alert=True)
    m = await msg_edit(message.message, "Verifying Your Data's, Please Wait.")
    _bot, caption, forward_tag, data, protect, button = await sts.get_data(user)
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
       await msg_edit(m, f"Source Chat May Be A Private Channel / Group. Use Userbot (User Must Be Member Over There) Or  If Make Your [Bot](t.me/{_bot['username']}) An Admin Over There", retry_btn(frwd_id), True)
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
          pling=0
          await edit(m, 'Progressing', 10, sts)
          print(f"Starting Forwarding Process... From :{sts.get('FROM')} To: {sts.get('TO')} Totel: {sts.get('limit')} Stats : {sts.get('skip')})")
          async for message in client.iter_messages(
            client,
            chat_id=sts.get('FROM'), 
            limit=int(sts.get('limit')), 
            offset=int(sts.get('skip')) if sts.get('skip') else 0
            ):
                if await is_cancelled(client, user, m, sts):
                   return
                if pling %20 == 0: 
                   await edit(m, 'Progressing', 10, sts)
                pling += 1
                sts.add('fetched')
                if message == "DUPLICATE":
                   sts.add('duplicate')
                   continue 
                elif message == "FILTERED":
                   sts.add('filtered')
                   continue 
                if message.empty or message.service:
                   sts.add('deleted')
                   continue
                if forward_tag:
                   MSG.append(message.id)
                   notcompleted = len(MSG)
                   completed = sts.get('total') - sts.get('fetched')
                   if ( notcompleted >= 100 
                        or completed <= 100): 
                      await forward(client, MSG, m, sts, protect)
                      sts.add('total_files', notcompleted)
                      await asyncio.sleep(10)
                      MSG = []
                else:
                   new_caption = custom_caption(message, caption, sts.get_all_caption_configs()) # Pass all caption configs
                   details = {"msg_id": message.id, "media": media(message), "caption": new_caption, 'button': button, "protect": protect, "is_pinned": message.pinned}
                   await copy(client, details, m, sts)
                   sts.add('total_files')
                   await asyncio.sleep(sleep) 
        except Exception as e:
            await msg_edit(m, f'<b>Error :</b>\n<code>{e}</code>', wait=True)
            temp.IS_FRWD_CHAT.remove(sts.TO)
            return await stop(client, user)
        temp.IS_FRWD_CHAT.remove(sts.TO)
        await send(client, user, "🎉 Forwarding Completed")
        await edit(m, 'Completed', "completed", sts) 
        await stop(client, user)
            
async def copy(bot, msg_details, m, sts):
   try:                                  
     sent_msg = None # Initialize sent_msg
     if msg_details.get("media") and msg_details.get("caption"):
        sent_msg = await bot.send_cached_media(
              chat_id=sts.get('TO'),
              file_id=msg_details.get("media"),
              caption=msg_details.get("caption"),
              reply_markup=msg_details.get('button'),
              protect_content=msg_details.get("protect"))
     else:
        sent_msg = await bot.copy_message(
              chat_id=sts.get('TO'),
              from_chat_id=sts.get('FROM'),    
              caption=msg_details.get("caption"),
              message_id=msg_details.get("msg_id"),
              reply_markup=msg_details.get('button'),
              protect_content=msg_details.get("protect"))
     
     # Pinning logic
     if sts.get('pinning') and msg_details.get("is_pinned"): # Check if pinning is enabled and source message was pinned
         try:
             await bot.pin_chat_message(chat_id=sts.get('TO'), message_id=sent_msg.id)
         except Exception as pin_e:
             logger.warning(f"Failed to pin message {sent_msg.id} in {sts.get('TO')}: {pin_e}")
   except FloodWait as e: # Corrected variable name from msg to msg_details
     await edit(m, 'Progressing', e.value, sts)
     await asyncio.sleep(e.value + 1) # Add a small buffer
     await edit(m, 'Progressing', 10, sts)
     await copy(bot, msg, m, sts)
   except Exception as e:
     print(e)
     sts.add('deleted')
        
async def forward(bot, msg, m, sts, protect):
   try:                             
     await bot.forward_messages(
           chat_id=sts.get('TO'),
           from_chat_id=sts.get('FROM'), 
           protect_content=protect,
           message_ids=msg)
   except FloodWait as e:
     await edit(m, 'Progressing', e.value, sts)
     await asyncio.sleep(e.value)
     await edit(m, 'Progressing', 10, sts)
     await forward(bot, msg, m, sts, protect)

PROGRESS = """
📈 Percetage : {0} %

♻️ Fetched : {1}

🔥 Forwarded : {2}

🫠 Remaining : {3}

📊 Status : {4}

⏳️ ETA : {5}
"""

async def msg_edit(msg, text, button=None, wait=None):
    try:
        return await msg.edit(text, reply_markup=button)
    except MessageNotModified:
        pass 
    except FloodWait as e:
        if wait:
           await asyncio.sleep(e.value)
           return await msg_edit(msg, text, button, wait)
        
async def edit(msg, title, status, sts):
   i = sts.get(full=True)
   status = 'Forwarding' if status == 10 else f"Sleeping {status} s" if str(status).isnumeric() else status
   percentage = "{:.0f}".format(float(i.fetched)*100/float(i.total))
   
   now = time.time()
   diff = int(now - i.start)
   speed = sts.divide(i.fetched, diff)
   elapsed_time = round(diff) * 1000
   time_to_completion = round(sts.divide(i.total - i.fetched, int(speed))) * 1000
   estimated_total_time = elapsed_time + time_to_completion  
   progress = "▰{0}{1}".format(
       ''.join(["▰" for i in range(math.floor(int(percentage) / 10))]),
       ''.join(["▱" for i in range(10 - math.floor(int(percentage) / 10))]))
   button =  [[InlineKeyboardButton(title, f'fwrdstatus#{status}#{estimated_total_time}#{percentage}#{i.id}')]]
   estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
   estimated_total_time = estimated_total_time if estimated_total_time != '' else '0 s'

   text = TEXT.format(i.fetched, i.total_files, i.duplicate, i.deleted, i.skip, status, percentage, estimated_total_time, progress)
   if status in ["cancelled", "completed"]:
      button.append(
         [InlineKeyboardButton('📢 Updates', url='https://t.me/Madflix_Bots'),
         InlineKeyboardButton('💬 Support', url='https://t.me/MadflixBots_Support')]
         )
   else:
      button.append([InlineKeyboardButton('✖️ Cancel ✖️', 'terminate_frwd')])
   await msg_edit(msg, text, InlineKeyboardMarkup(button))
   
async def is_cancelled(client, user, msg, sts):
   if temp.CANCEL.get(user)==True:
      temp.IS_FRWD_CHAT.remove(sts.TO)
      await edit(msg, "Cancelled", "completed", sts)
      await send(client, user, "❌ Forwarding Process Cancelled")
      await stop(client, user)
      return True 
   return False 

async def stop(client, user):
   try:
     await client.stop()
   except:
     pass 
   await db.rmve_frwd(user)
   temp.forwardings -= 1
   temp.lock[user] = False 
    
async def send(bot, user, text):
   try:
      await bot.send_message(user, text=text)
   except:
      pass 
     
def custom_caption(msg, old_caption_from_db, caption_configs):
  """
  Applies various caption modifications based on user settings.
  
  Args:
    msg (Message): The Pyrogram Message object.
    old_caption_from_db (str): The legacy single custom caption from DB (if any).
    caption_configs (dict): A dictionary containing all new caption-related settings.
  
  Returns:
    str: The modified caption.
  """
  if msg.media:
    if (msg.video or msg.document or msg.audio or msg.photo):
      media = getattr(msg, msg.media.value, None)
      if media:
        file_name = getattr(media, 'file_name', '')
        file_size = getattr(media, 'file_size', '')
        original_caption = getattr(msg, 'caption', '')
        if original_caption:
          original_caption = original_caption.html # Original caption in HTML format
        
        # Start with the original caption or an empty string if none
        final_caption = original_caption if original_caption else ""

        # If the new caption system is not enabled, fall back to the old system (if old_caption_from_db exists)
        if not caption_configs.get('caption_enabled', False):
            if old_caption_from_db:
                return old_caption_from_db.format(filename=file_name, size=get_size(file_size), caption=original_caption)
            return original_caption

        # --- Apply new caption modifications in order ---

        # 1. HEADER
        header = caption_configs.get('caption_header')
        if header:
            final_caption = header + "\n" + final_caption if final_caption else header # Add header at the very beginning

        # 2. PREFIX
        prefix = caption_configs.get('caption_prefix')
        if prefix:
            lines = final_caption.split('\n')
            final_caption = '\n'.join([f"{prefix}{line}" for line in lines]) # Add prefix to each line

        # 3. SUFFIX
        suffix = caption_configs.get('caption_suffix')
        if suffix:
            final_caption = final_caption + "\n" + suffix if final_caption else suffix

        # 4. FOOTER
        footer = caption_configs.get('caption_footer')
        if footer: # Add footer at the very end
            final_caption = final_caption + "\n" + footer if final_caption else footer

        # 5. DELETE BEFORE
        delete_before_word = caption_configs.get('caption_delete_before_word')
        if delete_before_word and delete_before_word in final_caption: # Delete everything before the word (inclusive)
            final_caption = final_caption[final_caption.find(delete_before_word):] 

        # 6. DELETE AFTER
        delete_after_word = caption_configs.get('caption_delete_after_word')
        if delete_after_word and delete_after_word in final_caption: # Delete everything after the word (inclusive)
            final_caption = final_caption[:final_caption.find(delete_after_word) + len(delete_after_word)] 

        # 7. DELETE WORDS
        delete_words_list = caption_configs.get('caption_delete_words_list')
        if delete_words_list:
            words_to_delete = delete_words_list.split()
            for word in words_to_delete:
                final_caption = final_caption.replace(word, '')
        
        # 8. REPLACE WORDS
        replace_words_map = caption_configs.get('caption_replace_words_map')
        if replace_words_map:
            pairs = replace_words_map.split('\n')
            for pair in pairs:
                if '=' in pair:
                    old, new = pair.split('=', 1)
                    final_caption = final_caption.replace(old.strip(), new.strip()) # Replace all occurrences

        # 9. LINK REMOVE
        link_remove = caption_configs.get('caption_link_remove', False)
        if link_remove:
            # Regex to find URLs (http/https)
            final_caption = re.sub(r'https?://\S+|www\.\S+', '', final_caption)
            # Regex to find Telegram t.me links (and also remove any remaining http/https for robustness)
            final_caption = re.sub(r't\.me/\S+', '', final_caption)

        # 10. LINK REPLACE
        link_replace_pair = caption_configs.get('caption_link_replace_pair')
        if link_replace_pair and '=' in link_replace_pair:
            old_link, new_link = link_replace_pair.split('=', 1)
            final_caption = final_caption.replace(old_link.strip(), new_link.strip())
        
        # 11. REMOVE USERNAME
        username_remove = caption_configs.get('caption_username_remove', False)
        if username_remove:
            final_caption = re.sub(r'@\w+', '', final_caption) # Remove all @usernames

        # 12. USERNAME REPLACE
        username_replace_pair = caption_configs.get('caption_username_replace_pair')
        if username_replace_pair and '=' in username_replace_pair:
            old_username, new_username = username_replace_pair.split('=', 1)
            final_caption = final_caption.replace(old_username.strip(), new_username.strip()) # Replace all occurrences
        
        # 13. CAPTION LENGTH
        caption_length_limit = caption_configs.get('caption_length_limit')
        if caption_length_limit and isinstance(caption_length_limit, int) and len(final_caption) > caption_length_limit:
            final_caption = final_caption[:caption_length_limit] + "..." # Add ellipsis if trimmed

        # Format with filename and size if placeholders are present
        # This assumes the placeholders are in the HEADER/FOOTER/PREFIX/SUFFIX or original caption
        # If the user wants to use them in the final output, they should include them in their custom texts.
        # For now, we'll just return the processed caption.
        
        # The original `caption` variable (old_caption_from_db) is no longer the primary source
        # for formatting unless the new system is disabled.
        # If the new system is enabled, the user is expected to put {filename}, {size}, {caption}
        # in their header/footer/prefix/suffix if they want them.
        
        # For now, let's just return the processed final_caption.
        # If the user has {filename}, {size}, {caption} in their custom texts, they will be formatted here.
        try:
            return final_caption.format(filename=file_name, size=get_size(file_size), caption=original_caption)
        except KeyError:
            # If placeholders are present but not all are provided, return as is
            return final_caption
  return None

def get_size(size):
  units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
  size = float(size)
  i = 0
  while size >= 1024.0 and i < len(units):
     i += 1
     size /= 1024.0
  return "%.2f %s" % (size, units[i]) 

def media(msg):
  if msg.media:
     media = getattr(msg, msg.media.value, None)
     if media:
        return getattr(media, 'file_id', None)
  return None 

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def retry_btn(id):
    return InlineKeyboardMarkup([[InlineKeyboardButton('♻️ Retry ♻️', f"start_public_{id}")]])




@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    await m.answer("Forwarding Cancelled !", show_alert=True)
          



@Client.on_callback_query(filters.regex(r'^fwrdstatus'))
async def status_msg(bot, msg):
    _, status, est_time, percentage, frwd_id = msg.data.split("#")
    sts = STS(frwd_id)
    if not sts.verify():
       fetched, forwarded, remaining = 0
    else:
       fetched, forwarded = sts.get('fetched'), sts.get('total_files')
       remaining = fetched - forwarded 
    est_time = TimeFormatter(milliseconds=est_time)
    est_time = est_time if (est_time != '' or status not in ['completed', 'cancelled']) else '0 s'
    return await msg.answer(PROGRESS.format(percentage, fetched, forwarded, remaining, status, est_time), show_alert=True)
                  


                  
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
    await update.message.reply_to_message.delete()







# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
