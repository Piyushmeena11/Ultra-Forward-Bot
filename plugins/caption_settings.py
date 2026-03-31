# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper

import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation
from .regix import custom_caption
from .test import get_configs, update_configs

async def caption_main_menu_buttons(user_id):
    """Generates the main caption settings menu buttons - 6 main buttons as per video."""
    configs = await get_configs(user_id)
    caption_enabled = configs.get('caption_enabled', False)

    buttons = [
        # Row 1: HEADER and FOOTER
        [InlineKeyboardButton('📝 HEADER', callback_data='settings#caption_header_menu'),
         InlineKeyboardButton('FOOTER 📝', callback_data='settings#caption_footer_menu')],
        # Row 2: PREFIX and SUFFIX
        [InlineKeyboardButton('➡️ PREFIX', callback_data='settings#caption_prefix_menu'),
         InlineKeyboardButton('SUFFIX ⬅️', callback_data='settings#caption_suffix_menu')],
        # Row 3: DELETE BEFORE and DELETE AFTER
        [InlineKeyboardButton('🗑️ DELETE BEFORE', callback_data='settings#caption_delete_before_menu'),
         InlineKeyboardButton('DELETE AFTER 🗑️', callback_data='settings#caption_delete_after_menu')],
        # Row 4: DELETE WORDS and REPLACE WORDS
        [InlineKeyboardButton('🚫 DELETE WORDS', callback_data='settings#caption_delete_words_menu'),
         InlineKeyboardButton('REPLACE WORDS 🔄', callback_data='settings#caption_replace_words_menu')],
        # Row 5: LINK REMOVE and LINK REPLACE
        [InlineKeyboardButton('🔗 LINK REMOVE', callback_data='settings#caption_link_remove_toggle'),
         InlineKeyboardButton('LINK REPLACE 🔗', callback_data='settings#caption_link_replace_menu')],
        # Row 6: USERNAME REMOVE and USERNAME REPLACE
        [InlineKeyboardButton('👤 REMOVE USERNAME', callback_data='settings#caption_username_remove_toggle'),
         InlineKeyboardButton('USERNAME REPLACE 👥', callback_data='settings#caption_username_replace_menu')],
        # Row 7: CAPTION LENGTH and RENEW
        [InlineKeyboardButton('📏 CAPTION LENGTH', callback_data='settings#caption_length_menu'),
         InlineKeyboardButton('RENEW CAPTION ♻️', callback_data='settings#caption_renew')],
        # Row 8: RESET and SEE CAPTION
        [InlineKeyboardButton('🗑️ RESET CAPTION', callback_data='settings#caption_reset'),
         InlineKeyboardButton('SEE CAPTION 👀', callback_data='settings#caption_see')],
        # Row 9: ENABLE/DISABLE and BACK
        [InlineKeyboardButton(f"{'✅ Enabled' if caption_enabled else '❌ Disabled'}", 
                            callback_data=f'settings#toggle_caption_enabled-{caption_enabled}'),
         InlineKeyboardButton('« BACK', callback_data='settings#main')]
    ]
    return InlineKeyboardMarkup(buttons)

async def handle_caption_query(bot, query, user_id, caption_type):
    """
    Handles all callback queries related to caption settings.
    """
    if caption_type == "caption":  # Entry point from main settings menu
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "Manage all aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
        return

    # --- Helper function for text input flow ---
    async def _ask_for_text_input(key, prompt_text, back_callback):
        """Ask user for text input and save it."""
        configs = await get_configs(user_id)
        current_value = configs.get(key)
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ REMOVE', callback_data=f'settings#{key}_remove')],
            [InlineKeyboardButton('🔙 BACK', callback_data=f'settings#{back_callback}')]
        ])
        
        await query.message.delete()
        msg_to_edit = await bot.send_message(
            user_id,
            f"🔧 <b>{key.replace('caption_', '').upper()}</b>\n\n"
            f"Current: <code>{current_value if current_value else 'None'}</code>\n\n"
            f"✏️ {prompt_text}\n\n"
            f"⚠️ Send your text or /cancel to cancel",
            reply_markup=buttons
        )
        
        try:
            user_input_msg = await bot.listen(chat_id=user_id, timeout=300)
            if user_input_msg.text == "/cancel":
                await user_input_msg.delete()
                return
            
            # Save the new value
            await update_configs(user_id, key, user_input_msg.text)
            await user_input_msg.delete()
            
        except asyncio.TimeoutError:
            pass
        finally:
            # Return to main caption menu
            await bot.send_message(
                user_id,
                "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
                "Manage all aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

    async def _ask_for_int_input(key, prompt_text, back_callback):
        """Ask user for integer input and save it."""
        configs = await get_configs(user_id)
        current_value = configs.get(key)
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ REMOVE', callback_data=f'settings#{key}_remove')],
            [InlineKeyboardButton('🔙 BACK', callback_data=f'settings#{back_callback}')]
        ])
        
        await query.message.delete()
        msg_to_edit = await bot.send_message(
            user_id,
            f"🔧 <b>{key.replace('caption_', '').upper()}</b>\n\n"
            f"Current: <code>{current_value if current_value else 'None'}</code>\n\n"
            f"✏️ {prompt_text}\n\n"
            f"⚠️ Send a number or /cancel to cancel",
            reply_markup=buttons
        )
        
        try:
            user_input_msg = await bot.listen(chat_id=user_id, timeout=300)
            if user_input_msg.text == "/cancel":
                await user_input_msg.delete()
                return
            
            try:
                value = int(user_input_msg.text)
                await update_configs(user_id, key, value)
                await user_input_msg.delete()
            except ValueError:
                await user_input_msg.delete()
                await msg_to_edit.edit_text(
                    f"❌ Invalid input. Please send a number.",
                    reply_markup=buttons
                )
                return
            
        except asyncio.TimeoutError:
            pass
        finally:
            # Return to main caption menu
            await bot.send_message(
                user_id,
                "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
                "Manage all aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

    async def _remove_setting(key):
        """Remove a specific caption setting."""
        await update_configs(user_id, key, None)
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "✅ Setting removed successfully!",
            reply_markup=await caption_main_menu_buttons(user_id)
        )

    # --- Handle different caption types ---
    
    if caption_type == "caption_header_menu":
        configs = await get_configs(user_id)
        await _ask_for_text_input('caption_header', 
                                 "Send the text to add at the beginning of caption", 
                                 'caption')
    
    elif caption_type == "caption_footer_menu":
        await _ask_for_text_input('caption_footer', 
                                 "Send the text to add at the end of caption", 
                                 'caption')
    
    elif caption_type == "caption_prefix_menu":
        await _ask_for_text_input('caption_prefix', 
                                 "Send text to add at the start of each line", 
                                 'caption')
    
    elif caption_type == "caption_suffix_menu":
        await _ask_for_text_input('caption_suffix', 
                                 "Send text to add at the end of each line", 
                                 'caption')
    
    elif caption_type == "caption_delete_before_menu":
        await _ask_for_text_input('caption_delete_before_word', 
                                 "Send a word. Everything BEFORE this word will be deleted", 
                                 'caption')
    
    elif caption_type == "caption_delete_after_menu":
        await _ask_for_text_input('caption_delete_after_word', 
                                 "Send a word. Everything AFTER this word will be deleted", 
                                 'caption')
    
    elif caption_type == "caption_delete_words_menu":
        await _ask_for_text_input('caption_delete_words_list', 
                                 "Send words to delete, separated by spaces\n\nExample: word1 word2 word3", 
                                 'caption')
    
    elif caption_type == "caption_replace_words_menu":
        await _ask_for_text_input('caption_replace_words_map', 
                                 "Send words in format: old=new (one per line)\n\nExample:\nold1=new1\nold2=new2", 
                                 'caption')
    
    elif caption_type == "caption_link_remove_toggle":
        configs = await get_configs(user_id)
        current_state = configs.get('caption_link_remove', False)
        new_state = not current_state
        await update_configs(user_id, 'caption_link_remove', new_state)
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "Manage all aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    
    elif caption_type == "caption_link_replace_menu":
        await _ask_for_text_input('caption_link_replace_pair', 
                                 "Send links in format: old_link=new_link\n\nExample:\nhttps://old.com=https://new.com", 
                                 'caption')
    
    elif caption_type == "caption_username_remove_toggle":
        configs = await get_configs(user_id)
        current_state = configs.get('caption_username_remove', False)
        new_state = not current_state
        await update_configs(user_id, 'caption_username_remove', new_state)
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "Manage all aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    
    elif caption_type == "caption_username_replace_menu":
        await _ask_for_text_input('caption_username_replace_pair', 
                                 "Send usernames in format: @old=@new\n\nExample:\n@olduser=@newuser", 
                                 'caption')
    
    elif caption_type == "caption_length_menu":
        await _ask_for_int_input('caption_length_limit', 
                                "Send maximum caption length (in characters)", 
                                'caption')
    
    elif caption_type == "caption_renew":
        # Re-display the main settings
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "Caption settings refreshed.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    
    elif caption_type == "caption_reset":
        # Reset all caption-related settings
        reset_keys = [
            'caption_enabled', 'caption_header', 'caption_footer',
            'caption_prefix', 'caption_suffix',
            'caption_delete_before_word', 'caption_delete_after_word',
            'caption_delete_words_list', 'caption_replace_words_map',
            'caption_link_remove', 'caption_link_replace_pair',
            'caption_username_remove', 'caption_username_replace_pair',
            'caption_length_limit'
        ]
        
        for key in reset_keys:
            await update_configs(user_id, key, None if key != 'caption_enabled' else False)
        
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "✅ All caption settings have been reset to default.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    
    elif caption_type == "caption_see":
        configs = await get_configs(user_id)
        
        # Create a sample caption preview
        sample_caption = "This is a sample caption with @username and https://example.com link"
        
        # Build caption configs for preview
        caption_configs = {
            'caption_enabled': configs.get('caption_enabled', False),
            'caption_header': configs.get('caption_header'),
            'caption_footer': configs.get('caption_footer'),
            'caption_prefix': configs.get('caption_prefix'),
            'caption_suffix': configs.get('caption_suffix'),
            'caption_delete_before_word': configs.get('caption_delete_before_word'),
            'caption_delete_after_word': configs.get('caption_delete_after_word'),
            'caption_delete_words_list': configs.get('caption_delete_words_list'),
            'caption_replace_words_map': configs.get('caption_replace_words_map'),
            'caption_link_remove': configs.get('caption_link_remove', False),
            'caption_link_replace_pair': configs.get('caption_link_replace_pair'),
            'caption_username_remove': configs.get('caption_username_remove', False),
            'caption_username_replace_pair': configs.get('caption_username_replace_pair'),
            'caption_length_limit': configs.get('caption_length_limit')
        }
        
        # Create dummy message for preview
        class DummyMessage:
            def __init__(self):
                self.media = 'document'
                self.document = type('obj', (object,), {
                    'file_name': 'sample_file.pdf',
                    'file_size': 5242880
                })()
                self.caption = type('obj', (object,), {
                    'html': sample_caption
                })()
                self.video = None
                self.photo = None
                self.audio = None
        
        dummy_msg = DummyMessage()
        preview = custom_caption(dummy_msg, None, caption_configs)
        
        preview_text = preview if preview else "No preview available"
        
        await query.message.edit_text(
            f"<b><u>📋 Caption Preview</u></b>\n\n"
            f"<b>Status:</b> {'✅ Enabled' if configs.get('caption_enabled') else '❌ Disabled'}\n\n"
            f"<b>Preview:</b>\n<code>{preview_text}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« Back', callback_data='settings#caption')]])
        )
    
    elif caption_type.startswith("caption_") and caption_type.endswith("_remove"):
        # Handle remove buttons
        key = caption_type.replace("_remove", "")
        await _remove_setting(key)
    
    elif caption_type.startswith("toggle_caption_enabled"):
        current_state = caption_type.split('-')[1] == 'True'
        new_state = not current_state
        await update_configs(user_id, 'caption_enabled', new_state)
        await query.message.edit_text(
            "<b><u>⚙️ Custom Caption Settings</u></b>\n\n"
            "Manage all aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    
    else:
        await query.answer("Unknown caption setting.", show_alert=True)


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
