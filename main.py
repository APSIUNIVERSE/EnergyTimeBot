import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup, any_state
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardButton, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import database
import letter_db
import users_db
from aiogram.exceptions import TelegramBadRequest
import re
import datetime
import humanize


TOKEN = "..."
dp = Dispatcher()
bot = Bot(token=TOKEN)
storage = MemoryStorage()
ADMIN_ID = [..., ..., ...]


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


class PaginationGame(CallbackData, prefix="pag_game"):
    action: str
    page: int


class PaginationMessage(CallbackData, prefix="pag_message"):
    action: str
    page: int


class PaginationDelete(CallbackData, prefix="pag_delete"):
    action: str
    page: int


class PaginationDeleteUser(CallbackData, prefix="pag_delete_user"):
    action: str
    page: int


class PaginationInfo(CallbackData, prefix="pag_info"):
    action: str
    page: int


class NewGame(StatesGroup):
    link = State()
    name = State()
    energy = State()
    interval = State()
    interval_energy = State()
    check = State()


class MessageSend(StatesGroup):
    message = State()
    button = State()
    link = State()
    check = State()
    game = State()
    end = State()


class DeleteGame(StatesGroup):
    game = State()
    delete = State()


class InfoGame(StatesGroup):
    game = State()
    info = State()
    photo = State()


tasks = {}
admin_kb = ReplyKeyboardBuilder()
admin_kb.add(KeyboardButton(text="Добавить новую игру"), KeyboardButton(text="Удалить игру"))
admin_kb.row(KeyboardButton(text="Рассылка"), KeyboardButton(text="Статистика"))
admin_kb.row(KeyboardButton(text="Актуальные проекты / Описание"))


@dp.message(CommandStart(), StateFilter(any_state))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        if message.from_user.id in ADMIN_ID:
            await letter_db.sql_add_users_command(message.from_user.id)
            await users_db.sql_add_users_command(message.from_user.id, f"@{message.from_user.username}")
            await message.answer("👋 Hi! \n\n💎 I'm the only official bot EnergyTimeBot✅\n\n🤖 Collected all telegram clickers in one place.\n\n🔋 I will notify you when the energy in your games is 100% ready to collect\n\n🌟 Help you not to miss collecting coins and energy = increase your earnings in games\n\n🕵️ Daily all the latest news on each project (insides/codes/combos)\n\n📃 Instruction on how to set up the bot will take 60 seconds of your time, and in return will save you more than 120 minutes daily.\n\n- Type /help\n\nOr click on the Menu🟰 button in the bottom left corner of the screen, a menu will open with a selection of commands, click help.",
                                 reply_markup=await paginator(id=message.from_user.id, page=0), parse_mode='HTML')
            await message.answer(f"👋 Приветствую тебя, уважаемый администратор! Тебе доступны следующие команды:\n\n🕹 Добавить новую игру: Возможность добавления игр, путём заполнения некоторых данных (ссылка на игру, название и т.д.)\n\n🗑 Удалить игру: Ты можешь удалить любую устаревшую/неинтересную игру\n\n📬 Рассылка: Возможность разослать сообщение, с привязанной к нему кнопкой, любым пользователям\n\n📊 Статистика: Получение статистики каждого пользователя\n\n📌 Актуальные проекты / Описание: Ты можешь изменять информацию о любой игре",
                                 reply_markup=admin_kb.as_markup(resize_keyboard=True), parse_mode='HTML')
        else:
            await users_db.sql_add_users_command(message.from_user.id, f"@{message.from_user.username}")
            await letter_db.sql_add_users_command(message.from_user.id)
            await message.answer("👋 Hi! \n\n💎 I'm the only official bot EnergyTimeBot✅\n\n🤖 Collected all telegram clickers in one place.\n\n🔋 I will notify you when the energy in your games is 100% ready to collect\n\n🌟 Help you not to miss collecting coins and energy = increase your earnings in games\n\n🕵️ Daily all the latest news on each project (insides/codes/combos)\n\n📃 Instruction on how to set up the bot will take 60 seconds of your time, and in return will save you more than 120 minutes daily.\n\n- Type /help\n\nOr click on the Menu🟰 button in the bottom left corner of the screen, a menu will open with a selection of commands, click help.",
                                 reply_markup=await paginator(id=message.from_user.id, page=0), parse_mode='HTML')
    except:
        if message.from_user.id in ADMIN_ID:
            users = await letter_db.sql_read_users()
            for user in users:
                await letter_db.sql_no_send_command(user[0])
            await message.answer("👋 Hi! \n\n💎 I'm the only official bot EnergyTimeBot✅\n\n🤖 Collected all telegram clickers in one place.\n\n🔋 I will notify you when the energy in your games is 100% ready to collect\n\n🌟 Help you not to miss collecting coins and energy = increase your earnings in games\n\n🕵️ Daily all the latest news on each project (insides/codes/combos)\n\n📃 Instruction on how to set up the bot will take 60 seconds of your time, and in return will save you more than 120 minutes daily.\n\n- Type /help\n\nOr click on the Menu🟰 button in the bottom left corner of the screen, a menu will open with a selection of commands, click help.",
                                 reply_markup=await paginator(id=message.from_user.id, page=0), parse_mode='HTML')
            await message.answer("👋 Приветствую тебя, уважаемый администратор! Тебе доступны следующие команды:\n\n"
                                 "🕹 <b>Добавить новую игру:</b> Возможность добавления игр, путём заполнения некоторых данных (ссылка на игру, название и т.д.)\n\n"
                                 "🗑 <b>Удалить игру:</b> Ты можешь удалить любую устаревшую/неинтересную игру\n\n"
                                 "📬 <b>Рассылка:</b> Возможность разослать сообщение, с привязанной к нему кнопкой, любым пользователям\n\n"
                                 "📊 <b>Статистика:</b> Получение статистики каждого пользователя\n\n"
                                 "📌 <b>Актуальные проекты / Описание:</b> Ты можешь изменять информацию о любой игре",
                                 reply_markup=admin_kb.as_markup(resize_keyboard=True), parse_mode='HTML')
        else:
            await message.answer("👋 Hi! \n\n💎 I'm the only official bot EnergyTimeBot✅\n\n🤖 Collected all telegram clickers in one place.\n\n🔋 I will notify you when the energy in your games is 100% ready to collect\n\n🌟 Help you not to miss collecting coins and energy = increase your earnings in games\n\n🕵️ Daily all the latest news on each project (insides/codes/combos)\n\n📃 Instruction on how to set up the bot will take 60 seconds of your time, and in return will save you more than 120 minutes daily.\n\n- Type /help\n\nOr click on the Menu🟰 button in the bottom left corner of the screen, a menu will open with a selection of commands, click help.",
                                 reply_markup=await paginator(id=message.from_user.id, page=0), parse_mode='HTML')


@dp.message(Command("help"), StateFilter(any_state))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    users = await letter_db.sql_read_users()
    for user in users:
        await letter_db.sql_no_send_command(user[0])
    await message.answer(f"How to use a bot correctly?\n\n✅ In the start message you will have a list of games available to you\nIt is necessary to tick the games you need and press the 'add' button.\n- Done, now in the 'menu' click (button in the lower left corner of the screen) 'Open the list of added games'.\n\n✅ Now you need to select a time to set a timer for each game:\n- Select a game, click on the 'Select Time' button\n- Choose the right time depending on your level and energy recovery rate in a particular game.\n<u>EXAMPLE: in the game 'Hamster Kombat 🐹' the coins are collected every 3 hours.</u>\nAccordingly, you need to select the time '3 hours'\n\n✅ Done, you have set the time!\n- Next, click on the 'open application' button, you will open the application with the game.\n- Collect coins in the game, close the game\n- Next, you need to start the timer, click on the 'Start Time' button.\nDone, the timer is started and you will receive a notification <u>'energy restored  100%'</u> after the selected time.\n\n❗️REMEMBER\nTo make the timer coincide with your time in games 100%, first open the game from the 'open application' button.\n- Then close the game and click on the <b>'Start time'</b> button\n<u>If you do not press the <b>'Start Time'</b> button - the timer will not start!</u>\n\n\n⛔️ To stop the timer manually, press the <b>'Stop Time'</b> button - Stops the active timer.\n\n🕒 Select Timer Time - <b>'Select Time'</b> button - Ability to select and set the desired time for each game.\n\n📲 Open Application: Go to the application itself\n\n📩 To get up-to-date news/insides/codes/combos on games, open the 'menu' and click <b>'Game Info (Insides/Code/Combos)'</b> button\n- Then select the game for which you want to see up-to-date information.\n\n🔇 You can also turn on/off notifications, open the menu and click 'Notifications (on/off)' button.\n\n❌ To delete a previously added game 'favorite games' - open the menu and select 'delete game' /delete , select the game you want to delete.",
                         parse_mode='HTML')


@dp.message(F.text == "Удалить игру", StateFilter(any_state))
async def delete_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
        await message.answer("Выберите игру, которую хотите удалить",
                             reply_markup=await paginator_delete(page=0))
    else:
        await message.answer("Данная команда Вам недоступна!")


@dp.message(Command("delete"), StateFilter(any_state))
async def delete_game_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Select the game you want to uninstall",
                         reply_markup=await paginator_delete_user(id=message.from_user.id, page=0))


@dp.message(F.text == "Добавить новую игру", StateFilter(any_state))
async def link_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
        await state.set_state(NewGame.link)
        await message.answer("Введите ссылку на игру")
    else:
        await message.answer("This command is not available to you!")


@dp.message(F.text == "Рассылка", StateFilter(any_state))
async def newsletter_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
        await message.answer("Напишите сообщение, которое хотите разослать")
        await state.set_state(MessageSend.message)
    else:
        await message.answer("This command is not available to you!")


@dp.message(F.text == "Актуальные проекты / Описание", StateFilter(any_state))
async def info_projects_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
        await message.answer("Выберите игру", reply_markup=await paginator_info(page=0))
    else:
        await message.answer("This command is not available to you!")


@dp.message(Command("info"), StateFilter(any_state))
async def info_games_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
    await message.answer("Select game", reply_markup=await paginator_info(page=0))


@dp.message(Command("notifications"), StateFilter(any_state))
async def newsletter_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
    inline_kb = InlineKeyboardBuilder()
    inline_kb.row(InlineKeyboardButton(text="Turn on notifications", callback_data="on"))
    inline_kb.row(InlineKeyboardButton(text="Turn off notifications", callback_data="off"))
    await message.answer("Select option:", reply_markup=inline_kb.as_markup())
    await state.set_state(MessageSend.message)


@dp.message(F.text == "Статистика", StateFilter(any_state))
async def statistic_command(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
        doc = await users_db.sql_users_stats()
        await message.answer_document(FSInputFile(doc))
    else:
        await message.answer("This command is not available to you!")


@dp.message(F.text.startswith("http"), NewGame.link)
async def link_command(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("Введите название игры")
    await state.set_state(NewGame.name)


@dp.message(NewGame.link)
async def name_command(message: types.Message, state: FSMContext):
    await message.answer("Проверьте ссылку!")
    await state.set_state(NewGame.link)


@dp.message(NewGame.name)
async def energy_command(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите кол-во энергии")
    await state.set_state(NewGame.energy)


@dp.message(NewGame.energy)
async def interval_command(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        try:
            await state.update_data(energy=f"{data['energy']}{message.text};")
        except:
            await state.update_data(energy=f"{message.text};")
        await message.answer("Введите интервал в секундах")
        await state.set_state(NewGame.interval)
    else:
        await message.answer("Введите число!")


@dp.message(NewGame.interval)
async def check_command(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        try:
            await state.update_data(interval=f"{data['interval']}{message.text};")
        except:
            await state.update_data(interval=f"{message.text};")
        inline_kb = InlineKeyboardBuilder()
        inline_kb.add(InlineKeyboardButton(text="Еще", callback_data="more"),
                      InlineKeyboardButton(text="Далее", callback_data="step"))
        await message.answer("Добавить еще или далее?", reply_markup=inline_kb.as_markup())
        await state.set_state(NewGame.interval_energy)
    else:
        await message.answer("Введите число")


@dp.callback_query(F.data == "more", NewGame.interval_energy)
async def interval_and_energy_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.answer("Введите кол-во энергии")
    await state.set_state(NewGame.energy)


@dp.callback_query(F.data == "step", NewGame.interval_energy)
async def step_command(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    check_button = InlineKeyboardBuilder()
    check_button.add(InlineKeyboardButton(text=data['name'], url=data['link']))
    await callback.answer("")
    try:
        await callback.message.edit_text("Введите Да если все верно", reply_markup=check_button.as_markup())
        await state.set_state(NewGame.check)
    except:
        await callback.message.edit_text("Проверьте ссылку и нажмите добавить новую игру!")
        await state.clear()


@dp.message(F.text == "Да", NewGame.check)
async def new_game_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await database.sql_add_command(data)
        await message.answer("Игра добавлена!")
    except:
        await message.answer("Произошла ошибка! Проверьте правильность введенных данных.")
    await state.clear()


@dp.message(Command("games"), StateFilter(any_state))
async def games_command(message: types.Message):
    if message.from_user.id in ADMIN_ID:
        users = await letter_db.sql_read_users()
        for user in users:
            await letter_db.sql_no_send_command(user[0])
    await message.answer("Select game!",
                         reply_markup=await paginator_game(page=0, id=message.from_user.id))


@dp.message(MessageSend.message)
async def button_name_command(message: types.Message, state: FSMContext):
    await state.update_data(message=message.text)
    await message.answer("Enter the button name")
    await state.set_state(MessageSend.button)


@dp.message(MessageSend.button)
async def link_button_command(message: types.Message, state: FSMContext):
    await state.update_data(button=message.text)
    await message.answer("Вставьте ссылку, которая будет привязана к кнопке")
    await state.set_state(MessageSend.link)


@dp.message(MessageSend.link)
async def check_message_command(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()
    button = InlineKeyboardBuilder()
    button.add(types.InlineKeyboardButton(text=data['button'], url=data['link']))
    try:
        await message.answer(f"Проверьте правильность сообщения\n\n{data['message']}\n\n<em>Если все правильно, напишите Да</em>", reply_markup=button.as_markup(), parse_mode='HTML')
        await state.set_state(MessageSend.check)
    except TelegramBadRequest:
        await message.answer("Проверьте ссылку!")
        await state.set_state(MessageSend.link)


@dp.message(F.text == "Да", MessageSend.check)
async def send_message_command(message: types.Message, state: FSMContext):
    await message.answer("Выберите пользователей игр", reply_markup=await paginator_message(page=0))
    await state.set_state(MessageSend.game)


@dp.message(InfoGame.info)
async def text_info_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await database.sql_info_command(message.text, data["game"])
    await message.answer("Отправьте фото(единственное)")
    await state.set_state(InfoGame.photo)


@dp.message(F.photo, InfoGame.photo)
async def photo_info_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    await database.sql_photo_command(photo_id, data["game"])
    await message.answer("Информация об игре изменена")
    await state.clear()


async def paginator_game(id, page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await users_db.sql_read_user(id)
    read = read[5][:-1].split(';')
    for ret in read[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=ret.split(' // ')[0], callback_data=f"menu_{ret.split(' // ')[0]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=PaginationGame(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=PaginationGame(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    return builder.as_markup()


async def paginator(id, page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await database.sql_read()
    check_read = await users_db.sql_read_user(id)
    check_read = re.split(r';| // ', check_read[5])
    for ret in read[start_offset:end_offset]:
        if ret[1] in check_read:
            builder.row(InlineKeyboardButton(text=f"{ret[1]}☑️", callback_data=f"game_{ret[1]}"))
        else:
            builder.row(InlineKeyboardButton(text=ret[1], callback_data=f"game_{ret[1]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=Pagination(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=Pagination(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text="Add games", callback_data="add_game"))
    return builder.as_markup()


async def paginator_message(page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await database.sql_read()
    for ret in read[start_offset:end_offset]:
        percentage = await database.sql_formula_players(ret[1])
        sum = await database.sql_sum_players()
        percent = f"{round(percentage[0] * 100 / sum[0][0], 1)}%"
        builder.row(InlineKeyboardButton(text=f"{ret[1]} - {percent}", callback_data=f"game_{ret[1]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=PaginationMessage(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=PaginationMessage(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text="Отправить", callback_data="send"))
    builder.row(InlineKeyboardButton(text="Завершить", callback_data="end"))
    return builder.as_markup()


async def paginator_delete(page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await database.sql_read()
    for ret in read[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=ret[1], callback_data=f"delete_{ret[1]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=PaginationDelete(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=PaginationDelete(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    return builder.as_markup()


async def paginator_delete_user(id, page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await users_db.sql_read_user(id)
    read = read[5][:-1].split(';')
    for ret in read[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=ret.split(' // ')[0], callback_data=f"userdelete_{ret.split(' // ')[0]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=PaginationDeleteUser(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=PaginationDeleteUser(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    return builder.as_markup()


async def paginator_info(page: int = 0):
    builder = InlineKeyboardBuilder()
    start_offset = page * 10
    limit = 10
    end_offset = start_offset + limit
    read = await database.sql_read()
    for ret in read[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=ret[1], callback_data=f"project_{ret[1]}"))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️", callback_data=PaginationInfo(action="prev", page=page - 1).pack()))
    if end_offset < len(read) and len(read) > 10:
        buttons_row.append(InlineKeyboardButton(text="➡️", callback_data=PaginationInfo(action="next", page=page + 1).pack()))
    builder.row(*buttons_row)
    return builder.as_markup()


@dp.callback_query(PaginationMessage.filter())
async def pagination_message_handler(call: CallbackQuery, callback_data: PaginationMessage):
    page = callback_data.page
    await call.message.edit_reply_markup(reply_markup=await paginator_message(page=page))


@dp.callback_query(PaginationGame.filter())
async def pagination_game_handler(call: CallbackQuery, callback_data: PaginationGame):
    page = callback_data.page
    await call.message.edit_text("Select game:", reply_markup=await paginator_game(page=page, id=call.from_user.id))


@dp.callback_query(Pagination.filter())
async def pagination_handler(call: CallbackQuery, callback_data: Pagination):
    page = callback_data.page
    await call.message.edit_reply_markup(reply_markup=await paginator(id=call.from_user.id, page=page))


@dp.callback_query(PaginationDelete.filter())
async def pagination_delete_handler(call: CallbackQuery, callback_data: PaginationDelete):
    page = callback_data.page
    await call.message.edit_reply_markup(reply_markup=await paginator_delete(page=page))


@dp.callback_query(PaginationDeleteUser.filter())
async def pagination_delete_user_handler(call: CallbackQuery, callback_data: PaginationDeleteUser):
    page = callback_data.page
    await call.message.edit_reply_markup(reply_markup=await paginator_delete_user(id=call.from_user.id, page=page))


@dp.callback_query(PaginationInfo.filter())
async def pagination_info_handler(call: CallbackQuery, callback_data: PaginationInfo):
    page = callback_data.page
    await call.message.delete()
    await call.message.answer(text='Select game:', reply_markup=await paginator_info(page=page))


@dp.callback_query(F.data.startswith("project_"))
async def button_command(callback: types.CallbackQuery):
    await callback.answer("")
    data = callback.data.split('_')[1]
    read = await database.sql_read_game(data)
    if callback.from_user.id in ADMIN_ID:
        inline_kb = InlineKeyboardBuilder()
        inline_kb.row(InlineKeyboardButton(text='Change', callback_data=f"update_{data}"))
        inline_kb.row(InlineKeyboardButton(text="Back", callback_data=PaginationInfo(action="prev", page=0).pack()))
        try:
            await callback.message.delete()
            await callback.message.answer_photo(photo=read[-2], caption=read[-3], reply_markup=inline_kb.as_markup())
        except:
            await callback.message.answer("Нет информации об игре, нажмите Изменить", reply_markup=inline_kb.as_markup())
    else:
        inline_kb = InlineKeyboardBuilder()
        inline_kb.row(InlineKeyboardButton(text="Назад", callback_data=PaginationInfo(action="prev", page=0).pack()))
        try:
            await callback.message.delete()
            await callback.message.answer_photo(photo=read[-2], caption=read[-3], reply_markup=inline_kb.as_markup())
        except:
            await callback.message.answer("There is no information about the game",
                                          reply_markup=inline_kb.as_markup())


@dp.callback_query(F.data.startswith("update_"), StateFilter(any_state))
async def update_game_info_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    data = callback.data.split('_')[1]
    await callback.message.answer("Напишите текст для игры")
    await state.set_state(InfoGame.game)
    await state.update_data(game=data)
    await state.set_state(InfoGame.info)


@dp.callback_query(F.data.startswith("delete_"))
async def delete_command(callback: types.CallbackQuery):
    data = callback.data.split('_')[1]
    await database.sql_delete_task(data)
    read = await users_db.sql_read_users()
    for ret in read:
        games_list = list(ret)
        games = games_list[-1].split(';')
        for game in games:
            if data in game.split(' // ')[0]:
                games.remove(game)
                updated_games = ';'.join(games)
                await users_db.sql_update_game(updated_games, games_list[0])
    await callback.answer(f"Игра {data} удалена!")
    await callback.message.delete()


@dp.callback_query(F.data.startswith("userdelete_"))
async def delete_user_command(callback: types.CallbackQuery):
    data = callback.data.split('_')[1]
    read = await users_db.sql_read_user(callback.from_user.id)
    read = read[-1].split(';')
    for ret in read:
        if data in ret.split(' // ')[0]:
            read.remove(ret)
            updated_games = ';'.join(read)
            await users_db.sql_update_game(updated_games, callback.from_user.id)
    await callback.answer(f"The {data} game has been removed from favorites!")
    await callback.message.delete()


@dp.callback_query(F.data.startswith("game_"))
async def button_command(callback: types.CallbackQuery):
    for button in callback.message.reply_markup.inline_keyboard:
        for text in button:
            if callback.data == text.callback_data and '☑️' not in text.text:
                text.text = text.text + '☑️'
            elif callback.data == text.callback_data and '☑️' in text.text:
                text.text = text.text.replace('☑️', '')
    await callback.message.edit_text(text=callback.message.text, reply_markup=callback.message.reply_markup)


@dp.callback_query(F.data.startswith("send"), MessageSend.game)
async def send_command(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    button = InlineKeyboardBuilder()
    button.add(types.InlineKeyboardButton(text=data['button'], url=data['link']))
    z = 0
    for but in callback.message.reply_markup.inline_keyboard:
        for text in but:
            if '☑️' in text.text:
                z = 1
                users = await letter_db.sql_read_users()
                for user in users:
                    if text.text.split(' - ')[0] in user[2] and user[1] != "yes":
                        await letter_db.sql_send_command(user[0])
                        await bot.send_message(chat_id=user[0], text=data['message'],
                                               reply_markup=button.as_markup(), parse_mode='HTML')
    if z == 0:
        await callback.answer(text="Select game!")
    else:
        await callback.answer(text="Отправлено!")


@dp.callback_query(F.data.startswith("end"), StateFilter(any_state))
async def end_command(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Отправка завершена!")
    await callback.message.delete()
    users = await letter_db.sql_read_users()
    for user in users:
        await letter_db.sql_no_send_command(user[0])


@dp.callback_query(F.data.startswith("menu_"))
async def game_info_command(callback: CallbackQuery):
    await callback.answer('')
    info = callback.data.split('_')
    url_link = await database.sql_read_only(info[1])
    inline_kb = InlineKeyboardBuilder()
    inline_kb.row(InlineKeyboardButton(text="Restart Time", callback_data=f'reset_{info[1]}'))
    inline_kb.add(InlineKeyboardButton(text="Stop Time", callback_data=f'stop_{info[1]}'),
                  InlineKeyboardButton(text="Select Time ✅", callback_data=f"interval_{info[1]}"))
    inline_kb.row(InlineKeyboardButton(text="Open the application", url=url_link[0]))
    inline_kb.row(InlineKeyboardButton(text="Back", callback_data=PaginationGame(action="prev", page=0).pack()))
    await callback.message.edit_text(text="Select option:", reply_markup=inline_kb.as_markup())


@dp.callback_query(F.data.startswith("add_game"))
async def add_game_command(callback: types.CallbackQuery):
    games = ""
    z = 0
    read = await users_db.sql_read_user(callback.from_user.id)
    read = re.split(r';| // ', read[5])
    for button in callback.message.reply_markup.inline_keyboard:
        for text in button:
            if '☑️' in text.text and text.text[:-2] not in read:
                z += 1
                games += f"{text.text.replace('☑️', '')};"
                await database.sql_players_command(text.text[:-2])
    if z == 0:
        await callback.answer(text="Select game!")
    else:
        await users_db.sql_add_game(games, callback.from_user.id)
        await letter_db.sql_add_game(games, callback.from_user.id)
        await callback.answer(text="Games added!")


@dp.callback_query(F.data.startswith("reset_"))
async def timer_command(callback: types.CallbackQuery):
    f = False
    data = callback.data.split("_")[1]
    task_name = f"{callback.from_user.id}_{data}"
    timer = await users_db.sql_read_user(callback.from_user.id)
    timer = timer[5].split(';')
    for time in timer:
        if f"{data} //" in time:
            f = True
            interval = int(time.split(' // ')[2])
            timer = interval
            task = asyncio.create_task(auto_message_command(callback.from_user.id, timer, data))
            tasks[task_name] = task
            break
    if f is True:
        await callback.answer("The timer has started!")
        await users_db.sql_timer_command(callback.from_user.id)
    else:
        await callback.answer("Select Time!")


@dp.callback_query(F.data.startswith("stop_"))
async def stop_timer_command(callback: types.CallbackQuery):
    data = callback.data.split("_")[1]
    task_name = f"{callback.from_user.id}_{data}"
    task = tasks.get(task_name)
    if task:
        task.cancel()
        del tasks[task_name]
    await callback.answer("Timer stopped!")


@dp.callback_query(F.data.startswith("interval_"))
async def timer_command(callback: types.CallbackQuery):
    await callback.answer("")
    data = callback.data.split("_")[1]
    read = await database.sql_read_game(data)
    energy = read[2].split(";")
    interval = read[3].split(";")
    inline_kb = InlineKeyboardBuilder()
    for i in range(len(energy) - 1):
        if int(interval[i]) < 60:
            inline_kb.row(InlineKeyboardButton(text=f"{interval[i]} sec",
                                               callback_data=f"energy_{data}_{energy[i]}_{interval[i]}"))
        else:
            button = humanize.precisedelta(datetime.timedelta(seconds=int(interval[i]))).replace('seconds', 'sec')
            inline_kb.row(InlineKeyboardButton(text=f"{button}",
                                               callback_data=f"energy_{data}_{energy[i]}_{interval[i]}"))
    inline_kb.row(InlineKeyboardButton(text="Cancel", callback_data="cancel_message"))
    await callback.message.answer("choose your preferred option:",
                                  reply_markup=inline_kb.as_markup())


@dp.callback_query(F.data.startswith("cancel_message"))
async def cancel_message_command(callback: types.CallbackQuery):
    await callback.answer("")
    await callback.message.delete()


@dp.callback_query(F.data.startswith("energy_"))
async def energy_interval_command(callback: types.CallbackQuery):
    await callback.answer("")
    data = callback.data.split('_')
    read = await users_db.sql_read_user(callback.from_user.id)
    read_game = read[5].split(';')
    for ret in range(len(read_game)):
        if data[1] == read_game[ret].split(' // ')[0]:
            read_game[ret] = f"{data[1]} // {data[2]} // {data[3]}"
    game = ';'.join(read_game)
    await users_db.sql_update_game(game, callback.from_user.id)
    await callback.message.delete()


async def auto_message_command(chat_id: int, time: int, data: str):
    read = await users_db.sql_read_user(chat_id)
    if read[4] == "on":
        try:
            await asyncio.sleep(time)
            await bot.send_message(chat_id=chat_id, text=f"The energy in {data} has been restored!")
            await users_db.sql_notifications_command(chat_id)
        except asyncio.CancelledError:
            return


@dp.callback_query(F.data.startswith("on"))
async def notifications_on_command(callback: types.CallbackQuery):
    await callback.answer("Notifications are enabled!")
    await callback.message.delete()
    await users_db.sql_notifications_on(callback.from_user.id)


@dp.callback_query(F.data.startswith("off"))
async def notifications_off_command(callback: types.CallbackQuery):
    await callback.answer("Notifications are disabled!")
    await callback.message.delete()
    await users_db.sql_notifications_off(callback.from_user.id)


async def main():
    database.sql_start()
    users_db.users_sql_start()
    letter_db.letter_sql_start()
    bot = Bot(TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
