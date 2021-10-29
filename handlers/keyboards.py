from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    boy = InlineKeyboardButton(text='Male', callback_data='male')
    girl = InlineKeyboardButton(text='Female', callback_data='female')
    keyboard.add(boy, girl)
    return keyboard


def main_keyboard(is_search=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_search = KeyboardButton('Start Search🔍')
    button_info = KeyboardButton('All sorts of things👜')
    button_cancel_search = KeyboardButton('Cancel Search')
    button_rating = KeyboardButton('Rating⭐️')
    if is_search is True:
        keyboard.add(button_cancel_search, button_rating, button_info)
    elif is_search is False:
        keyboard.add(button_search, button_rating, button_info)
    return keyboard


def about_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_rules = KeyboardButton('Rules📖')
    button_back = KeyboardButton('Back')
    button_about = KeyboardButton('About Project')
    keyboard.add(button_rules, button_back, button_about)
    return keyboard


def dialog_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_stop_dialog = KeyboardButton(text="❌Stop Dialog❌")
    button_next = KeyboardButton('➡️Next Dialog')
    button_share_link = KeyboardButton(text="🏹Share link🏹")
    keyboard.add(button_stop_dialog, button_share_link)
    keyboard.row(button_next)
    return keyboard


def after_dialog_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = KeyboardButton('Back')
    button_next = KeyboardButton('➡️Next Dialog')
    keyboard.add(button_next, button_back)
    return keyboard
