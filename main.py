import logging
from os import getenv
from sys import exit
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
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


def reset_in_game():
    global IN_GAME
    IN_GAME = tuple()


class Form(StatesGroup):
    name_c = State()
    name_l = State()
    name_p = State()
    new_game = State()


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


@dp.message_handler(state=Form.name_c)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()

    if message.from_id not in GAMES.keys():
        GAMES[message.from_id] = dict()
    elif message.text in GAMES[message.from_id].keys():
        await message.answer(f'The game \"{message.text}\" already exists')
        return

    GAMES[message.from_id][message.text] = []
    await message.answer(f'The game \"{message.text}\" is created')


@dp.message_handler(state=Form.name_l)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()

    if message.from_id not in GAMES.keys() or message.text not in GAMES[message.from_id]:
        await message.answer(f'The game \"{message.text}\" does not exist')
        return

    set_in_game(message.from_id, message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Add player', 'Log out']
    keyboard.add(*buttons)

    await message.answer(f'The game \"{message.text}\" is opened', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Log out')
async def cmd_start(message: types.Message):
    reset_in_game()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['New game', 'Log in to game']
    keyboard.add(*buttons)
    await message.answer("Back to the menu", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Add player')
async def cmd_start(message: types.Message):
    await Form.name_p.set()
    await message.answer("Enter the name of the player or /cancel")


@dp.message_handler(state=Form.name_p)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()

    if message.text in GAMES[IN_GAME[0]][IN_GAME[1]]:
        await message.answer(f'The player \"{message.text}\" already exists')
        return

    GAMES[IN_GAME[0]][IN_GAME[1]].append(message.text)
    await message.answer(f'The player \"{message.text}\" is added')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('ОК')


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
# @dp.errors_handler(exception=BotBlocked)
# async def error_bot_blocked(update: types.Update, exception: BotBlocked):
#     print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
#     return True
#
#


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
