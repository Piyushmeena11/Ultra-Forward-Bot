# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import time as tm
from database import db 
from .test import parse_buttons

STATUS = {}

class STS:
    def __init__(self, id):
        self.id = id
        self.data = STATUS
    
    def verify(self):
        return self.data.get(self.id)
    
    def store(self, From, to,  skip, limit):
        self.data[self.id] = {"FROM": From, 'TO': to, 'total_files': 0, 'skip': skip, 'limit': limit,
                      'fetched': skip, 'filtered': 0, 'deleted': 0, 'duplicate': 0, 'total': limit, 'start': 0}
        self.get(full=True)
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.data.get(self.id)
        if not full:
           return values.get(value)
        for k, v in values.items():
            setattr(self, k, v)
        return self

    def add(self, key=None, value=1, time=False):
        if time:
          return self.data[self.id].update({'start': tm.time()})
        self.data[self.id].update({key: self.get(key) + value}) 
    
    def divide(self, no, by):
       by = 1 if int(by) == 0 else by 
       return int(no) / by 
    
    async def get_data(self, user_id):
        bot = await db.get_bot(user_id)
        k, filters = self, await db.get_filters(user_id)
        size, configs = None, await db.get_configs(user_id)
        if configs['duplicate']:
           duplicate = [configs['db_uri'], self.TO]
        else:
           duplicate = False
        button = parse_buttons(configs['button'] if configs['button'] else '')
        if configs['file_size'] != 0:
            size = [configs['file_size'], configs['size_limit']]
        
        # Collect all caption-related configs into a single dictionary
        caption_configs = {
            'caption_enabled': configs.get('caption_enabled', False),
            'caption_header': configs.get('caption_header'),
            'caption_footer': configs.get('caption_footer'),
            'caption_prefix': configs.get('caption_prefix'), # Corrected key
            'caption_suffix': configs.get('caption_suffix'), # Corrected key
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
        self.data[self.id]['caption_configs'] = caption_configs # Store for easy access in custom_caption
        
        return bot, configs['caption'], configs['forward_tag'], {'chat_id': k.FROM, 'limit': k.limit, 'offset': k.skip, 'filters': filters,
                'keywords': configs['keywords'], 'media_size': size, 'extensions': configs['extension'], 'skip_duplicate': duplicate}, \
                configs['protect'], button, configs.get('pinning', False), caption_configs # Pass the new caption_configs dict

    def get_all_caption_configs(self):
        return self.data[self.id].get('caption_configs', {})

def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m"
    seconds = int(seconds)
    result += f"{seconds}s"
    return result



# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
