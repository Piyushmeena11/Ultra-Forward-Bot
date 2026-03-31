# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper


import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation # Not directly used here, but kept for consistency
from .regix import custom_caption # Import custom_caption for preview
from .test import get_configs, update_configs

async def caption_main_menu_buttons(user_id):
    """Generates the main caption settings menu buttons."""
    configs = await get_configs(user_id)
    caption_enabled = configs.get('caption_enabled', False)

    buttons = [
        # Row 1
        [InlineKeyboardButton('📝 HEADER', callback_data='settings#caption_header_menu'),
         InlineKeyboardButton('FOOTER 📝', callback_data='settings#caption_footer_menu')],
        # Row 2
        [InlineKeyboardButton('➡️ PREFIX', callback_data='settings#caption_prefix_menu'),
         InlineKeyboardButton('SUFFIX ⬅️', callback_data='settings#caption_suffix_menu')],
        # Row 3
        [InlineKeyboardButton('🗑️ DELETE BEFORE', callback_data='settings#caption_delete_before_menu'),
         InlineKeyboardButton('DELETE AFTER 🗑️', callback_data='settings#caption_delete_after_menu')],
        # Row 4
        [InlineKeyboardButton('🚫 DELETE WORDS', callback_data='settings#caption_delete_words_menu'),
         InlineKeyboardButton('REPLACE WORDS 🔄', callback_data='settings#caption_replace_words_menu')],
        # Row 5
        [InlineKeyboardButton('🔗 LINK REMOVE', callback_data='settings#caption_link_remove_toggle'),
         InlineKeyboardButton('LINK REPLACE 🔗', callback_data='settings#caption_link_replace_menu')],
        # Row 6
        [InlineKeyboardButton('👤 REMOVE USERNAME', callback_data='settings#caption_username_remove_toggle'),
         InlineKeyboardButton('USERNAME REPLACE 👥', callback_data='settings#caption_username_replace_menu')],
        # Row 7
        [InlineKeyboardButton('📏 CAPTION LENGTH', callback_data='settings#caption_length_menu'),
         InlineKeyboardButton('RENEW CAPTION ♻️', callback_data='settings#caption_renew')],
        # Row 8
        [InlineKeyboardButton('🗑️ RESET CAPTION', callback_data='settings#caption_reset'),
         InlineKeyboardButton('SEE CAPTION 👀', callback_data='settings#caption_see')],
        # Row 9
        [InlineKeyboardButton(f"{'✅ Enabled' if caption_enabled else '❌ Disabled'}", callback_data=f'settings#toggle_caption_enabled-{caption_enabled}'),
         InlineKeyboardButton('« BACK', callback_data='settings#main')]
    ]
    return InlineKeyboardMarkup(buttons)

async def handle_caption_query(bot, query, user_id, caption_type):
    """
    Handles all callback queries related to caption settings.
    """
    if caption_type == "caption": # Entry point from main settings menu
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )

    # --- Helper functions for input flow ---
    async def _start_input_flow(key, prompt_title, prompt_text, current_value, back_callback_data):
        """Initiates the input flow for a specific caption setting."""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ REMOVE', callback_data=f'settings#{key.replace("caption_", "")}_remove')],
            [InlineKeyboardButton('🔙 BACK', callback_data=f'settings#{back_callback_data}')]
        ])
        await query.message.delete()
        msg_to_edit = await bot.send_message(
            user_id,
            f"🔧 <b>{prompt_title}</b>\n\nCurrent: <code>{current_value if current_value else 'None'}</code>\n\n✏️ {prompt_text}\n\n⚠️ Only single input allowed",
            reply_markup=buttons
        )
        try:
            user_input_msg = await bot.listen(chat_id=user_id, timeout=300)
            if user_input_msg.text == "/cancel":
                await user_input_msg.delete()
                await msg_to_edit.edit_text("Process Canceled!", reply_markup=buttons)
                return
            
            # Save the new value
            await update_configs(user_id, key, user_input_msg.text)
            await user_input_msg.delete()
            await msg_to_edit.edit_text("Successfully Updated!", reply_markup=buttons)
            
        except asyncio.exceptions.TimeoutError:
            await msg_to_edit.edit_text('Process Has Been Automatically Cancelled', reply_markup=buttons)
        finally:
            # Always return to the main caption menu after input or cancellation
            await query.message.edit_text(
                "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

    async def _start_int_input_flow(key, prompt_title, prompt_text, current_value, back_callback_data):
        """Initiates the integer input flow for a specific caption setting."""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton('❌ REMOVE', callback_data=f'settings#{key.replace("caption_", "")}_remove')], # Assuming remove for int means setting to None
            [InlineKeyboardButton('🔙 BACK', callback_data=f'settings#{back_callback_data}')]
        ])
        await query.message.delete()
        msg_to_edit = await bot.send_message(
            user_id,
            f"🔧 <b>{prompt_title}</b>\n\nCurrent: <code>{current_value if current_value else 'None'}</code>\n\n✏️ {prompt_text}\n\n⚠️ Only single input allowed (number)",
            reply_markup=buttons
        )
        try:
            user_input_msg = await bot.listen(chat_id=user_id, timeout=300)
            if user_input_msg.text == "/cancel":
                await user_input_msg.delete()
                await msg_to_edit.edit_text("Process Canceled!", reply_markup=buttons)
                return
            
            try:
                value = int(user_input_msg.text)
                await update_configs(user_id, key, value)
                await user_input_msg.delete()
                await msg_to_edit.edit_text("Successfully Updated!", reply_markup=buttons)
            except ValueError:
                await user_input_msg.delete()
                await msg_to_edit.edit_text("Invalid input. Please send a number.", reply_markup=buttons)
                return
            
        except asyncio.exceptions.TimeoutError:
            await msg_to_edit.edit_text('Process Has Been Automatically Cancelled', reply_markup=buttons)
        finally:
            await query.message.edit_text(
                "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

    async def _remove_setting(key, back_callback_data):
        """Removes a specific caption setting."""
        await update_configs(user_id, key, None)
        await query.message.edit_text(
            "✅ Removed successfully!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 BACK', callback_data=f'settings#{back_callback_data}')]])
        )
        # After removal, return to the main caption menu
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )

    # --- Handlers for each button ---
    configs = await get_configs(user_id) # Fetch configs once for current values

    # HEADER
    if caption_type == "caption_header_menu":
        await _start_input_flow('caption_header', "HEADER", "Send new header text.", configs.get('caption_header'), "caption")
    elif caption_type == "caption_header_remove":
        await _remove_setting('caption_header', "caption")

    # FOOTER
    elif caption_type == "caption_footer_menu":
        await _start_input_flow('caption_footer', "FOOTER", "Send new footer text.", configs.get('caption_footer'), "caption")
    elif caption_type == "caption_footer_remove":
        await _remove_setting('caption_footer', "caption")

    # PREFIX
    elif caption_type == "caption_prefix_menu":
        await _start_input_flow('caption_prefix', "PREFIX", "Send new prefix text (e.g., `🔥` for each line).", configs.get('caption_prefix'), "caption")
    elif caption_type == "caption_prefix_remove":
        await _remove_setting('caption_prefix', "caption")

    # SUFFIX
    elif caption_type == "caption_suffix_menu":
        await _start_input_flow('caption_suffix', "SUFFIX", "Send new suffix text.", configs.get('caption_suffix'), "caption")
    elif caption_type == "caption_suffix_remove":
        await _remove_setting('caption_suffix', "caption")

    # DELETE BEFORE
    elif caption_type == "caption_delete_before_menu":
        await _start_input_flow('caption_delete_before_word', "DELETE BEFORE", "Send a word. Text before this word will be removed.", configs.get('caption_delete_before_word'), "caption")
    elif caption_type == "caption_delete_before_remove":
        await _remove_setting('caption_delete_before_word', "caption")

    # DELETE AFTER
    elif caption_type == "caption_delete_after_menu":
        await _start_input_flow('caption_delete_after_word', "DELETE AFTER", "Send a word. Text after this word will be removed.", configs.get('caption_delete_after_word'), "caption")
    elif caption_type == "caption_delete_after_remove":
        await _remove_setting('caption_delete_after_word', "caption")

    # Remaining buttons (from previous implementation)
    elif caption_type == "caption_delete_words_menu":
        await _start_input_flow('caption_delete_words_list', "DELETE WORDS", "Send words to delete, separated by spaces (e.g., `word1 word2`).\n/cancel to cancel.", "caption")
    elif caption_type == "caption_replace_words_menu":
        await _start_input_flow('caption_replace_words_map', "REPLACE WORDS", "Send words to replace in `old=new` format, one pair per line.\nExample:\n`old_word1=new_word1\nold_word2=new_word2`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_link_remove_toggle":
        current_state = configs.get('caption_link_remove', False) # Get current state
        new_state = not current_state
        await update_configs(user_id, 'caption_link_remove', new_state)
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_link_replace_menu":
        await _start_input_flow('caption_link_replace_pair', "LINK REPLACE", "Send old and new link in `old_link=new_link` format.\nExample:\n`https://old.com=https://new.com`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_username_remove_toggle":
        current_state = configs.get('caption_username_remove', False) # Get current state
        new_state = not current_state
        await update_configs(user_id, 'caption_username_remove', new_state)
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_username_replace_menu":
        await _start_input_flow('caption_username_replace_pair', "USERNAME REPLACE", "Send old and new username in `@old=@new` format.\nExample:\n`@olduser=@newuser`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_length_menu":
        await _start_int_input_flow('caption_length_limit', "CAPTION LENGTH", "Send the maximum caption length (number).\n/cancel to cancel.", configs.get('caption_length_limit'), "caption")
    elif caption_type == "caption_renew":
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nCaption settings renewed. See preview below.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
        await handle_caption_query(bot, query, user_id, "caption_see")
    elif caption_type == "caption_reset":
        await update_configs(user_id, 'caption_enabled', False)
        await update_configs(user_id, 'caption_header', None)
        await update_configs(user_id, 'caption_footer', None)
        await update_configs(user_id, 'caption_prefix', None)
        await update_configs(user_id, 'caption_suffix', None)
        await update_configs(user_id, 'caption_delete_before_word', None)
        await update_configs(user_id, 'caption_delete_after_word', None)
        await update_configs(user_id, 'caption_delete_words_list', None)
        await update_configs(user_id, 'caption_replace_words_map', None)
        await update_configs(user_id, 'caption_link_remove', False)
        await update_configs(user_id, 'caption_link_replace_pair', None)
        await update_configs(user_id, 'caption_username_remove', False)
        await update_configs(user_id, 'caption_username_replace_pair', None)
        await update_configs(user_id, 'caption_length_limit', None)
        
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nAll caption settings have been reset to default.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_see":
        configs = await get_configs(user_id)
        class DummyMessage:
            def __init__(self, text, media_type=None, caption_text=None):
                self.text = text
                self._media = media_type # Store actual media type
                self.caption = type('obj', (object,), {'html': caption_text})() if caption_text else None # Mock caption object with html attribute
                self.video = None
                self.document = None
                self.audio = None
                self.photo = None
                
                # Set media flags based on media_type
                if media_type == 'video': self.video = True
                elif media_type == 'document': self.document = True
                elif media_type == 'audio': self.audio = True
                elif media_type == 'photo': self.photo = True

            @property
            def media(self):
                return type('obj', (object,), {'value': self._media})() if self._media else None # Mock media object with value attribute

        sample_original_caption_text = "This is a sample original caption with a link: https://example.com and a username: @sampleuser. Some more text here."
        
        # Create a dummy message object with a sample original caption
        dummy_msg = DummyMessage(
            text=sample_original_caption_text, 
            caption_text=sample_original_caption_text, 
            media_type='document' # Assuming a document for file_name/size in custom_caption
        )
        
        # Prepare caption_settings_for_preview from current configs
        caption_settings_for_preview = {
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

        # Call custom_caption with dummy message and the new settings
        preview_caption = custom_caption(dummy_msg, None, caption_settings_for_preview)
        
        await query.message.edit_text(
            f"<b><u>Current Caption Preview</b></u>\n\n"
            f"Caption Feature: {'✅ Enabled' if configs.get('caption_enabled', False) else '❌ Disabled'}\n\n"
            f"<b>Preview:</b>\n<code>{preview_caption}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« Back', callback_data='settings#caption')]])
        )

    elif caption_type.startswith("toggle_caption_enabled"):
        current_state = caption_type.split('-')[1] == 'True'
        new_state = not current_state
        await update_configs(user_id, 'caption_enabled', new_state) # Update with new_state
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    else:
        await query.answer("Unknown caption setting.", show_alert=True)

    # --- Handlers for each button ---
    if caption_type == "caption_header_menu":
        await _ask_for_text_input('caption_header', "Send the text you want to add as HEADER.\n/cancel to cancel.", "caption")
    elif caption_type == "caption_footer_menu":
        await _ask_for_text_input('caption_footer', "Send the text you want to add as FOOTER.\n/cancel to cancel.", "caption")
    elif caption_type == "caption_prefix_menu":
        await _ask_for_text_input('caption_prefix', "Send the text you want to add as PREFIX (e.g., `🔥` for each line).\n/cancel to cancel.", "caption")
    elif caption_type == "caption_suffix_menu":
        await _ask_for_text_input('caption_suffix', "Send the text you want to add as SUFFIX.\n/cancel to cancel.", "caption")
    elif caption_type == "caption_delete_before_menu":
        await _ask_for_text_input('caption_delete_before_word', "Send the word. Everything before this word will be deleted.\n/cancel to cancel.", "caption")
    elif caption_type == "caption_delete_after_menu":
        await _ask_for_text_input('caption_delete_after_word', "Send the word. Everything after this word will be deleted.\n/cancel to cancel.", "caption")
    elif caption_type == "caption_delete_words_menu":
        await _ask_for_text_input('caption_delete_words_list', "Send words to delete, separated by spaces (e.g., `word1 word2`).\n/cancel to cancel.", "caption")
    elif caption_type == "caption_replace_words_menu":
        await _ask_for_text_input('caption_replace_words_map', "Send words to replace in `old=new` format, one pair per line.\nExample:\n`old_word1=new_word1\nold_word2=new_word2`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_link_remove_toggle":
        configs = await get_configs(user_id)
        current_state = configs.get('caption_link_remove', False) # Get current state
        new_state = not current_state
        await update_configs(user_id, 'caption_link_remove', new_state)
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_link_replace_menu":
        await _ask_for_text_input('caption_link_replace_pair', "Send old and new link in `old_link=new_link` format.\nExample:\n`https://old.com=https://new.com`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_username_remove_toggle":
        configs = await get_configs(user_id) # Get current state
        current_state = configs.get('caption_username_remove', False)
        new_state = not current_state
        await update_configs(user_id, 'caption_username_remove', new_state)
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_username_replace_menu":
        await _ask_for_text_input('caption_username_replace_pair', "Send old and new username in `@old=@new` format.\nExample:\n`@olduser=@newuser`\n/cancel to cancel.", "caption")
    elif caption_type == "caption_length_menu":
        await _ask_for_int_input('caption_length_limit', "Send the maximum caption length (number).\n/cancel to cancel.", "caption")
    elif caption_type == "caption_renew":
        # This will essentially re-display the current settings and a preview
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nCaption settings renewed. See preview below.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
        # Simulate a preview for renew
        await handle_caption_query(bot, query, user_id, "caption_see")
    elif caption_type == "caption_reset":
        # Reset all caption-related settings to None or default
        await update_configs(user_id, 'caption_enabled', False)
        await update_configs(user_id, 'caption_header', None)
        await update_configs(user_id, 'caption_footer', None)
        await update_configs(user_id, 'caption_prefix', None)
        await update_configs(user_id, 'caption_suffix', None)
        await update_configs(user_id, 'caption_delete_before_word', None)
        await update_configs(user_id, 'caption_delete_after_word', None)
        await update_configs(user_id, 'caption_delete_words_list', None)
        await update_configs(user_id, 'caption_replace_words_map', None)
        await update_configs(user_id, 'caption_link_remove', False)
        await update_configs(user_id, 'caption_link_replace_pair', None)
        await update_configs(user_id, 'caption_username_remove', False)
        await update_configs(user_id, 'caption_username_replace_pair', None)
        await update_configs(user_id, 'caption_length_limit', None)
        
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nAll caption settings have been reset to default.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type == "caption_see":
        configs = await get_configs(user_id)
        # Create a dummy message object for preview
        class DummyMessage:
            def __init__(self, text, media=None, caption=None):
                self.text = text
                self.media = media
                self.caption = caption
                self.video = None
                self.document = None
                self.audio = None
                self.photo = None
                # Add a dummy html attribute for fcaption.html
                self.html = caption if caption else text

            @property
            def media(self):
                return self._media

            @media.setter
            def media(self, value):
                self._media = value
                if value == 'video': self.video = True
                elif value == 'document': self.document = True
                elif value == 'audio': self.audio = True
                elif value == 'photo': self.photo = True

        # Use a sample original caption for preview
        sample_original_caption = "This is a sample original caption with a link: https://example.com and a username: @sampleuser. Some more text here."
        
        # Pass all relevant configs to custom_caption
        dummy_msg = DummyMessage(text=sample_original_caption, caption=sample_original_caption, media='document') # Assuming a document for file_name/size for custom_caption
        
        # Need to pass all caption-related configs to custom_caption
        # For preview, we don't have actual file_name, file_size, etc.
        # custom_caption needs to be adapted to handle this gracefully or we pass dummy values.
        # For now, let's pass None for file_name, size, and use the sample_original_caption as fcaption
        
        # The custom_caption function in regix.py expects a 'caption' argument which is the old single custom caption.
        # We need to pass None for that, and let the new logic use the individual configs.

        # Call custom_caption with dummy message and the new settings
        # The custom_caption function in regix.py is now updated to accept these new settings.
        preview_caption = custom_caption(dummy_msg, None, caption_settings_for_preview)
        
        await query.message.edit_text(
            f"<b><u>Current Caption Preview</b></u>\n\n"
            f"Caption Feature: {'✅ Enabled' if configs.get('caption_enabled', False) else '❌ Disabled'}\n\n"
            f"<b>Preview:</b>\n<code>{preview_caption}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('« Back', callback_data='settings#caption')]])
        )

    elif caption_type.startswith("toggle_caption_enabled"):
        current_state = caption_type.split('-')[1] == 'True'
        new_state = not current_state
        await update_configs(user_id, 'caption_enabled', new_state) # Update with new_state
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    elif caption_type.startswith("toggle_caption_enabled"): # This was the problematic elif
        current_state = caption_type.split('-')[1] == 'True'
        new_state = not current_state
        await update_configs(user_id, 'caption_enabled', new_state)
        await query.message.edit_text(
            "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
            reply_markup=await caption_main_menu_buttons(user_id)
        )
    else:
        # Fallback for any unhandled caption_type, should not happen if all are covered
        await query.answer("Unknown caption setting.", show_alert=True)
