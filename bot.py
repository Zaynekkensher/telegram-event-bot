from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import re
import json
from datetime import datetime
import os
import shlex
from event_db import add_event, get_events, delete_event
import asyncio

if not os.getenv("BOT_TOKEN"):
    raise RuntimeError("❌ Переменная окружения BOT_TOKEN не задана")

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    sent_menu = await message.answer("Привет! Выберите действие (сообщения будут удалены через 10 секунд):", reply_markup=main_menu())
    await asyncio.sleep(10)
    await sent_menu.delete()
    await message.delete()

# === Заглушки для кнопок ===
@dp.callback_query(F.data == "add_event")
async def cb_add_event(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.answer(
        "Введите данные о событии по шаблону:\n\n"
        '/добавить дд.мм.гггг чч:мм "Город с пробелами" "Тип события" "Место с пробелами" "Описание с пробелами"'
    )
    await asyncio.sleep(10)
    await msg.delete()
    await callback.message.delete()

@dp.message(Command("добавить"))
async def quick_add_event(message: Message):
    try:
        parts = shlex.split(message.text)
        if len(parts) < 7:
            raise ValueError
        _, date_str, time_str, *rest = parts
        city, ev_type, place, description = rest
    except ValueError:
        msg = await message.answer(
            "❗️Неверный формат.\nИспользуйте шаблон:\n"
            '/добавить дд.мм.гггг чч:мм "Город с пробелами" "Тип события" "Место с пробелами" "Описание с пробелами"'
        )
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()
        return

    if not is_valid_date(date_str):
        msg = await message.answer("❗ Неверная дата. Формат: дд.мм.гггг")
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()
        return
    if not is_valid_time(time_str):
        msg = await message.answer("❗ Неверное время. Формат: чч:мм")
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()
        return

    try:
        await add_event(
            message.chat.id, date_str, time_str, city, ev_type, place, description
        )
        msg = await message.answer("✅ Событие добавлено!")
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()
    except Exception as e:
        msg = await message.answer(f"⚠ Ошибка при добавлении события: {e}")
        await asyncio.sleep(10)
        await msg.delete()
        await message.delete()

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        return True
    except:
        return False

def is_valid_time(time_str):
    return bool(re.fullmatch(r"\d{2}:\d{2}", time_str)) and \
           0 <= int(time_str[:2]) < 24 and 0 <= int(time_str[3:]) < 60

@dp.callback_query(F.data == "list_events")
async def cb_list_events(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    now = datetime.now()
    events = await get_events(callback.message.chat.id)

    if not events:
        msg = await callback.message.answer("📭 Список событий пуст.")
        await asyncio.sleep(10)
        await msg.delete()
        await callback.message.delete()
        await callback.answer()
        return

    text = "<b>📅 Список событий:</b>\n\n"
    for ev in events:
        dt = datetime.strptime(f"{ev['date']} {ev['time']}", "%d.%m.%Y %H:%M")
        block = (
            f"{ev['id']}. 📅 <b>{ev['date']} {ev['time']}</b>\n"
            f"🏷 {ev['type']} {ev['city']}\n"
            f"🏛 {ev['place']}\n"
            f"📝 {ev['description']}\n"
        )
        if dt < now:
            block = f"<i><span class='tg-spoiler'>{block}</span></i>"
        text += block + "\n"

    sent = await callback.message.answer(text)
    await asyncio.sleep(10)
    await sent.delete()
    await callback.answer()

@dp.callback_query(F.data == "delete_event")
async def cb_delete(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    events = await get_events(chat_id)

    if not events:
        msg = await callback.message.answer("📭 Список событий пуст.")
        await asyncio.sleep(10)
        await msg.delete()
        await callback.message.delete()
        await callback.answer()
        return

    keyboard = []
    for ev in events:
        button = InlineKeyboardButton(
            text=f"❌ Удалить: {ev['id']} {ev['date']} {ev['time']} {ev['type']} {ev['city']}",
            callback_data=f"delete_{ev['id']}"
        )
        keyboard.append([button])

    prompt_msg = await callback.message.answer("Выберите событие для удаления:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await asyncio.sleep(10)
    await prompt_msg.delete()
    await callback.message.delete()

@dp.message()
async def delete_by_number(message: Message):
    if not message.text.isdigit():
        return

    event_id = int(message.text)
    await delete_event(message.chat.id, event_id)
    msg = await message.answer("✅ Событие удалено.")
    await asyncio.sleep(10)
    await msg.delete()
    await message.delete()

@dp.callback_query(F.data.startswith("delete_"))
async def handle_delete_callback(callback: CallbackQuery):
    try:
        event_id = int(callback.data.split("_")[1])
        await delete_event(callback.message.chat.id, event_id)
        msg = await callback.message.answer("🗑 Событие удалено.")
        await asyncio.sleep(10)
        await msg.delete()
        await callback.message.delete()
    except Exception as e:
        msg = await callback.message.answer(f"⚠ Ошибка при удалении: {e}")
        await asyncio.sleep(10)
        await msg.delete()
        await callback.answer()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))