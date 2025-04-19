from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.enums import ParseMode
import asyncio

# === 🔐 Вставь сюда свой токен от BotFather ===
BOT_TOKEN = "7882211754:AAEHyH5kpQoFNWVtQrc7cu-3512uwsJaEMc"

# === Инициализация ===
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

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
async def cb_add(callback: CallbackQuery):
    await callback.message.answer("🟡 Вы нажали: Добавить событие")
    await callback.answer()

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