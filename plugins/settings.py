# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import asyncio 
from database import db
from config import Config
from translation import Translation
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()



@Client.on_message(filters.private & filters.command(['settings']))
async def settings(client, message):
    text="<b>Change Your Settings As Your Wish</b>"
    await message.reply_text(
        text=text,
        reply_markup=main_buttons(),
        quote=True
    )
    


    
@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
  user_id = query.from_user.id
  i, type = query.data.split("#")
  
  
  if type=="main":
     await query.message.edit_text(
       "<b>Change Your Settings As Your Wish</b>",
       reply_markup=main_buttons())
       
  elif type=="bots":
     buttons = [] 
     _bot = await db.get_bot(user_id)
     if _bot is not None:
        buttons.append([InlineKeyboardButton(_bot['name'],
                         callback_data=f"settings#editbot")])
     else:
        buttons.append([InlineKeyboardButton('✚ Add Bot ✚', 
                         callback_data="settings#addbot")])
        buttons.append([InlineKeyboardButton('✚ Add User Bot ✚', 
                         callback_data="settings#adduserbot")])
     buttons.append([InlineKeyboardButton('🔙 Back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>My Bots</u></b>\n\nYou Can Manage Your Bots In Here",
       reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbot":
     back_to_bots_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#bots")]])
     await query.message.delete()
     bot = await CLIENT.add_bot(bot, query)
     if bot != True: return
     await query.message.reply_text(
        "<b>Bot Token Successfully Added To Database</b>",
        reply_markup=back_to_bots_btn)
  
  elif type=="adduserbot":
     back_to_bots_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#bots")]])
     await query.message.delete()
     user = await CLIENT.add_session(bot, query)
     if user != True: return
     await query.message.reply_text(
        "<b>Session Successfully Added To Database</b>",
        reply_markup=back_to_bots_btn)
      
  elif type=="channels":
     buttons = []
     channels = await db.get_user_channels(user_id)
     for channel in channels:
        buttons.append([InlineKeyboardButton(f"{channel['title']}",
                         callback_data=f"settings#editchannels_{channel['chat_id']}")])
     buttons.append([InlineKeyboardButton('✚ Add Channel ✚', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('🔙 Back', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>My Channels</u></b>\n\nYou Can Manage Your Target Chats In Here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="addchannel":  
     back_to_channels_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#channels")]])
     await query.message.delete()
     try:
         text = await bot.send_message(user_id, "<b><u>Set Target Chat</u></b>\n\nForward A Message From Your Target Chat\n/cancel - To Cancel This Process")
         chat_ids = await bot.listen(chat_id=user_id, timeout=300)
         if chat_ids.text=="/cancel":
            await chat_ids.delete()
            return await text.edit_text("Process Canceled", reply_markup=back_to_channels_btn)
         elif not chat_ids.forward_date:
            await chat_ids.delete()
            return await text.edit_text("This Is Not A Forward Message")
         else:
            chat_id = chat_ids.forward_from_chat.id
            title = chat_ids.forward_from_chat.title
            username = chat_ids.forward_from_chat.username
            username = "@" + username if username else "private"
         chat = await db.add_channel(user_id, chat_id, title, username)
         await chat_ids.delete()
         await text.edit_text(
            "Successfully Updated" if chat else "This Channel Already Added", reply_markup=back_to_channels_btn)
     except asyncio.exceptions.TimeoutError:
         await text.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_to_channels_btn)
  
  elif type=="editbot": 
     back_to_bots_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#bots")]])
     bot = await db.get_bot(user_id)
     TEXT = Translation.BOT_DETAILS if bot['is_bot'] else Translation.USER_DETAILS
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removebot")
               ],
               [InlineKeyboardButton('🔙 Back', callback_data="settings#bots")]]
     await query.message.edit_text(
        TEXT.format(bot['name'], bot['id'], bot['username']),
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removebot":
     await db.remove_bot(user_id)
     back_to_bots_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#bots")]])
     await query.message.edit_text(
        "Successfully Updated",
        reply_markup=back_to_bots_btn)
                                             
  elif type.startswith("editchannels"): 
     chat_id = type.split('_')[1]
     chat = await db.get_channel_details(user_id, chat_id)
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removechannel_{chat_id}")
               ],
               [InlineKeyboardButton('🔙 Back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 Channel Details</b></u>\n\n<b>Title :</b> <code>{chat['title']}</code>\n<b>Channel ID :</b> <code>{chat['chat_id']}</code>\n<b>Username :</b> {chat['username']}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("removechannel"):
     chat_id = type.split('_')[1]
     back_to_channels_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#channels")]])
     await db.remove_channel(user_id, chat_id)
     await query.message.edit_text(
        "Successfully Updated",
        reply_markup=back_to_channels_btn)

                               
  elif type=="caption":
     buttons = []
     data = await get_configs(user_id)
     caption = data['caption']
     if caption is None:
        buttons.append([InlineKeyboardButton('✚ Add Caption ✚', 
                      callback_data="settings#addcaption")])
     else:
        buttons.append([InlineKeyboardButton('👀 See Caption', 
                      callback_data="settings#seecaption")])
        buttons[-1].append(InlineKeyboardButton('🗑️ Delete Caption', 
                      callback_data="settings#deletecaption"))
     buttons.append([InlineKeyboardButton('🔙 Back', # Caption is now a top-level item
                      callback_data="settings#main")]) # Back to main settings
     await query.message.edit_text(
        "<b><u>Custom Caption</b></u>\n\nYou Can Set A Custom Caption To Videos And Documents. Normaly Use Its Default Caption\n\n<b><u>Available Fillings :</b></u>\n\n<code>{filename}</code> : Filename\n<code>{size}</code> : File Size\n<code>{caption}</code> : Default Caption",
        reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="seecaption":   
     data = await get_configs(user_id)
     buttons = [[InlineKeyboardButton('✏️ Edit Caption', 
                  callback_data="settings#addcaption")
               ],[
               InlineKeyboardButton('🔙 Back', # Back to caption menu
                 callback_data="settings#caption")]]
     await query.message.edit_text(
        f"<b><u>Your Custom Caption</b></u>\n\n<code>{data['caption']}</code>",
        reply_markup=InlineKeyboardMarkup(buttons)) # Back to caption menu
    
  elif type=="deletecaption":
     await update_configs(user_id, 'caption', None)
     back_to_caption_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#caption")]])
     await query.message.edit_text(
        "Successfully Updated",
        reply_markup=back_to_caption_btn)
                              
  elif type=="addcaption":
     back_to_caption_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#caption")]])
     await query.message.delete()
     try:
         text = await bot.send_message(query.message.chat.id, "Send your custom caption\n/cancel - <code>cancel this process</code>")
         caption = await bot.listen(chat_id=user_id, timeout=300)
         if caption.text=="/cancel":
            await caption.delete()
            return await text.edit_text("Process Canceled !", reply_markup=back_to_caption_btn)
         try:
            caption.text.format(filename='', size='', caption='')
         except KeyError as e:
            await caption.delete()
            return await text.edit_text(
               f"Wrong Filling {e} Used In Your Caption. Change It",
               reply_markup=back_to_caption_btn)
         await update_configs(user_id, 'caption', caption.text)
         await caption.delete()
         await text.edit_text(
            "Successfully Updated",
            reply_markup=back_to_caption_btn)
     except asyncio.exceptions.TimeoutError:
         await text.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_to_caption_btn)

  elif type=="button":
     buttons = []
     button = (await get_configs(user_id))['button']
     if button is None:
        buttons.append([InlineKeyboardButton('✚ Add Button ✚', 
                      callback_data="settings#addbutton")])
     else:
        buttons.append([InlineKeyboardButton('👀 See Button', 
                      callback_data="settings#seebutton")])
        buttons[-1].append(InlineKeyboardButton('🗑️ Remove Button ', 
                      callback_data="settings#deletebutton"))
     buttons.append([InlineKeyboardButton('🔙 Back', 
                      callback_data="settings#extra_settings_menu")]) # Back to extra settings menu
     await query.message.edit_text(
        "<b><u>Custom Button</b></u>\n\nYou Can Set A Inline Button To Messages.\n\n<b><u>Format :</b></u>\n`[Madflix Botz][buttonurl:https://t.me/Madflix_Bots]`\n",
        reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbutton":
     back_to_extra_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#extra_settings_menu")]])
     await query.message.delete()
     try:
         txt = await bot.send_message(user_id, text="**Send your custom button.\n\nFORMAT:**\n`[forward bot][buttonurl:https://t.me/KR_Forward_Bot]`\n")
         ask = await bot.listen(chat_id=user_id, timeout=300)
         button = parse_buttons(ask.text.html)
         if not button:
            await ask.delete()
            return await txt.edit_text("Invalid Button", reply_markup=back_to_extra_btn)
         await update_configs(user_id, 'button', ask.text.html)
         await ask.delete()
         await txt.edit_text("Successfully Button Added",
            reply_markup=back_to_extra_btn)
     except asyncio.exceptions.TimeoutError:
         await txt.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_to_extra_btn)
  
  elif type=="seebutton":
      button_config = (await get_configs(user_id))['button']
      button = parse_buttons(button, markup=False)
      button.append([InlineKeyboardButton("🔙 Back", "settings#button")])
      await query.message.edit_text(
         "**Your Custom Button**",
         reply_markup=InlineKeyboardMarkup(button))
      
  elif type=="deletebutton":
     await update_configs(user_id, 'button', None)
     back_to_button_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#button")]]) # Corrected back button
     await query.message.edit_text(
        "Successfully Button Deleted",
        reply_markup=back_to_button_btn)
   
  elif type=="database":
     buttons = []
     db_uri = (await get_configs(user_id))['db_uri']
     if db_uri is None:
        buttons.append([InlineKeyboardButton('✚ Add URL ✚', 
                      callback_data="settings#addurl")])
     else:
        buttons.append([InlineKeyboardButton('👀 See URL', 
                      callback_data="settings#seeurl")])
        buttons[-1].append(InlineKeyboardButton('🗑️ Remove URL', 
                      callback_data="settings#deleteurl"))
     buttons.append([InlineKeyboardButton('🔙 Back', 
                      callback_data="settings#extra_settings_menu")]) # Back to extra settings menu
     await query.message.edit_text(
        "<b><u>Database</u></b>\n\nDatabase Is Required For Store Your Duplicate Messages Permenant. Other Wise Stored Duplicate Media May Be Disappeared When After Bot Restart.",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addurl":
     back_to_database_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#database")]])
     await query.message.delete() 
     uri = await bot.ask(user_id, "<b>please send your mongodb url.</b>\n\n<i>get your Mongodb url from [here](https://mongodb.com)</i>", disable_web_page_preview=True)
     if uri.text=="/cancel":
        return await uri.reply_text("Process Cancelled !", reply_markup=back_to_database_btn)
     if not uri.text.startswith("mongodb+srv://") and not uri.text.endswith("majority"):
        return await uri.reply("Invalid Mongodb URL", reply_markup=back_to_database_btn)
     await update_configs(user_id, 'db_uri', uri.text)
     await uri.reply("Successfully Database URL Added ✅",
             reply_markup=back_to_database_btn)
  
  elif type=="seeurl":
     db_uri = (await get_configs(user_id))['db_uri']
     await query.answer(f"Database URL : {db_uri}", show_alert=True)
     # No message edit here, so no reply_markup needed.
  
  elif type=="deleteurl":
     await update_configs(user_id, 'db_uri', None)
     back_to_database_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#database")]]) # Corrected back button
     await query.message.edit_text(
        "Successfully Your Database URL Deleted",
        reply_markup=back_to_database_btn)
      
  elif type=="filters_menu": # Corrected entry point for filters
     await query.message.edit_text(
        "<b><u>Custom Filters</u></b>\n\nConfigure The Type Of Messages Which You Want Forward",
        reply_markup=await filters_menu_buttons(user_id))
  
  elif type=="pinning": # New pinning settings menu
     buttons = []
     data = await get_configs(user_id)
     pinning_enabled = data.get('pinning', False) # Default to False if not set
     buttons.append([
         InlineKeyboardButton('✅ Enabled' if pinning_enabled else '❌ Disabled', callback_data=f'settings#toggle_pinning-{pinning_enabled}')
     ])
     buttons.append([InlineKeyboardButton('🔙 Back', callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>Pinning Settings</u></b>\n\nEnable or disable pinning of forwarded messages in the target channel if they were pinned in the source channel.",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type.startswith("toggle_pinning"): # Toggle pinning state
     current_state = type.split('-')[1] == 'True' # Convert string 'True'/'False' to boolean
     new_state = not current_state
     await update_configs(user_id, 'pinning', new_state)
     # Re-render the pinning menu with the new state
     buttons = [[InlineKeyboardButton('✅ Enabled' if new_state else '❌ Disabled', callback_data=f'settings#toggle_pinning-{new_state}')],
                [InlineKeyboardButton('🔙 Back', callback_data="settings#main")]]
     await query.message.edit_text(
        "<b><u>Pinning Settings</u></b>\n\nEnable or disable pinning of forwarded messages in the target channel if they were pinned in the source channel.",
        reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type.startswith("updatefilter"):
     i, key, value = type.split('-')
     if value=="True":
        await update_configs(user_id, key, False)
     else:
        await update_configs(user_id, key, True)
     # All filter updates now go back to the main filters menu
     await query.edit_message_reply_markup(
        reply_markup=await filters_menu_buttons(user_id))
   
  elif type.startswith("file_size"):
    settings = await get_configs(user_id)
    size = settings.get('file_size', 0)
    i, limit = size_limit(settings['size_limit'])
    await query.message.edit_text(
       f'<b><u>Size Limit</u></b>\n\nYou Can Set File Size Limit To Forward\n\nStatus : Files With {limit} `{size} MB` Will Forward',
       reply_markup=size_button(size)) # size_button already has correct back button
  elif type.startswith("update_size"):
    size = int(query.data.split('-')[1])
    if 0 < size > 2000:
      return await query.answer("Size Limit Exceeded", show_alert=True)
    # The `size_button` function already has the correct back button.
    # No need to redefine `buttons` here.
    await update_configs(user_id, 'file_size', size)
    i, limit = size_limit((await get_configs(user_id))['size_limit'])
    await query.message.edit_text(
       f'<b><u>Size Limit</u></b>\n\nYou Can Set File Size Limit To Forward\n\nStatus : Files With {limit} `{size} MB` Will Forward', reply_markup=size_button(size)) # size_button already has correct back button
  elif type.startswith('update_limit'):
    i, limit, size = type.split('-')
    limit, sts = size_limit(limit)
    # The `size_button` function already has the correct back button.
    # No need to redefine `buttons` here.
    await update_configs(user_id, 'size_limit', limit) 
    await query.message.edit_text(
       f'<b><u>Size Limit</u></b>\n\nYou Can Set File Size Limit To Forward\n\nStatus : Files With {sts} `{size} MB` Will Forward', reply_markup=size_button(int(size))) # size_button already has correct back button
      
  elif type == "add_extension":
    back_to_extension_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#get_extension")]])
    await query.message.delete() 
    ext = await bot.ask(user_id, text="Please Send Your Extensions (Seperete By Space)")
    if ext.text == '/cancel':
       return await ext.reply_text("Process Cancelled", reply_markup=back_to_extension_btn)
    extensions = ext.text.split(" ")
    # Ensure 'extension' is initialized as a list if it's None
    # Ensure 'extension' is initialized as a list if it's None
    extension = (await get_configs(user_id))['extension']
    if extension:
        for extn in extensions:
            extension.append(extn)
    else:
        extension = extensions
    await update_configs(user_id, 'extension', extension)
    await ext.reply_text(f"Successfully Updated", reply_markup=back_to_extension_btn)
      
  elif type == "get_extension":
    # This menu is accessed from filters_menu, so back button should go there
    extensions = (await get_configs(user_id))['extension']
    btn = extract_btn(extensions)
    btn.append([InlineKeyboardButton('✚ Add ✚', 'settings#add_extension')])
    btn.append([InlineKeyboardButton('Remove All', 'settings#rmve_all_extension')])
    btn.append([InlineKeyboardButton('🔙 Back', 'settings#filters_menu')])
    await query.message.edit_text(
        text='<b><u>Extensions</u></b>\n\nFiles With These Extiontions Will Not Forward',
        reply_markup=InlineKeyboardMarkup(btn))
  
  elif type == "rmve_all_extension":
    await update_configs(user_id, 'extension', None)
    back_to_extension_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#get_extension")]])
    await query.message.edit_text(text="Successfully Deleted", reply_markup=back_to_extension_btn)
  elif type == "add_keyword":
    back_to_keyword_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#get_keyword")]])
    await query.message.delete()
    ask = await bot.ask(user_id, text="Please Send The Keywords (Seperete By Space)")
    if ask.text == '/cancel':
       return await ask.reply_text("Process Canceled", reply_markup=back_to_keyword_btn)
    keywords = ask.text.split(" ")
    keyword = (await get_configs(user_id))['keywords']
    if keyword:
        for word in keywords:
            keyword.append(word)
    else:
        keyword = keywords
    await update_configs(user_id, 'keywords', keyword) 
    await ask.reply_text(f"Successfully Updated", reply_markup=back_to_keyword_btn)
  
  elif type == "get_keyword":
    keywords = (await get_configs(user_id))['keywords']
    btn = extract_btn(keywords)
    btn.append([InlineKeyboardButton('✚ Add ✚', 'settings#add_keyword')])
    btn.append([InlineKeyboardButton('Remove All', 'settings#rmve_all_keyword')])
    btn.append([InlineKeyboardButton('🔙 Back', 'settings#filters_menu')])
    await query.message.edit_text(
        text='<b><u>Keywords</u></b>\n\nFile With These Keywords In File Name Will Forwad',
        reply_markup=InlineKeyboardMarkup(btn))
      
  elif type == "rmve_all_keyword":
    await update_configs(user_id, 'keywords', None)
    back_to_keyword_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#get_keyword")]])
    await query.message.edit_text(text="Successfully Deleted", reply_markup=back_to_keyword_btn)
  elif type.startswith("alert"):
    alert = type.split('_')[1]
    await query.answer(alert, show_alert=True)
      
def main_buttons():
  # New main menu layout as requested
  buttons = [[
       InlineKeyboardButton('🤖 Bots',
                    callback_data=f'settings#bots'),
       InlineKeyboardButton('🔥 Channels',
                    callback_data=f'settings#channels')
       ],[
       InlineKeyboardButton('✏️ Caption', # Caption is now a top-level item
                    callback_data=f'settings#caption'),
       InlineKeyboardButton('📌 Pinning', # New Pinning button
                    callback_data=f'settings#pinning')
       ],[
       InlineKeyboardButton('🕵‍♀ Filters', # Filters menu
                    callback_data=f'settings#filters_menu'),
       InlineKeyboardButton('⚙️ Extra Settings', # Extra Settings menu
                    callback_data='settings#extra_settings_menu')
       ],[      
       InlineKeyboardButton('🔙 Back', callback_data='back') # Single back button on its own line
       ]]
  return InlineKeyboardMarkup(buttons)

def size_limit(limit):
   if str(limit) == "None":
      return None, ""
   elif str(limit) == "True":
      return True, "more than"
   else:
      return False, "less than"

def extract_btn(datas):
    i = 0
    btn = []
    if datas:
       for data in datas:
         if i >= 5:
            i = 0
         if i == 0:
            btn.append([InlineKeyboardButton(data, f'settings#alert_{data}')])
            i += 1
            continue
         elif i > 0:
            btn[-1].append(InlineKeyboardButton(data, f'settings#alert_{data}'))
            i += 1
    return btn 

def size_button(size):
  buttons = [[
       InlineKeyboardButton('+',
                    callback_data=f'settings#update_limit-True-{size}'),
       InlineKeyboardButton('=',
                    callback_data=f'settings#update_limit-None-{size}'),
       InlineKeyboardButton('-',
                    callback_data=f'settings#update_limit-False-{size}')
       ],[
       InlineKeyboardButton('+1',
                    callback_data=f'settings#update_size-{size + 1}'),
       InlineKeyboardButton('-1',
                    callback_data=f'settings#update_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#update_size-{size + 5}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#update_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10',
                    callback_data=f'settings#update_size-{size + 10}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#update_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50',
                    callback_data=f'settings#update_size-{size + 50}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#update_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100',
                    callback_data=f'settings#update_size-{size + 100}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#update_size_-{size - 100}')
       ],[
       InlineKeyboardButton('↩ Back',
                    callback_data="settings#filters_menu")
     ]]
  return InlineKeyboardMarkup(buttons)
       
async def filters_menu_buttons(user_id):
  filter_configs = await get_configs(user_id)
  filters = filter_configs['filters']
  buttons = [[
       InlineKeyboardButton('🏷️ Forward Tag',
                    callback_data=f'settings_#updatefilter-forward_tag-{filter_configs["forward_tag"]}'),
       InlineKeyboardButton('✅' if filter_configs['forward_tag'] else '❌',
                    callback_data=f'settings#updatefilter-forward_tag-{filter_configs["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ Texts',
                    callback_data=f'settings_#updatefilter-text-{filters["text"]}'),
       InlineKeyboardButton('✅' if filters['text'] else '❌',
                    callback_data=f'settings#updatefilter-text-{filters["text"]}')
       ],[
       InlineKeyboardButton('▶️ Skip Duplicate',
                    callback_data=f'settings_#updatefilter-duplicate-{filter_configs["duplicate"]}'),
       InlineKeyboardButton('✅' if filter_configs['duplicate'] else '❌',
                    callback_data=f'settings#updatefilter-duplicate-{filter_configs["duplicate"]}')
       ],[
       InlineKeyboardButton('🛑 Size Limit',
                    callback_data='settings#file_size')
       ],[
       InlineKeyboardButton('💾 Extension',
                    callback_data='settings#get_extension')
       ],[
       InlineKeyboardButton('📌 Keywords',
                    callback_data='settings#get_keyword')
       ],[
       InlineKeyboardButton('--- Message Types ---', callback_data='settings#alert_Message_Types')
       ],[
       InlineKeyboardButton('🎧 Audios',
                    callback_data=f'settings_#updatefilter-audio-{filters["audio"]}'),
       InlineKeyboardButton('✅' if filters['audio'] else '❌',
                    callback_data=f'settings#updatefilter-audio-{filters["audio"]}')
       ],[
       InlineKeyboardButton('🎤 Voices',
                    callback_data=f'settings_#updatefilter-voice-{filters["voice"]}'),
       InlineKeyboardButton('✅' if filters['voice'] else '❌',
                    callback_data=f'settings#updatefilter-voice-{filters["voice"]}')
       ],[
       InlineKeyboardButton('🎭 Animations',
                    callback_data=f'settings_#updatefilter-animation-{filters["animation"]}'),
       InlineKeyboardButton('✅' if filters['animation'] else '❌',
                    callback_data=f'settings#updatefilter-animation-{filters["animation"]}')
       ],[
       InlineKeyboardButton('📁 Documents', # Added missing message types
                    callback_data=f'settings_#updatefilter-document-{filters["document"]}'),
       InlineKeyboardButton('✅' if filters['document'] else '❌',
                    callback_data=f'settings#updatefilter-document-{filters["document"]}')
       ],[
       InlineKeyboardButton('🎞️ Videos', # Added missing message types
                    callback_data=f'settings_#updatefilter-video-{filters["video"]}'),
       InlineKeyboardButton('✅' if filters['video'] else '❌',
                    callback_data=f'settings#updatefilter-video-{filters["video"]}')
       ],[
       InlineKeyboardButton('📷 Photos', # Added missing message types
                    callback_data=f'settings_#updatefilter-photo-{filters["photo"]}'),
       InlineKeyboardButton('✅' if filters['photo'] else '❌',
                    callback_data=f'settings#updatefilter-photo-{filters["photo"]}')
       ],[
       InlineKeyboardButton('🃏 Stickers',
                    callback_data=f'settings_#updatefilter-sticker-{filters["sticker"]}'),
       InlineKeyboardButton('✅' if filters['sticker'] else '❌',
                    callback_data=f'settings#updatefilter-sticker-{filters["sticker"]}')
       ],[
       InlineKeyboardButton('📊 Poll',
                    callback_data=f'settings_#updatefilter-poll-{filters["poll"]}'),
       InlineKeyboardButton('✅' if filters['poll'] else '❌',
                    callback_data=f'settings#updatefilter-poll-{filters["poll"]}')
       ],[
       InlineKeyboardButton('🔒 Secure Message',
                    callback_data=f'settings_#updatefilter-protect-{filter_configs["protect"]}'),
       InlineKeyboardButton('✅' if filter_configs['protect'] else '❌',
                    callback_data=f'settings#updatefilter-protect-{filter_configs["protect"]}')
       ],[
       InlineKeyboardButton('🔙 back',
                    callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 
   
