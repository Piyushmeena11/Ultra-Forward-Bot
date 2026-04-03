# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import os
from config import Config

class Translation(object):
  START_TXT = """Hey {}

➻ I Am A Advanced Auto Forward Bot
  
➻ I Can Forward All Message From One Channel To Another Channel 
  
➻ Click Help Button To Know More About Me
  
<b>Bot Is Made By @Madflix_Bots</b>"""


  HELP_TXT = """<b><u>🛠️ Help</b></u>

<b><u>📚 Available Commands :</u></b>
⏣ __/start - Check I'm Alive__ 
⏣ __/forward - Forward Messages__
⏣ __/unequify - Delete Duplicate Messages In Channels__
⏣ __/settings - Configure Your Settings__
⏣ __/reset - Reset Your Settings__

<b><u>💢 Features :</b></u>
► __Forward Message From Public Channel To Your Channel Without Admin Permission. If The Channel Is Private Need Admin Permission__
► __Forward Message From Private Channel To Your Channel By Using Userbot(User Must Be Member In There)__
► __Custom Caption__
► __Custom Button__
► __Support Restricted Chats__
► __Skip Duplicate Messages__
► __Filter Type Of Messages__
► __Skip Messages Based On Extensions & Keywords & Size__
"""
  
  HOW_USE_TXT = """<b><u>⚠️ Before Forwarding :</b></u>
  
► __Add A Bot Or Userbot__
► __Add Atleast One To Channel (Your Bot/Userbot Must Be Admin In There)__
► __You Can Add Chats Or Bots By Using /settings__
► __If The **From Channel** Is Private Your Userbot Must Be Member In There Or Your Bot Must Need Admin Permission In There Also__
► __Then Use /forward To Forward Messages__"""
  
  ABOUT_TXT = """<b>🤖 My Name :</b> {}
<b>📝 Language :</b> <a href='https://python.org'>Python 3</a>
<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram 2.0</a>
<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a>
<b>📢 Channel :</b> <a href='https://t.me/Madflix_Bots'>Madflix Botz</a>
<b>🧑‍💻 Developer :</b> <a href='https://t.me/CallAdminRobot'>Jishu Developer</a>

<b>♻️ Bot Made By :</b> @Madflix_Bots"""
  
  STATUS_TXT = """<b><u>Bot Status</u></b>
  
<b>👱 Total Users :</b> <code>{}</code>

<b>🤖 Total Bots :</b> <code>{}</code>

<b>🔃 Forwardings :</b> <code>{}</code>
"""
  
  FROM_MSG = "<b><u>Set Source Chat</></>\n\nForward The Last Message Or Last Message Link Of Source Chat.\n/cancel - To Cancel This Process"
  TO_MSG = "<b><u>Choose Target Chat</u></b>\n\nChoose Your Target Chat From The Given Buttons.\n/cancel - To Cancel This Process"
  SKIP_MSG = "<b><u>Set Message Skiping Number</u></b>\n\nSkip The Message As Much As You Enter The Number And The Rest Of The Message Will Be Forwarded\nDefault Skip Number = <code>0</code>\n<code>eg: You Enter 0 = 0 Message Skiped\nYou Enter 5 = 5 Message Skiped</code>\n/cancel - To Cancel This Process"
  CANCEL = "Process Cancelled Succefully !"
  BOT_DETAILS = "<b><u>📄 Bot Details</u></b>\n\n<b>➣ Name :</b> <code>{}</code>\n<b>➣ Bot ID :</b> <code>{}</code>\n<b>➣ Username :</b> @{}"
  USER_DETAILS = "<b><u>📄 UserBot Details</u></b>\n\n<b>➣ Name :</b> <code>{}</code>\n<b>➣ User ID :</b> <code>{}</code>\n<b>➣ Username :</b> @{}"  
         
  TEXT = """<b><u>Forward Status</u></b>
  
<b>🕵 Fetch Message :</b> <code>{}</code>

<b>✅ Successfully Forward :</b> <code>{}</code>

<b>👥 Dublicate Message :</b> <code>{}</code>

<b>🗑 Deleted Message :</b> <code>{}</code>

<b>🪆 Skipped Message :</b> <code>{}</code>

<b>🔁 Filtered Message :</b> <code>{}</code>

<b>📊 Current Status :</b> <code>{}</code>

<b>🔥 Percentage :</b> <code>{}</code> %

{}
"""

  TEXT1 = """<b><u>Forwarded Status</u></b>

<b>🕵 Fetched Message :</b> <code>{}</code>

<b>✅ Successfully Forward :</b> <code>{}</code>

<b>👥 Dublicate Message :</b> <code>{}</code>

<b>🗑 Deleted Message :</b> <code>{}</code>

<b>🪆 Skipped :</b> <code>{}</code>

<b>📊 Stats :</b> <code>{}</code>

<b>⏳ Progress :</b> <code>{}</code>

<b>⏰ ETA :</b> <code>{}</code>

{}"""

  DUPLICATE_TEXT = """<b><u>Unequify Status</u></b>

<b>🕵 Fetched Files :</b> <code>{}</code>

<b>👥 Dublicate Deleted :</b> <code>{}</code>

{}
"""
  DOUBLE_CHECK = """<b><u>Double Checking</u></b>
  
Before Forwarding The Messages Click The Yes Button Only After Checking The Following

<b>★ Your Bot :</b> [{botname}](t.me/{botuname})
<b>★ From Channel :</b> <code>{from_chat}<>
<b>★ To Channel :</b> <code>{to_chat}</code>
<b>★ Skip Messages :</b> <code>{skip}</code>

<i>° [{botname}](t.me/{botuname}) Must Be Admin In <b>Target Chat</b></i> (<code>{to_chat}</code>)
<i>° If The <b>Source Chat</b> Is Private Your Userbot Must Be Member Or Your Bot Must Be Admin In There Also</i>

<b>If The Above Is Checked Then The Yes Button Can Be Clicked</b>"""

  CAPTION_TEXT = "```\n╔════════【 CAPTION 】═════════\n║     \n║ 〰️ YOU CAN SET A CUSTOM CAPTION TO\n║     VIDEOS AND DOCUMENTS.\n║ 〰️ NORMALY USE ITS DEFAULT CAPTION.\n╚═════════════════════════════\n```"
  HEADER_MSG = "🖊 SEND HERE FOR ADD HEADER IN CAPTION.\n\n〰️ MY SAVED WORDS FOR HEADER :\n<code>{}</code>"
  FOOTER_MSG = "🖊 SEND HERE FOR ADD FOOTER IN CAPTION.\n\n〰️ MY SAVED WORDS FOR FOOTER :\n<code>{}</code>"
  PREFIX_MSG = "🖊 SEND HERE FOR ADD PREFIX IN CAPTION.\n\n〰️ MY SAVED WORDS FOR PREFIX :\n<code>{}</code>"
  SUFFIX_MSG = "🖊 SEND HERE FOR ADD SUFFIX IN CAPTION.\n\n〰️ MY SAVED WORDS FOR SUFFIX :\n<code>{}</code>"
  DELETE_BEFORE_MSG = "🖊 SEND HERE FOR ADD DELETE BEFORE IN CAPTION.\n\n〰️ MY SAVED WORDS FOR DELETE BEFORE :\n<code>{}</code>"
  DELETE_AFTER_MSG = "🖊 SEND HERE FOR ADD DELETE AFTER IN CAPTION.\n\n〰️ MY SAVED WORDS FOR DELETE AFTER :\n<code>{}</code>"
  DELETE_WORDS_MSG = "🖊 SEND HERE FOR ADD DELETE IN CAPTION.\n\n〰️ MY SAVED WORDS FOR DELETE :\n<code>{}</code>"
  REPLACE_WORDS_MSG = "🖊 SEND HERE FOR REPLACE IN CAPTION.\n\n〰️ MULTIPLE TEXTS SEPARATE BY ,\n〰️ SEPARATE KEY AND VALUE BY >>\n\n〰️ EX :- IF YOU WANT REPLACE RAS INTO IAS AND New delhi INTO jaipur THEN SEND ➠\nRAS>>IAS,New delhi>>jaipur\n\n🖊 MY SAVED WORDS FOR REPLACE :\n<code>{}</code>"
  LINK_REPLACE_MSG = "🖊 SEND HERE FOR ADD LINK REPLACE IN CAPTION.\n\n🖊 MY SAVED WORDS FOR LINK REPLACE :\n<code>{}</code>"
  USERNAME_REPLACE_MSG = "🖊 SEND HERE FOR ADD USERNAME REPLACE IN CAPTION.\n\n🖊 MY SAVED WORDS FOR USERNAME REPLACE :\n<code>{}</code>"
  CAPTION_LENGTH_MSG = "🖊 SEND HERE FOR ADJUST LENGTH IN CAPTION.\n\n〰️ IT MUST BE POSITIVE DIGIT.\n\n〰️ MY SAVED CAPTION LENGTH :\n<code>{}</code>"
  RENEW_CAPTION_MSG = "<u><b>YOUR COMPLETE RENEW CAPTION</b></u>\n\nEDIT IT IF YOU WANT COMPLETE NEW CAPTION AS YOUR WISH."
  SEND_NEW_CAPTION_MSG = "SEND YOUR NEW CAPTION\n\nAVAILABLE FILLINGS:\n〰️ <code>{{filename}}</code> : Filename\n〰️ <code>{{size}}</code> : File size\n〰️ <code>{{caption}}</code> : Default caption\n〰️ <code>{{modified_caption}}</code> : modified caption\n〰️ <code>{{count}}</code> : counting\n\n/cancel - TO CANCEL THIS PROCESS"
  SEE_CAPTION_MSG = "〰️ MY HEADER :\n<code>{}</code>\n\n〰️ MY FOOTER :\n<code>{}</code>\n\n〰️ MY PREFIX :\n<code>{}</code>\n\n〰️ MY SUFFIX :\n<code>{}</code>\n\n〰️ MY REPLACE CAPTION :\n<code>{}</code>\n\n〰️ MY DELETE CAPTION :\n<code>{}</code>\n\n〰️ MY NEW CAPTION :\n<code>{}</code>\n\n〰️ MY CAPTION LENGTH :\n<code>{}</code>\n\n〰️ MY USERNAME REPLACE :\n<code>{}</code>\n\n〰️ MY LINK REPLACE :\n<code>{}</code>\n\n〰️ MY DELETE BEFORE :\n<code>{}</code>\n\n〰️ MY DELETE AFTER :\n<code>{}</code>"








# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
