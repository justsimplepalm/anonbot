import asyncio
import sqlite3
import traceback

import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ContentTypes
from aiogram.utils.exceptions import ChatIdIsEmpty, BotBlocked

from db.db_funcs import new_user, add_to_queue, search, update_conn_with, exit_queue, user_exists, check_queue, \
    select_conn_with, select_conn_with_self, count, update_count
from handlers.keyboards import start_keyboard, main_keyboard, about_keyboard, dialog_keyboard, after_dialog_keyboard
from loader import dp, bot


class Register(StatesGroup):
    sex = State()


@dp.message_handler(CommandStart(), state="*")
async def start_bot(message: Message):
    if user_exists(message.from_user.id) is False:
        await message.answer(text="Hello dear user!"
                                  "\nWhat's your sex", reply_markup=start_keyboard())
        await Register.sex.set()
    else:
        await message.answer("/help - description of all commands.\n\n"
                             "/search - start dialog.\n"
                             "/stop - stop dialog.\n"
                             "/sharelink - send partner link to your chat. (works only in dialog)\n\n"
                             "/rules - rules of bot.", reply_markup=main_keyboard())


@dp.callback_query_handler(state=Register.sex)
async def end_reg(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['sex'] = call.data
    new_user(call.from_user.id, call.from_user.username, data['sex'])
    await call.message.delete()
    await bot.send_message(call.from_user.id, text="/help - description of all commands.\n\n"
                                                   "/search - start dialog.\n"
                                                   "/stop - stop dialog.\n"
                                                   "/sharelink - send partner link to your chat. (works only in dialog)\n\n"
                                                   "/rules - rules of bot.", reply_markup=main_keyboard())
    await bot.send_message(-687036958,
                           f"New user registered : [{call.from_user.id}](tg://user?id={call.from_user.id})\n"
                           f"Users in bot : {count()}", parse_mode="MarkdownV2")


@dp.message_handler(CommandHelp(), state="*")
async def bot_help(message: Message):
    await message.answer("Help comm answer", reply_markup=main_keyboard())


@dp.message_handler(text="Back", state="*")
async def bot_back(message: Message, state: FSMContext):
    await state.finish()
    await bot_help(message)


@dp.message_handler(text="Cancel Search", state="*")
async def cancel_search(message: Message, state: FSMContext):
    await state.finish()
    if check_queue(message.from_user.id) == "True":
        exit_queue(message.from_user.id)
        await message.answer("Searching has been canceled", reply_markup=main_keyboard())
    elif check_queue(message.from_user.id) == "False":
        await message.answer('You are not in search', reply_markup=main_keyboard())


@dp.message_handler(text='All sorts of things👜', state='*')
async def about(message: Message):
    await message.answer(text='All info is there👇', reply_markup=about_keyboard())


@dp.message_handler(commands=['rules'], state='*')
@dp.message_handler(text='Rules📖', state='*')
async def rules(message: Message):
    await message.answer(f"📌Rules of @plmtstbot\n"
                         f"1. Any mention of psychoactive substances. (drugs)\n"
                         f"2. Child pornography. (\"CP\")\n"
                         f"3. Fraud. (Scam)\n"
                         f"4. Any advertising, spam.\n"
                         f"5. Selling something. (for example - selling intimate photos, videos)\n"
                         f"6. Any actions that violate the Telegram rules.\n"
                         f"7. Abusive behavior.\n"
                         f"8. Exchange, distribution of any 18+ materials")


@dp.message_handler(commands=['about'], state='*')
@dp.message_handler(text='About Project', state='*')
async def project(message: Message):
    await message.answer("Good project")


class Dialog(StatesGroup):
    msg = State()


@dp.message_handler(commands=['search'], state="*")
@dp.message_handler(text="Start Search🔍", state="*")
async def start_search(message: Message, state: FSMContext):
    try:
        if check_queue(message.from_user.id) is True:
            exit_queue(message.from_user.id)
        if select_conn_with(message.from_user.id) is not None:
            update_conn_with(message.from_user.id, 'NULL')
        add_to_queue(message.from_user.id)
        await message.answer("Searching partner for you...", reply_markup=main_keyboard(is_search=True))

        time_to_search = 0
        while True:
            await asyncio.sleep(0.5)
            time_to_search += 1

            print(f"Time : [{time_to_search}] User : [{message.from_user.id}]")

            if check_queue(message.from_user.id) == 'False':
                break

            if search() is not None and search() != message.from_user.id:

                try:
                    update_conn_with(message.from_user.id, search())
                    update_conn_with(search(), message.from_user.id)
                    break
                except Exception:
                    print(traceback.format_exc())
                    break

            if time_to_search == 600:
                try:
                    await message.answer("Sorry, there are no available users at the moment.",
                                         reply_markup=main_keyboard())
                    exit_queue(message.from_user.id)
                    break
                except Exception:
                    print(traceback.format_exc())
                    break

        try:
            exit_queue(message.from_user.id)
            exit_queue(select_conn_with(message.from_user.id)[0])
        except sqlite3.OperationalError:
            print(traceback.format_exc())
        except Exception:
            print(traceback.format_exc())

        await Dialog.msg.set()

        await bot.send_message(select_conn_with(message.from_user.id)[0],
                               text="Dialog started\n"
                                    "/next - next dialog\n"
                                    "/stop - stop dialog\n"
                                    "/sharelink - share yourself",
                               reply_markup=dialog_keyboard())
        await message.answer("Dialog started\n"
                             "/next - next dialog\n"
                             "/stop - stop dialog\n"
                             "/sharelink - share yourself",
                             reply_markup=dialog_keyboard())

    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.TEXT, state=Dialog.msg)
async def chatting_text(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['msg'] = message.text

        if data['msg'] == "❌Stop Dialog❌" or data['msg'] == "/stop":
            await bot.send_message(select_conn_with(message.from_user.id)[0], "Dialog stopped",
                                   reply_markup=after_dialog_keyboard())
            await bot.send_message(message.from_user.id, "Dialog stopped", reply_markup=after_dialog_keyboard())
            update_conn_with(select_conn_with(message.from_user.id)[0], 'NULL')
            update_conn_with(message.from_user.id, 'NULL')

        elif data['msg'] == "🏹Share link🏹" or data['msg'] == "/sharelink":
            if message.from_user.username is not None:
                await bot.send_message(select_conn_with_self(message.from_user.id)[0],
                                       text=f"<a href='tg://user?id={message.from_user.id}'>Your partner has shared link</a>",
                                       parse_mode='html')
                await message.answer(
                    text=f"<a href='tg://user?id={message.from_user.id}'>Your partner has shared link</a>\n",
                    parse_mode='html')
            elif message.from_user.username is None:
                await message.answer("You don't have user name to share link.")

        elif data['msg'] == "➡️Next Dialog" or data['msg'] == "/next":
            if select_conn_with(message.from_user.id) is not None:
                try:
                    await bot.send_message(select_conn_with(message.from_user.id)[0], "Dialog stopped",
                                           reply_markup=after_dialog_keyboard())
                except aiogram.utils.exceptions.ChatIdIsEmpty:
                    pass
                try:
                    update_conn_with(select_conn_with(message.from_user.id)[0], 'NULL')
                    update_conn_with(message.from_user.id, 'NULL')
                except sqlite3.OperationalError:
                    pass
            await state.finish()
            await start_search(message, state)

        elif data['msg'] == "Back":
            await state.finish()
            await start_bot(message)

        elif await state.get_state() == "Dialog:msg" and message.content_type == "text":
            await bot.send_message(select_conn_with(message.from_user.id)[0], text=data['msg'])
            update_count(message.from_user.id)

    except BotBlocked:
        await state.finish()
        await message.answer("User left chat...", reply_markup=main_keyboard())
        try:
            update_conn_with(select_conn_with(message.from_user.id)[0], 'NULL')
            update_conn_with(message.from_user.id, 'NULL')
        except sqlite3.OperationalError:
            pass

    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.PHOTO, state=Dialog.msg)
async def chatting_photo(message: Message, state: FSMContext):
    try:
        await bot.send_photo(select_conn_with(message.from_user.id)[0], message.photo[0].file_id,
                             caption=message.text)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.STICKER, state=Dialog.msg)
async def chatting_sticker(message: Message, state: FSMContext):
    try:
        await bot.send_sticker(select_conn_with(message.from_user.id)[0], message.sticker.file_id)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.VOICE, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_voice(select_conn_with(message.from_user.id)[0], message.voice.file_id)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.VIDEO, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_video(select_conn_with(message.from_user.id)[0], message.video.file_id)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.VIDEO_NOTE, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_video_note(select_conn_with(message.from_user.id)[0], message.video_note.file_id)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.CONTACT, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_contact(select_conn_with(message.from_user.id)[0],
                               vcard=message.contact.vcard,
                               phone_number=message.contact.phone_number,
                               first_name=message.contact.first_name,
                               last_name=message.contact.last_name, )
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.DOCUMENT, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_document(select_conn_with(message.from_user.id)[0], message.document.file_id)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.DICE, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_dice(select_conn_with(message.from_user.id)[0], message.dice.value)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.LOCATION, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_location(select_conn_with(message.from_user.id)[0],
                                longitude=message.location.longitude,
                                latitude=message.location.latitude,
                                live_period=message.location.live_period,
                                proximity_alert_radius=message.location.proximity_alert_radius,
                                heading=message.location.heading,
                                horizontal_accuracy=message.location.horizontal_accuracy)
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler(content_types=ContentTypes.VENUE, state=Dialog.msg)
async def chatting_voice(message: Message, state: FSMContext):
    try:
        await bot.send_venue(select_conn_with(message.from_user.id)[0],
                             latitude=message.venue.location.latitude,
                             longitude=message.venue.location.longitude,
                             title=message.venue.title,
                             address=message.venue.address, )
        update_count(message.from_user.id)
    except Exception:
        print(traceback.format_exc())


@dp.message_handler()
async def err_handler(message: Message):
    await message.answer("Unknown command")
