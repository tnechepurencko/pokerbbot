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


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Enter the name of the game or /cancel")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    if message.from_id not in GAMES.keys():
        GAMES[message.from_id] = []
    GAMES[message.from_id].append(data['name'])

    await message.reply(f'The game \"{GAMES[message.from_id][-1]}\" is created')
    await state.finish()

#
# @dp.message_handler(commands='start')
# async def cmd_start(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     buttons = ['New game', 'Log in to game']
#     keyboard.add(*buttons)
#     await message.answer('Choose an option', reply_markup=keyboard)
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





# @dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
# async def process_age(message: types.Message, state: FSMContext):
#     await Form.next()
#     await state.update_data(age=int(message.text))
#
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.add("М", "Ж")
#     markup.add("Другое")
#
#     await message.reply("Укажи пол (кнопкой)", reply_markup=markup)
#
#
# # Проверяем пол
# @dp.message_handler(lambda message: message.text not in ["М", "Ж", "Другое"], state=Form.gender)
# async def process_gender_invalid(message: types.Message):
#     return await message.reply("Не знаю такой пол. Укажи пол кнопкой на клавиатуре")
#
#
# # Сохраняем пол, выводим анкету
# @dp.message_handler(state=Form.gender)
# async def process_gender(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['gender'] = message.text
#         markup = types.ReplyKeyboardRemove()
#
#         await bot.send_message(
#             message.chat.id,
#             md.text(
#                 md.text('Hi! Nice to meet you,', md.bold(data['name'])),
#                 md.text('Age:', md.code(data['age'])),
#                 md.text('Gender:', data['gender']),
#                 sep='\n',
#             ),
#             reply_markup=markup,
#             parse_mode=ParseMode.MARKDOWN,
#         )
#
#     await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
