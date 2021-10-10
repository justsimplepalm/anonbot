import logging
from aiogram import executor

from config import MAIN_ADMIN
from loader import dp, bot


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


async def on_startup(dp):
    await bot.send_message(chat_id=MAIN_ADMIN,
                           text="Bot Started")


if __name__ == "__main__":
    from handlers import dp

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
