import logging
from os import getenv
from sys import exit
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

GAMES = dict()
IN_GAME = tuple()


def set_in_game(uid, game_name):
    global IN_GAME
    IN_GAME = (uid, game_name)


class Form(StatesGroup):
    name_c = State()
    name_l = State()
    new_game = State()
    in_game = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['New game', 'Log in to game']
    keyboard.add(*buttons)
    await message.answer('Choose an option', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'New game')
async def cmd_start(message: types.Message):
    await Form.name_c.set()
    await message.answer("Enter the name of the game or /cancel")


@dp.message_handler(lambda message: message.text == 'Log in to game')
async def cmd_start(message: types.Message):
    await Form.name_l.set()
    await message.answer("Enter the name of the game or /cancel")


@dp.message_handler(state=Form.name_l)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await state.finish()

    if message.from_id not in GAMES.keys() or data['name'] not in GAMES[message.from_id]:
        await message.answer(f'The game \"{message.text}\" does not exist')
        return

    set_in_game(message.from_id, message.text)
    await Form.in_game.set()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Add players', 'Log out']
    keyboard.add(*buttons)

    await message.answer(f'The game \"{message.text}\" is opened', reply_markup=keyboard)


# @dp.message_handler(state=Form.in_game)
# async def cmd_start(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     buttons = ['Add players', 'Log out']
#     keyboard.add(*buttons)
#     await message.answer('Choose an option', reply_markup=keyboard)



@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('ОК')


@dp.message_handler(state=Form.name_c)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    if message.from_id not in GAMES.keys():
        GAMES[message.from_id] = []
    GAMES[message.from_id].append(data['name'])

    await message.answer(f'The game \"{GAMES[message.from_id][-1]}\" is created')
    await state.finish()


#
#
# @dp.message_handler(lambda message: message.text == 'New game')
# async def without_puree(message: types.Message, state: FSMContext):
#     await Form.name.set()
#     await message.answer('Enter the name of the game')
#
#
# @dp.message_handler(state=Form.name)
# async def process_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['name'] = message.text
#
#     await Form.next()
#     await message.reply("Сколько тебе лет?")
#
#
# @dp.message_handler(lambda message: message.text == 'Log in to game')
# async def without_puree(message: types.Message):
#     await message.reply('Logging in')
#
#
# @dp.message_handler(commands="answer")
# async def cmd_answer(message: types.Message):
#     await message.answer("Это простой ответ")
#
#
# @dp.message_handler(commands="reply")
# async def cmd_reply(message: types.Message):
#     await message.reply('Это ответ с "ответом"')
#
#
# @dp.message_handler(commands="dice")
# async def cmd_dice(message: types.Message):
#     await message.answer_dice(emoji="🎲")
#
#
# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)
#
#
# @dp.errors_handler(exception=BotBlocked)
# async def error_bot_blocked(update: types.Update, exception: BotBlocked):
#     print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
#     return True
#
#


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
