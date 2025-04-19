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
import shlex

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
    await callback.message.answer(
        "Введите данные о событии по шаблону:\n\n"
        '/добавить дд.мм.гггг чч:мм "Город с пробелами" "Тип события" "Место с пробелами" "Описание с пробелами"'
    )
    await callback.answer()

@dp.message(Command("добавить"))
async def quick_add_event(message: Message):
    try:
        parts = shlex.split(message.text)
        if len(parts) < 7:
            raise ValueError
        _, date_str, time_str, *rest = parts
        city, ev_type, place, description = rest
    except ValueError:
        return await message.answer(
            "❗️Неверный формат.\nИспользуйте шаблон:\n"
            '/добавить дд.мм.гггг чч:мм "Город с пробелами" "Тип события" "Место с пробелами" "Описание с пробелами"'
        )

    if not is_valid_date(date_str):
        return await message.answer("❗ Неверная дата. Формат: дд.мм.гггг")
    if not is_valid_time(time_str):
        return await message.answer("❗ Неверное время. Формат: чч:мм")

    chat_id = str(message.chat.id)
    data = load_data()
    if chat_id not in data:
        data[chat_id] = []
    data[chat_id].append({
        "date": date_str,
        "time": time_str,
        "city": city,
        "type": ev_type,
        "place": place,
        "description": description
    })
    save_data(data)

    await message.answer("✅ Событие добавлено!")

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

@dp.callback_query(F.data == "list_events")
async def cb_list_events(callback: CallbackQuery):
    chat_id = str(callback.message.chat.id)
    now = datetime.now()
    data = load_data()
    events = data.get(chat_id, [])

    if not events:
        await callback.message.answer("📭 Список событий пуст.")
        await callback.answer()
        return

    def parse_datetime(e):
        return datetime.strptime(f"{e['date']} {e['time']}", "%d.%m.%Y %H:%M")

    events.sort(key=parse_datetime)

    text = "<b>📅 Список событий:</b>\n\n"
    for ev in events:
        dt = parse_datetime(ev)
        block = (
            f"📅 <b>{ev['date']} {ev['time']}</b>\n"
            f"🏷 {ev['type']} в {ev['city']}\n"
            f"🏛 {ev['place']}\n"
            f"📝 {ev['description']}\n"
        )
        if dt < now:
            block = f"<i><span class='tg-spoiler'>{block}</span></i>"
        text += block + "\n"

    await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "delete_event")
async def cb_delete(callback: CallbackQuery):
    await callback.message.answer("🗑 Вы нажали: Удалить событие")
    await callback.answer()

# === Запуск ===
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))