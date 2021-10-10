import asyncio
import traceback

from aiogram.dispatcher import *
from aiogram.dispatcher.filters import *
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import *
from aiogram.utils.exceptions import *

from db.db_funcs import *
from loader import dp, bot


class Sex(StatesGroup):
    sex = State()


def main_board():
    keyword = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_search = KeyboardButton('Start search🔍')
    button_info_project = KeyboardButton('Info👜')
    count_user = KeyboardButton(f"""There are already {count_users()} users in the bot🥳""")
    keyword.add(button_search, button_info_project)
    keyword.row(count_user)
    return keyword


@dp.message_handler(CommandStart(), state="*")
async def start_bot(message: Message, state: FSMContext):
    if users_exists(message.from_user.id) is False:
        keyboard = InlineKeyboardMarkup(row_width=2)
        boy = InlineKeyboardButton(text='Male', callback_data='male')
        girl = InlineKeyboardButton(text='Female', callback_data='female')
        keyboard = keyboard.add(boy, girl)
        await message.answer(
            text=f'Hello <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
                 f'\nAre you male or female?',
            reply_markup=keyboard, parse_mode='html')
        await Sex.sex.set()
    elif users_exists(message.from_user.id) is True:
        remove_from_queue(message.from_user.id)
        await message.answer(text=(
            f"Hello <a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a>\n"
            f'/help - description of all bot commands.\n'
            f'/start - start a dialogue.\n'
            f'/rules - communication rules.'), reply_markup=main_board())


@dp.callback_query_handler(state=Sex.sex)
async def set_sex(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['sex'] = call.data
    try:
        new_user(call.from_user.id, call.from_user.username, data['sex'])
        await call.message.delete()
        await call.message.answer(
            f'Welcome to the bot , <a href="tg://user?id={call.from_user.id}">{call.from_user.full_name}</a>\n'
            f'🥳 You have successfully registered in our bot!\n'
            f'\n'
            f'/help - description of all bot commands.\n'
            f'/start - start a dialogue.\n'
            f'\n'
            f'/rules - communication rules.', reply_markup=main_board())
    except sqlite3.IntegrityError:
        await call.message.edit_text(text=f'Hello '
                                          f'<a href="tg://user?id={call.from_user.id}">{call.from_user.full_name}</a>')
    await state.finish()


@dp.message_handler(commands=['rules'], state='*')
@dp.message_handler(lambda message: message.text == 'Rules📖')
async def rules(message: Message):
    await message.answer(f"📌Правила общения в @plmtstbot\n"
                         f"1. Any mention of psychoactive substances. (drugs)\n"
                         f"2. Child pornography. (\"CP\")\n"
                         f"3. Fraud. (Scam)\n"
                         f"4. Any advertising, spam.\n"
                         f"5. Selling something. (for example - selling intimate photos, videos)\n"
                         f"6. Any actions that violate the Telegram rules.\n"
                         f"7. Abusive behavior.\n"
                         f"8. Exchange, distribution of any 18+ materials")


class Dialog(StatesGroup):
    msg = State()


@dp.message_handler(commands='help', state='*')
async def help_bot(message: Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, text='/start\n/help\n/search')


@dp.message_handler(commands=['search'], state='*')
@dp.message_handler(lambda message: message.text == 'Start search🔍', state='*')
async def start_search(message: Message, state: FSMContext):
    try:
        if queue_exists(message.from_user.id):
            remove_from_queue(message.from_user.id)
        add_to_queue(message.from_user.id, select_conn_with(message.from_user.id)[0][0])

        button_cancel = KeyboardButton(text="Cancel")
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard = keyboard.add(button_cancel)

        await message.answer(text='Searching user fro you...', reply_markup=keyboard)

        while True:
            await asyncio.sleep(0.5)
            for_search = [message.from_user.id, None]
            if search()[0] not in for_search:
                try:
                    update_connection(search()[0], message.from_user.id)
                    update_connection(message.from_user.id, search()[0])
                    break
                except Exception as e:
                    print(e)

        try:
            remove_from_queue(message.from_user.id)
            remove_from_queue(select_conn_with(message.from_user.id)[0][0])
        except Exception as e:
            print(e)

        await Dialog.msg.set()

        button_cancel = KeyboardButton(text="❌Stop dialog")
        button_link = KeyboardButton(text="🏹Share link")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup = markup.add(button_link, button_cancel)
        await bot.send_message(chat_id=select_conn_with(message.from_user.id)[0][0], text="Dialog started.",
                               reply_markup=markup)
        await bot.send_message(chat_id=message.from_user.id, text="Dialog started.",
                               reply_markup=markup)
        return
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(state=Dialog.msg)
@dp.message_handler(content_types=ContentTypes.TEXT)
async def chatting(message: Message, state: FSMContext):
    try:
        button_next = KeyboardButton('➡️Next Dialog')
        button_cancel = KeyboardButton('Cancel')
        menu_msg_chatting = ReplyKeyboardMarkup(resize_keyboard=True)
        menu_msg_chatting.add(button_cancel, button_next)

        await state.update_data(msg=message.text)
        user_data = await state.get_data()

        if user_data['msg'] == '❌Stop dialog':
            await message.answer('Диалог закончился!', reply_markup=menu_msg_chatting)
            await bot.send_message(select_conn_with(message.from_user.id)[0][0], 'Диалог закончился!',
                                   reply_markup=menu_msg_chatting)
            update_connection(select_conn_with(message.from_user.id)[0][0], 'NULL')
            update_connection(message.from_user.id, 'NULL')

        elif user_data['msg'] == '🏹Share link':
            if message.from_user.username is None:
                await bot.send_message(select_conn_with_self(message.from_user.id)[0][0], 'Username is empty.')
            else:
                await bot.send_message(select_conn_with_self(message.from_user.id)[0][0],
                                       "@" + message.from_user.username)
                await message.answer('@' + message.from_user.username)

        elif user_data['msg'] == '➡️Next Dialog':
            await start_search(message, state)

        elif user_data['msg'] == 'Cancel':
            await state.finish()
            await back(message, state)

        else:
            await bot.send_message(select_conn_with(message.from_user.id)[0][0], user_data['msg'])

    except ChatIdIsEmpty:
        print(traceback.format_exc())
        await state.finish()
        await help_bot(message, state)
        print("aa")
    except BotBlocked:
        await message.answer("User left chat.")
        await state.finish()
        await start_bot(message, state)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.PHOTO)
@dp.message_handler(state=Dialog.msg)
async def chatting_photo(message: Message, state: FSMContext):
    try:
        await bot.send_photo(select_conn_with(message.from_user.id)[0][0], message.photo[0].file_id,
                             caption=message.text)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.STICKER)
@dp.message_handler(state=Dialog.msg)
async def chatting_sticker(message: Message, state: FSMContext):
    try:
        await bot.send_sticker(select_conn_with(message.from_user.id)[0][0], message.sticker.file_id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(commands=['cancel'], state="*")
@dp.message_handler(lambda message: message.text == 'Cancel', state="*")
async def back(message: Message, state: FSMContext):
    await state.finish()
    await start_bot(message, state)


@dp.message_handler()
async def end(message: Message):
    await message.answer('Я не знаю, что с этим делать')
