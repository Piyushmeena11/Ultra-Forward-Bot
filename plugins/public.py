# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper





import re
import asyncio 
from .utils import STS
from database import db
from config import temp 
from translation import Translation
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait 
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
 


 
#===================Run Function===================#

@Client.on_message(filters.private & filters.command(["fwd", "forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
      return await message.reply("You Did Not Added Any Bot. Please Add A Bot Using /settings !")
    channels = await db.get_user_channels(user_id)
    if not channels:
       return await message.reply_text("Please Set A To Channel In /settings Before Forwarding")
    if len(channels) > 1:
       for channel in channels:
          title = channel['title']
          if channel.get('topic_id'):
              title += f" (Topic: {channel['topic_id']})"
          buttons.append([KeyboardButton(title)])
          btn_data[title] = {"chat_id": channel['chat_id'], "topic_id": channel.get('topic_id')}
       buttons.append([KeyboardButton("cancel")]) 
       _toid = await bot.ask(message.chat.id, Translation.TO_MSG, reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
       if _toid.text.startswith(('/', 'cancel')):
          return await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())
       to_title = _toid.text
       to_dest = btn_data.get(to_title)
       if not to_dest:
          return await message.reply_text("Wrong Channel Choosen !", reply_markup=ReplyKeyboardRemove())
       toid = to_dest['chat_id']
       to_topic_id = to_dest['topic_id']
    else:
       toid = channels[0]['chat_id']
       to_topic_id = channels[0].get('topic_id')
       title = channels[0]['title']
       if to_topic_id:
           title += f" (Topic: {to_topic_id})"
       to_title = title
    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return 
    if fromid.text and not fromid.forward_date:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)(/(\d+))?$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid Link')
            
        chat_id_str = match.group(4)
        if match.group(7):
            from_topic_id = int(match.group(5))
            last_msg_id = int(match.group(7))
        else:
            from_topic_id = None
            last_msg_id = int(match.group(5))
            
        if chat_id_str.isnumeric():
            chat_id = int("-100" + chat_id_str)
        else:
            chat_id = chat_id_str
            
    elif getattr(fromid, 'forward_from_chat', None) and fromid.forward_from_chat.type in [enums.ChatType.CHANNEL, enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        from_topic_id = getattr(fromid, 'message_thread_id', None)
        
        if last_msg_id == None:
           return await message.reply_text("This May Be A Forwarded Message From A Group And Sended By Anonymous Admin. Instead Of This Please Send Last Message Link From Group")
    else:
        await message.reply_text("Invalid Link/Forward !")
        return 
    try:
        chat_info = await bot.get_chat(chat_id)
        title = chat_info.title
        if from_topic_id:
            title += f" (Topic: {from_topic_id})"
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "private" if getattr(fromid, 'text', None) else getattr(fromid.forward_from_chat, 'title', "private")
        if from_topic_id:
            title += f" (Topic: {from_topic_id})"
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link Specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return
    forward_id = f"{user_id}-{skipno.id}"
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Translation.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id), from_topic=from_topic_id, to_topic=to_topic_id)







# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
