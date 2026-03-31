# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper


import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation
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
    
    # Generic function to ask for text input
    async def _ask_for_text_input(key, prompt_text, back_callback_data):
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton('« Back', callback_data=f'settings#{back_callback_data}')]])
        await query.message.delete()
        try:
            msg_to_edit = await bot.send_message(user_id, prompt_text)
            user_input = await bot.listen(chat_id=user_id, timeout=300)
            if user_input.text == "/cancel":
                await user_input.delete()
                return await msg_to_edit.edit_text("Process Canceled!", reply_markup=back_btn)
            await update_configs(user_id, key, user_input.text)
            await user_input.delete()
            await msg_to_edit.edit_text("Successfully Updated!", reply_markup=back_btn)
        except asyncio.exceptions.TimeoutError:
            await msg_to_edit.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_btn)
        finally:
            await query.message.edit_text(
                "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

    # Generic function to ask for integer input
    async def _ask_for_int_input(key, prompt_text, back_callback_data):
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton('« Back', callback_data=f'settings#{back_callback_data}')]])
        await query.message.delete()
        try:
            msg_to_edit = await bot.send_message(user_id, prompt_text)
            user_input = await bot.listen(chat_id=user_id, timeout=300)
            if user_input.text == "/cancel":
                await user_input.delete()
                return await msg_to_edit.edit_text("Process Canceled!", reply_markup=back_btn)
            try:
                value = int(user_input.text)
                await update_configs(user_id, key, value)
                await user_input.delete()
                await msg_to_edit.edit_text("Successfully Updated!", reply_markup=back_btn)
            except ValueError:
                await user_input.delete()
                return await msg_to_edit.edit_text("Invalid input. Please send a number.", reply_markup=back_btn)
        except asyncio.exceptions.TimeoutError:
            await msg_to_edit.edit_text('Process Has Been Automatically Cancelled', reply_markup=back_btn)
        finally:
            await query.message.edit_text(
                "<b><u>Custom Caption Settings</b></u>\n\nManage various aspects of your custom captions here.",
                reply_markup=await caption_main_menu_buttons(user_id)
            )

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
