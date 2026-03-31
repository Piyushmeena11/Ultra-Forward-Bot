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
from .test import CLIENT, get_configs, update_configs, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CLIENT = CLIENT()

from .caption_settings import handle_caption_query

# --- Main Menu Buttons ---
def main_buttons():
    """Main settings menu layout."""
    buttons = [[
        InlineKeyboardButton('🤖 Bots', callback_data='settings#bots'),
        InlineKeyboardButton('🔥 Channels', callback_data='settings#channels')
    ],[
        InlineKeyboardButton('✏️ Caption', callback_data='settings#caption'),
        InlineKeyboardButton('📌 Pinning', callback_data='settings#pinning')
    ],[
        InlineKeyboardButton('🕵️ Filters', callback_data='settings#filters_menu'),
        InlineKeyboardButton('⚙️ Extra Settings', callback_data='settings#extra_settings_menu')
    ],[
        InlineKeyboardButton('🔙 Back', callback_data='back')
    ]]
    return InlineKeyboardMarkup(buttons)

def size_limit(limit):
    """Parse size limit setting."""
    if str(limit) == "None":
        return None, ""
    elif str(limit) == "True":
        return True, "more than"
    else:
        return False, "less than"

def extract_btn(datas):
    """Extract buttons from data."""
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
    """Generate size adjustment buttons."""
    buttons = [[
        InlineKeyboardButton('+', callback_data=f'settings#update_limit-True-{size}'),
        InlineKeyboardButton('=', callback_data=f'settings#update_limit-None-{size}'),
        InlineKeyboardButton('-', callback_data=f'settings#update_limit-False-{size}')
    ],[
        InlineKeyboardButton('+1', callback_data=f'settings#update_size-{size + 1}'),
        InlineKeyboardButton('-1', callback_data=f'settings#update_size_-{size - 1}')
    ],[
        InlineKeyboardButton('+5', callback_data=f'settings#update_size-{size + 5}'),
        InlineKeyboardButton('-5', callback_data=f'settings#update_size_-{size - 5}')
    ],[
        InlineKeyboardButton('+10', callback_data=f'settings#update_size-{size + 10}'),
        InlineKeyboardButton('-10', callback_data=f'settings#update_size_-{size - 10}')
    ],[
        InlineKeyboardButton('+50', callback_data=f'settings#update_size-{size + 50}'),
        InlineKeyboardButton('-50', callback_data=f'settings#update_size_-{size - 50}')
    ],[
        InlineKeyboardButton('+100', callback_data=f'settings#update_size-{size + 100}'),
        InlineKeyboardButton('-100', callback_data=f'settings#update_size_-{size - 100}')
    ],[
        InlineKeyboardButton('« Back', callback_data='settings#main')
    ]]
    return InlineKeyboardMarkup(buttons)

# --- Main Settings Handler ---
@Client.on_callback_query(filters.regex(r'^settings#'))
async def setting_cb(bot, query):
    try:
        user_id = query.from_user.id
        type = query.data.split('#')[1]
        
        # --- CAPTION SETTINGS (Handled separately) ---
        if type.startswith('caption') or type == 'caption':
            await handle_caption_query(bot, query, user_id, type)
            return
        
        # --- PINNING SETTINGS ---
        if type == "pinning":
            configs = await get_configs(user_id)
            pinning_enabled = configs.get('pinning', False)
            
            buttons = [[
                InlineKeyboardButton(f"{'✅ Enabled' if pinning_enabled else '❌ Disabled'}", 
                                   callback_data=f'settings#toggle_pinning-{pinning_enabled}')
            ],[
                InlineKeyboardButton('« BACK', callback_data='settings#main')
            ]]
            
            await query.message.edit_text(
                "<b><u>📌 Pinning Settings</u></b>\n\n"
                "When enabled, messages that are pinned in the source channel will also be pinned in the target channel.\n\n"
                f"<b>Current Status:</b> {'✅ Enabled' if pinning_enabled else '❌ Disabled'}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        
        elif type.startswith("toggle_pinning"):
            current_state = type.split('-')[1] == 'True'
            new_state = not current_state
            await update_configs(user_id, 'pinning', new_state)
            
            buttons = [[
                InlineKeyboardButton(f"{'✅ Enabled' if new_state else '❌ Disabled'}", 
                                   callback_data=f'settings#toggle_pinning-{new_state}')
            ],[
                InlineKeyboardButton('« BACK', callback_data='settings#main')
            ]]
            
            await query.message.edit_text(
                "<b><u>📌 Pinning Settings</u></b>\n\n"
                "When enabled, messages that are pinned in the source channel will also be pinned in the target channel.\n\n"
                f"<b>Current Status:</b> {'✅ Enabled' if new_state else '❌ Disabled'}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        
        # --- MAIN MENU ---
        elif type == "main":
            await query.message.edit_text(
                "<b><u>⚙️ Settings Menu</u></b>\n\n"
                "Choose what you want to configure:",
                reply_markup=main_buttons()
            )
        
        # --- BOTS MENU ---
        elif type == "bots":
            user_bot = await db.get_bot(user_id)
            if user_bot:
                bot_info = f"✅ <b>Bot Added</b>\n\nName: {user_bot['name']}\nUsername: @{user_bot['username']}"
                btn = [
                    [InlineKeyboardButton('✏️ Change Bot', callback_data='settings#add_bot')],
                    [InlineKeyboardButton('« BACK', callback_data='settings#main')]
                ]
            else:
                bot_info = "❌ <b>No Bot Added</b>\n\nAdd a bot to start forwarding messages."
                btn = [
                    [InlineKeyboardButton('➕ Add Bot', callback_data='settings#add_bot')],
                    [InlineKeyboardButton('« BACK', callback_data='settings#main')]
                ]
            
            await query.message.edit_text(
                "<b><u>🤖 Bot Settings</u></b>\n\n" + bot_info,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        
        elif type == "add_bot":
            result = await CLIENT.add_bot(bot, query.message)
            if result:
                await query.message.edit_text("✅ <b>Bot Added Successfully!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« BACK', callback_data='settings#bots')]]))
            else:
                await query.message.edit_text("❌ <b>Bot Addition Failed</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« BACK', callback_data='settings#bots')]]))
        
        # --- CHANNELS MENU ---
        elif type == "channels":
            channels = await db.get_user_channels(user_id)
            if channels:
                channel_list = "\n".join([f"✅ {ch['title']}" for ch in channels])
                btn = [
                    [InlineKeyboardButton('➕ Add Channel', callback_data='settings#add_channel')],
                    [InlineKeyboardButton('🗑️ Remove Channel', callback_data='settings#remove_channel')],
                    [InlineKeyboardButton('« BACK', callback_data='settings#main')]
                ]
            else:
                channel_list = "❌ <b>No Channel Added</b>"
                btn = [
                    [InlineKeyboardButton('➕ Add Channel', callback_data='settings#add_channel')],
                    [InlineKeyboardButton('« BACK', callback_data='settings#main')]
                ]
            
            await query.message.edit_text(
                "<b><u>🔥 Channel Settings</u></b>\n\n" + channel_list,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        
        elif type == "add_channel":
            # This would require async input from user
            await query.message.edit_text(
                "Send the target channel ID or username (with @):\n\n/cancel - Cancel",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« BACK', callback_data='settings#channels')]])
            )
        
        elif type == "remove_channel":
            channels = await db.get_user_channels(user_id)
            if channels:
                btn = [[InlineKeyboardButton(ch['title'], callback_data=f'settings#remove_ch_{ch["chat_id"]}')] for ch in channels]
                btn.append([InlineKeyboardButton('« BACK', callback_data='settings#channels')])
                
                await query.message.edit_text(
                    "<b>Select channel to remove:</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        
        # --- FILTERS MENU ---
        elif type == "filters_menu":
            btn = [
                [InlineKeyboardButton('📄 Document', callback_data='settings#filter_document')],
                [InlineKeyboardButton('🎬 Video', callback_data='settings#filter_video')],
                [InlineKeyboardButton('🎵 Audio', callback_data='settings#filter_audio')],
                [InlineKeyboardButton('🖼️ Photo', callback_data='settings#filter_photo')],
                [InlineKeyboardButton('« BACK', callback_data='settings#main')]
            ]
            
            await query.message.edit_text(
                "<b><u>🕵️ Filters Menu</u></b>\n\n"
                "Choose file type to configure filters:",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        
        # --- EXTRA SETTINGS ---
        elif type == "extra_settings_menu":
            btn = [
                [InlineKeyboardButton('📝 Custom Caption', callback_data='settings#caption')],
                [InlineKeyboardButton('⏷️ Forward Tag', callback_data='settings#forward_tag')],
                [InlineKeyboardButton('🔒 Protect Content', callback_data='settings#protect')],
                [InlineKeyboardButton('🔘 Buttons', callback_data='settings#buttons')],
                [InlineKeyboardButton('« BACK', callback_data='settings#main')]
            ]
            
            await query.message.edit_text(
                "<b><u>⚙️ Extra Settings</u></b>\n\n"
                "Configure additional options:",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        
        else:
            await query.answer("Unknown setting", show_alert=True)
    
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)
        logger.error(f"Settings callback error: {e}")


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
