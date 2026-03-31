# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper


import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation
from .test import get_configs, update_configs


async def handle_caption_query(bot, query, user_id, caption_type):
    """
    Handles all callback queries related to caption settings.
    """
    
    if caption_type == "caption":
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
        buttons.append([InlineKeyboardButton('🔙 Back',
                          callback_data="settings#main")]) # Back to main settings
        await query.message.edit_text(
            "<b><u>Custom Caption</b></u>\n\nYou Can Set A Custom Caption To Videos And Documents. Normaly Use Its Default Caption\n\n<b><u>Available Fillings :</b></u>\n\n<code>{filename}</code> : Filename\n<code>{size}</code> : File Size\n<code>{caption}</code> : Default Caption",
            reply_markup=InlineKeyboardMarkup(buttons))
                                   
    elif caption_type == "seecaption":
        data = await get_configs(user_id)
        buttons = [[InlineKeyboardButton('✏️ Edit Caption',
                      callback_data="settings#addcaption")
                   ],[
                   InlineKeyboardButton('🔙 Back',
                     callback_data="settings#caption")]] # Back to caption menu
        await query.message.edit_text(
            f"<b><u>Your Custom Caption</b></u>\n\n<code>{data['caption']}</code>",
            reply_markup=InlineKeyboardMarkup(buttons))
        
    elif caption_type == "deletecaption":
        await update_configs(user_id, 'caption', None)
        back_to_caption_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#caption")]])
        await query.message.edit_text(
            "Successfully Updated",
            reply_markup=back_to_caption_btn)
                                  
    elif caption_type == "addcaption":
        back_to_caption_btn = InlineKeyboardMarkup([[InlineKeyboardButton('🔙 Back', callback_data="settings#caption")]])
        await query.message.delete()
        try:
            text = await bot.send_message(query.message.chat.id, "Send your custom caption\n/cancel - <code>cancel this process</code>")
            caption_text = await bot.listen(chat_id=user_id, timeout=300)
            if caption_text.text=="/cancel":
                await caption_text.delete()
                return await text.edit_text("Process Canceled !", reply_markup=back_to_caption_btn)
            try:
                caption_text.text.format(filename='', size='', caption='')
            except KeyError as e:
                await caption_text.delete()
                return await text.edit_text(
                   f"Wrong Filling {e} Used In Your Caption. Change It",
                   reply_markup=back_to_caption_btn)
            await update_configs(user_id, 'caption', caption_text.text)
            await caption_text.delete()
            await text.edit_text(
                "Successfully Updated",
                reply_markup=back_to_caption_btn)
        except asyncio.exceptions.TimeoutError:
            await text.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_to_caption_btn)
