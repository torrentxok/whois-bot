from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

# reply кнопки
btn_start = KeyboardButton('/start')
btn_help = KeyboardButton('/help')
btn_command_list = KeyboardButton('/commands')

kb_whois = ReplyKeyboardMarkup(resize_keyboard=True)
kb_whois.row(btn_start, btn_help, btn_command_list)

# inline кнопки
btn_find = InlineKeyboardButton(text='/find     { your domain }', switch_inline_query_current_chat='/find ')
btn_add_domain = InlineKeyboardButton(text='/add    { your domain }', switch_inline_query_current_chat='/add ')
btn_delete_donaim = InlineKeyboardButton(text='/delete    { your domain }', switch_inline_query_current_chat='/delete ')
btn_domain_list = InlineKeyboardButton(text='/list', switch_inline_query_current_chat='/list ')

inline_kb_whois = InlineKeyboardMarkup(row_width=2)
inline_kb_whois.add(btn_find, btn_domain_list).add(btn_add_domain, btn_delete_donaim)