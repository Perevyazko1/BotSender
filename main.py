from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import sqlite3 as sq
import asyncio
import aioschedule
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                                      MessageToDeleteNotFound, BotBlocked, BotKicked)
from contextlib import suppress
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import filters

storage = MemoryStorage()
# bot_token = '5463577812:AAEeYWZMkwYjRxf3Gm_cEsGZvYxG__ohMY0'
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)

btnMonday = KeyboardButton('Понедельник')
btnTuesday = KeyboardButton('Вторник')
btnWednesday = KeyboardButton('Среда')
btnThursday = KeyboardButton('Четверг')
btnFriday = KeyboardButton('Пятница')
btnSaturday = KeyboardButton('Суббота')
btnSunday = KeyboardButton('Воскресенье')
btnEveryday = KeyboardButton('Каждый день')
btnEsc = KeyboardButton('Отмена')
dayMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnEveryday, btnSunday, btnSaturday, btnThursday, btnFriday,
                                                        btnWednesday, btnMonday, btnTuesday, btnEsc)


def clear_text(a):
    a = str(a)
    a = a.split("'")
    a = ''.join(a)
    a = a.split(")")
    a = ''.join(a)
    a = a.split("(")
    a = ''.join(a)
    a = a.split(",")
    a = '|'.join(a)
    a = a.split("]")
    a = ''.join(a)
    a = a.split("[")
    a = ''.join(a)
    return a


@dp.message_handler(commands="start")
async def start(message: types.Message):
    global id_user
    id_user = message.from_id
    group = message.chat.id
    print(group)
    await message.answer(f'Привет {message.from_user.full_name} \n\n' '<i>Этот бот предназначен для отправки заданных '
                         'сообщений в ТОЛЬКО в группу по расписанию.\n\n'
                         'Для в заимодействия с ботом необходимо добавить его в группу и назначить администратором.</i>\n\n'
                         '<b><u>ЗАДАЧИ МОЖЕТ ВЫСТАВЛЯТЬ ТОЛЬКО АДМИНИСТРАТОР ЧАТА</u></b>',
                         parse_mode=types.ParseMode.HTML, disable_notification=True)
    sql_add_user_base('CREATE TABLE IF NOT EXISTS users (date,id, time, task, descriptions)')
    await bot.send_video(message.chat.id,open('IMG_7784.mp4','rb'))

class FSMcreatetask(StatesGroup):  # сохранение запрашиваемого перевода в машину состояния
    date = State()
    id = State()
    time = State()
    task = State()
    descriptions = State()


@dp.message_handler(commands="task", state=None, is_chat_admin=True)
async def task(message: types.Message):
    await FSMcreatetask.date.set()
    await message.answer('<i>Выберете день недели. </i>', reply_markup=dayMenu,
                         parse_mode=types.ParseMode.HTML, disable_notification=True)
    await message.answer('<i>И нажмите кнопку.</i>👇', reply_markup=dayMenu,
                         parse_mode=types.ParseMode.HTML, disable_notification=True)

@dp.message_handler(state=FSMcreatetask.date)
async def load_name(message: types.Message, state: FSMContext):
    if message.text == 'Понедельник' or message.text == 'Вторник' or message.text == 'Среда' \
            or message.text == 'Четверг' or message.text == 'Пятница' or message.text == 'Суббота' \
            or message.text == 'Воскресенье' or message.text == 'Каждый день':
        async with state.proxy() as data:
            data['date'] = message.text
            data['id'] = message.chat.id
        await FSMcreatetask.time.set()
        await message.answer('<i>Введите время задачи в формате 24-часовом формате Пример: 00:00</i>',
                             parse_mode=types.ParseMode.HTML, reply_markup=ReplyKeyboardRemove(), disable_notification=True)
    elif message.text == 'Отмена':
        await state.finish()
        await message.answer('<i>Создание задачи отменено.</i>', parse_mode=types.ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove(), disable_notification=True)

    else:
        await message.answer('<b>Не правильно!</b>\n\n'
                             ' <i>Выберете день недели. </i>', parse_mode=types.ParseMode.HTML,
                             reply_markup=dayMenu, disable_notification=True)
        await message.answer('<i>И нажмите кнопку.</i>👇', reply_markup=dayMenu,
                             parse_mode=types.ParseMode.HTML, disable_notification=True)

        # await FSMcreatetask.date.set()


@dp.message_handler(state=FSMcreatetask.time)
async def load_time(message: types.Message, state: FSMContext):
    testmessage = message.text
    testmessage = testmessage.split(":")
    testmessage = ''.join(testmessage)
    testmessage = testmessage.isdigit()
    if testmessage and len(message.text) == 5:
        async with state.proxy() as data:
            data['time'] = message.text
        await FSMcreatetask.task.set()
        await message.answer('<i>Введите задачу.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)
    else:
        await message.answer('<b>Не правильно!</b>\n\n'
                             '<i>Введите время задачи в формате 24-часовом формате Пример: 00:00</i>',
                             parse_mode=types.ParseMode.HTML, reply_markup=ReplyKeyboardRemove(), disable_notification=True)
        await FSMcreatetask.time.set()


@dp.message_handler(content_types=ContentType.VIDEO_NOTE,state=FSMcreatetask.task)
async def video_note(message: types.Message, state: FSMContext):
    await message.answer('<i>Видеокружки не принимаются, нажмите на 📎 для записи видео</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.VOICE,state=FSMcreatetask.task)
async def voice(message: types.Message, state: FSMContext):
    await message.answer('<i>Голосовые сообщения тоже не принимаются 🤦‍, нажмите на 📎 для записи видео.</i>',parse_mode=types.ParseMode.HTML)

@dp.message_handler(content_types=ContentType.PHOTO,state=FSMcreatetask.task)
async def video_note(message: types.Message, state: FSMContext):
    await message.answer('<i>Фото не принимаются, нажмите на 📎 для записи видео</i>',parse_mode=types.ParseMode.HTML)



@dp.message_handler(state=FSMcreatetask.task)
async def load_task_sql(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['task'] = message.text
    await FSMcreatetask.descriptions.set()
    await message.answer('<i>Введите название задачи.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)


@dp.message_handler(state=FSMcreatetask.descriptions)
async def load_descriptions(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['descriptions'] = message.text
    await sql_add_command(state, 'INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)')  # выводил в базу
    await message.answer('<i>Задача сохранена!</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)
    await state.finish()
    sql_add_user_base('CREATE TABLE IF NOT EXISTS users (date,id, time, task, descriptions)')
    send_task()


@dp.message_handler(commands="list_task", state=None, is_chat_admin=True)
async def task(message: types.Message):
    group = message.chat.id
    list = sql_task(f'SELECT date, time, task, descriptions FROM users WHERE id = {str(group)}')
    print(list)
    if list:
        for task in list:
            await message.answer(clear_text(task))
    else:
        await message.answer('<i>Никаких задач не назначено.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)


class FSMdeletetask(StatesGroup):  # удаление задачи
    task = State()


@dp.message_handler(commands="delete_task", state=None, is_chat_admin=True)
async def task(message: types.Message):
    await FSMdeletetask.task.set()
    await message.answer('<i>Введите задачу для удаления.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)


@dp.message_handler(state=FSMdeletetask.task)
async def load_name(message: types.Message, state: FSMContext):
    group = message.chat.id
    async with state.proxy() as data:
        data['task'] = message.text
        request = str(tuple(data.values()))[2:-3]

    await state.finish()
    sql = sql_reqwest_task(f"SELECT * FROM users WHERE id = {str(group)} and descriptions = '{request}'")

    sql_task(f"DELETE from users where id = {group} and descriptions = '{request}'")
    if sql:
        await message.answer('<i>Задача удалена.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)
    else:
        await message.answer('<i>Задача не найдена.</i>', parse_mode=types.ParseMode.HTML, disable_notification=True)


# _________________________Запись в базу______________________


async def sql_add_command(state, request):
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    async with state.proxy() as data:
        cur.execute(request, tuple(data.values()))
        base.commit()


def sql_task(reqwest):
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    cur.execute(reqwest).fetchall()
    base.commit()
    return cur.execute(reqwest).fetchall()


def sql_add_user_base(reqwest):
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    if base:
        print('База подключена')
    base.execute(reqwest)
    base.commit()


def sql_reqwest_task(reqwest):
    global base, cur
    base = sq.connect('task.db')
    cur = base.cursor()
    cur.execute(reqwest).fetchall()
    base.commit()
    return cur.execute(reqwest).fetchall()


@dp.message_handler(filters.Text(contains='бот', ignore_case=True))
async def text_example(msg: types.Message):
    await msg.reply('Это вы про меня)?')


@dp.message_handler()
async def load_task(message: types.Message):
    if message.text == '/start@CREATOR_TASK_FOR_CHAT_BOT' or message.text == '/task@CREATOR_TASK_FOR_CHAT_BOT' \
            or message.text == '/delete_task@CREATOR_TASK_FOR_CHAT_BOT' or message.text == '/list_task@CREATOR_TASK_FOR_CHAT_BOT':
        try:
            await message.delete()
        except MessageCantBeDeleted:
            await asyncio.sleep(1)

@dp.message_handler(state=FSMcreatetask.descriptions)
async def load_task(chat_id_group, text_task):
    try:
        await dp.bot.send_message(chat_id=chat_id_group, text=text_task)
        await asyncio.sleep(1)
    except BotKicked:
        await asyncio.sleep(1)


async def send_task():
    sql_tasks_sunday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Воскресенье"')
    for sql_task_sunday in sql_tasks_sunday:
        aioschedule.every().sunday.at(time_str=str(sql_task_sunday[1])).do(load_task, sql_task_sunday[0],
                                                                           sql_task_sunday[2])

    sql_tasks_saturday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Суббота"')
    for sql_task_saturday in sql_tasks_saturday:
        aioschedule.every().saturday.at(time_str=str(sql_task_saturday[1])).do(load_task, sql_task_saturday[0],
                                                                               sql_task_saturday[2])

    sql_tasks_friday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Пятница"')
    for sql_task_friday in sql_tasks_friday:
        aioschedule.every().friday.at(time_str=str(sql_task_friday[1])).do(load_task, sql_task_friday[0],
                                                                           sql_task_friday[2])

    sql_tasks_thursday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Четверг"')
    for sql_task_thursday in sql_tasks_thursday:
        aioschedule.every().thursday.at(time_str=str(sql_task_thursday[1])).do(load_task, sql_task_thursday[0],
                                                                               sql_task_thursday[2])

    sql_tasks_wednesday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Среда"')
    for sql_task_wednesday in sql_tasks_wednesday:
        aioschedule.every().wednesday.at(time_str=str(sql_task_wednesday[1])).do(load_task, sql_task_wednesday[0],
                                                                                 sql_task_wednesday[2])

    sql_tasks_tuesday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Вторник"')
    for sql_task_tuesday in sql_tasks_tuesday:
        aioschedule.every().tuesday.at(time_str=str(sql_task_tuesday[1])).do(load_task, sql_task_tuesday[0],
                                                                             sql_task_tuesday[2])

    sql_tasks_monday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Понедельник"')
    for sql_task_monday in sql_tasks_monday:
        aioschedule.every().monday.at(time_str=str(sql_task_monday[1])).do(load_task, sql_task_monday[0],
                                                                           sql_task_monday[2])

    sql_tasks_everyday = sql_reqwest_task(f'SELECT id, time, task FROM users WHERE  date = "Каждый день"')
    for sql_task_everyday in sql_tasks_everyday:
        aioschedule.every().day.at(time_str=str(sql_task_everyday[1])).do(load_task, sql_task_everyday[0],
                                                                          sql_task_everyday[2])
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(send_task())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
