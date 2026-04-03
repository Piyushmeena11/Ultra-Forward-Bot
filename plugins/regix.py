# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import os
import sys 
import math
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
                
                from_topic = sts.get('from_topic')
                if from_topic and getattr(message, 'message_thread_id', getattr(message, 'reply_to_message_id', None)) != from_topic:
                    continue
                
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
                   data = caption # the configs dict
                   new_caption = custom_caption(message, data)
                   details = {"msg_id": message.id, "media": media(message), "caption": new_caption, 'button': button, "protect": protect, "pin_message": data.get("pin_message", False)}
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
            
async def copy(bot, msg, m, sts):
   try:
     to_topic = sts.get('to_topic')                                  
     if msg.get("media") and msg.get("caption"):
        k = await bot.send_cached_media(
              chat_id=sts.get('TO'),
              file_id=msg.get("media"),
              caption=msg.get("caption"),
              reply_markup=msg.get('button'),
              reply_to_message_id=to_topic,
              protect_content=msg.get("protect"))
     else:
        k = await bot.copy_message(
              chat_id=sts.get('TO'),
              from_chat_id=sts.get('FROM'),    
              caption=msg.get("caption"),
              message_id=msg.get("msg_id"),
              reply_markup=msg.get('button'),
              reply_to_message_id=to_topic,
              protect_content=msg.get("protect"))
              
     if msg.get("pin_message"):
         try:
             await k.pin(both_sides=True)
         except Exception:
             pass
   except FloodWait as e:
     await edit(m, 'Progressing', e.value, sts)
     await asyncio.sleep(e.value)
     await edit(m, 'Progressing', 10, sts)
     await copy(bot, msg, m, sts)
   except Exception as e:
     print(e)
     sts.add('deleted')
        
async def forward(bot, msg, m, sts, protect):
   try:
     to_topic = sts.get('to_topic')                            
     for msg_id in msg:
         await bot.forward_messages(
               chat_id=sts.get('TO'),
               from_chat_id=sts.get('FROM'), 
               protect_content=protect,
               reply_to_message_id=to_topic,
               message_ids=msg_id)
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
     
def custom_caption(msg, configs):
  if not configs.get('caption_enabled', True):
    return msg.caption.html if msg.caption else None
    
  # Base caption logic
  fcaption = msg.caption.html if msg.caption else ""
  
  if configs.get('caption'):
    # If a RENEW CAPTION is set, it becomes the base
    try:
      file_name = ""
      file_size = ""
      if msg.media:
        media = getattr(msg, msg.media.value, None)
        if media:
          file_name = getattr(media, 'file_name', '')
          file_size = get_size(getattr(media, 'file_size', 0))
      
      renew = configs['caption'].replace('{{line_space}}', '\n')
      fcaption = renew.format(
        filename=file_name,
        size=file_size,
        caption=fcaption,
        modified_caption=fcaption, # Placeholder for now
        count="{count}" # Placeholder for external counting if needed
      )
    except Exception:
      pass

  # 1. Strip Before/After
  if configs.get('delete_before'):
    if fcaption.startswith(configs['delete_before']):
      fcaption = fcaption[len(configs['delete_before']):].lstrip()
  
  if configs.get('delete_after'):
    if fcaption.endswith(configs['delete_after']):
      fcaption = fcaption[:-len(configs['delete_after'])].rstrip()

  # 2. Delete Words
  if configs.get('delete_words'):
    words = [w.strip() for w in configs['delete_words'].split(',')]
    for word in words:
      fcaption = fcaption.replace(word, "")

  # 3. Replace Words
  if configs.get('replace_words'):
    pairs = [p.strip() for p in configs['replace_words'].split(',')]
    for pair in pairs:
      if ">>" in pair:
        old, new = pair.split(">>", 1)
        fcaption = fcaption.replace(old, new)

  # 4. Username Remove/Replace
  if configs.get('remove_username'):
    fcaption = re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z0-9_]+)', '', fcaption)
  elif configs.get('username_replace'):
    replacement = configs.get('username_replace')
    fcaption = re.sub(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z0-9_]+)', replacement, fcaption)

  # 5. Link Remove/Replace
  if configs.get('link_remove'):
    # Remove raw links
    fcaption = re.sub(r'https?://[^\s<]+', '', fcaption)
    # Strip hyperlink tags, keeping the inner text
    fcaption = re.sub(r'<a[^>]*href="[^"]*"[^>]*>(.*?)</a>', r'\1', fcaption)
  elif configs.get('link_replace'):
    replacement = configs.get('link_replace')
    # Replace raw links
    fcaption = re.sub(r'https?://[^\s<]+', replacement, fcaption)
    # Replace hyperlink urls, keeping the text
    fcaption = re.sub(r'(<a[^>]*href=")[^"]*("[^>]*>.*?</a>)', rf'\1{replacement}\2', fcaption)

  # 6. Apply Prefix/Suffix
  if configs.get('prefix'):
    fcaption = configs['prefix'] + fcaption
  if configs.get('suffix'):
    fcaption = fcaption + configs['suffix']

  # 7. Apply Header/Footer
  if configs.get('header'):
    fcaption = configs['header'] + "\n" + fcaption
  if configs.get('footer'):
    fcaption = fcaption + "\n" + configs['footer']

  # 8. Caption Length
  if configs.get('caption_length'):
    try:
      limit = int(configs['caption_length'])
      if len(fcaption) > limit:
        fcaption = fcaption[:limit]
    except:
      pass

  return fcaption if fcaption else None

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
