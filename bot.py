import pickle
from traceback import print_exception
from functools import wraps

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = ''
ADMIN = 0

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

def checker(func):
    @wraps(func)
    def wrapper(message: types.Message):
        if message.chat.id == ADMIN:
            return func(message)
        return False
    return wrapper

def save_data(**kwargs):
    with open('settings', 'rb') as f:
        data = pickle.load(f)
    for key, value in kwargs.items():
        data[key] = value if value else data[key]
    with open('settings', 'wb') as f:
        pickle.dump(data, f)

@dp.message_handler(commands=['start'])
@checker
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Указать user-agent')
    button2 = KeyboardButton('Указать cookies')
    button3 = KeyboardButton('Указать максимальную цену')
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    text = 'Начало работы с ботом'
    await bot.send_message(ADMIN, text, reply_markup=markup)

@dp.message_handler(state='*', text='Указать user-agent')
@checker
async def set_agent(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.set_state('USER_AGENT')
    text = 'Введите ваш user-agent'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='USER_AGENT')
@checker
async def save_agent(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.reset_state()
    user_agent = message.text
    save_data(user_agent=user_agent)
    text = 'User-Agent сохранен'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='*', text='Указать cookies')
@checker
async def set_cookies(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.set_state('COOKIE1')
    text = 'Введите значение cookie cr00'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='COOKIE1')
@checker
async def save_cookie1(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.set_state('COOKIE2')
    cr = message.text
    save_data(cr=cr)
    text = 'Введите значение cookie p20t'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='COOKIE2')
@checker
async def save_cookie2(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.reset_state()
    p2 = message.text
    save_data(p2=p2)
    text = 'Cookie сохранены'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='*', text='Указать максимальную цену')
@checker
async def set_price(message: types.Message):
    state = dp.current_state(user=ADMIN)
    await state.set_state('MAX_PRICE')
    text = 'Введите максимальную цену, это должно быть целое число или с плавающей запятой(точкой) в рублях'
    await bot.send_message(ADMIN, text)

@dp.message_handler(state='MAX_PRICE')
@checker
async def save_price(message: types.Message):
    state = dp.current_state(user=ADMIN)
    try:
        price = float(message.text)
        save_data(price=price)
        await state.reset_state()
        text = 'Максимальная цена сохранена'
    except ValueError:
        text = 'Цена должна быть целым числом или дробью с точкой в качестве разделителя'
    await bot.send_message(ADMIN, text)

async def bought(link):
    text = 'Куплен товар: {}'.format(link)
    await bot.send_message(ADMIN, text)

async def unlogin():
    text = 'Нет доступа к аккаунту, введите ваши куки и user-agent'
    await bot.send_message(ADMIN, text)

def activate_bot(on_startup):
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
        except Exception as error:
            with open('bot.log.error', 'a') as f:
                print_exception(type(error), error, error.__traceback__, file=f)