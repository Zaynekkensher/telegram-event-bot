from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import re
import json
from datetime import datetime
import os

# === 🔐 Вставь сюда свой токен от BotFather ===
BOT_TOKEN = "7882211754:AAEHyH5kpQoFNWVtQrc7cu-3512uwsJaEMc"

# === Инициализация ===
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# === FSM группа для добавления события ===
class AddEvent(StatesGroup):
    date = State()
    time = State()
    city = State()
    type = State()
    place = State()
    description = State()

# === Главное меню ===
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить событие", callback_data="add_event")],
        [InlineKeyboardButton(text="📋 Список событий", callback_data="list_events")],
        [InlineKeyboardButton(text="🗑 Удалить событие", callback_data="delete_event")],
    ])

# === /start ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu())

# === Заглушки для кнопок ===
@dp.callback_query(F.data == "add_event")
async def cb_add_event(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите дату события (дд.мм.гггг):")
    await state.set_state(AddEvent.date)
    await callback.answer()

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except:
        return False

def is_valid_time(time_str):
    return bool(re.fullmatch(r"\d{2}:\d{2}", time_str)) and \
           0 <= int(time_str[:2]) < 24 and 0 <= int(time_str[3:]) < 60

def load_data():
    if not os.path.exists("data.json"):
        return {}
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@dp.message(AddEvent.date)
async def step_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Неверный формат. Введите дату в формате дд.мм.гггг:")
        return
    await state.update_data(date=message.text)
    await message.answer("Введите время события (чч:мм):")
    await state.set_state(AddEvent.time)

@dp.message(AddEvent.time)
async def step_time(message: Message, state: FSMContext):
    if not is_valid_time(message.text):
        await message.answer("❌ Неверный формат. Введите время в формате чч:мм:")
        return
    await state.update_data(time=message.text)
    await message.answer("Введите город события:")
    await state.set_state(AddEvent.city)

@dp.message(AddEvent.city)
async def step_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введите тип события:")
    await state.set_state(AddEvent.type)

@dp.message(AddEvent.type)
async def step_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("Введите место события (можно пропустить):")
    await state.set_state(AddEvent.place)

@dp.message(AddEvent.place)
async def step_place(message: Message, state: FSMContext):
    await state.update_data(place=message.text)
    await message.answer("Введите описание события (можно пропустить):")
    await state.set_state(AddEvent.description)

@dp.message(AddEvent.description)
async def step_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    user_data = await state.get_data()
    chat_id = str(message.chat.id)

    data = load_data()
    if chat_id not in data:
        data[chat_id] = []
    data[chat_id].append(user_data)
    save_data(data)

    await message.answer("✅ Событие добавлено!")
    await state.clear()

@dp.callback_query(F.data == "list_events")
async def cb_list(callback: CallbackQuery):
    await callback.message.answer("📋 Вы нажали: Список событий")
    await callback.answer()

@dp.callback_query(F.data == "delete_event")
async def cb_delete(callback: CallbackQuery):
    await callback.message.answer("🗑 Вы нажали: Удалить событие")
    await callback.answer()

# === Запуск ===
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))