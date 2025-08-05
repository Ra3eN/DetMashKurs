# main.py
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Токен из @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Хранение прогресса в JSON
DATA_FILE = "user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

STEPS = [
    "start", "drive_type", "input_data",
    "motor_selection", "kinematic_calc", "gear_calc",
    "shaft_calc", "bearing_calc", "assembly",
    "report", "drawings", "complete"
]

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"step": "start", "info": {}}
        save_data(data)
        await message.answer(
            "👋 Привет! Я — помощник по курсовому проекту по *деталям машин*.\n"
            "Нажми /begin, чтобы начать.",
            parse_mode="Markdown"
        )
    else:
        step = data[user_id]["step"]
        await resume(message, step)

async def resume(message: types.Message, step: str):
    titles = {
        "drive_type": "Выбор типа привода",
        "input_data": "Ввод данных",
        "motor_selection": "Подбор двигателя",
        # ... добавь остальные
    }
    current = titles.get(step, step)
    await message.answer(
        f"С возвращением! Ты остановился на: *{current}*\n"
        "Нажми /begin, чтобы продолжить.",
        parse_mode="Markdown"
    )

@dp.message(Command("begin"))
async def begin(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()
    step = data.get(user_id, {}).get("step", "start")

    descriptions = {
        "drive_type": "🏭 Выбери тип привода: ленточный или цепной",
        "input_data": "📊 Введи: P = ... кВт, n = ... об/мин",
        "motor_selection": "🔌 Подбираем двигатель...",
        "complete": "🎉 Проект завершён!"
    }

    text = descriptions.get(step, "Шаг в разработке")
    data[user_id]["step"] = STEPS[(STEPS.index(step) + 1) % len(STEPS)]
    save_data(data)
    await message.answer(text)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())