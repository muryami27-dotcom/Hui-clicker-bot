import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
import uvicorn

# Настройки
API_TOKEN = '8599791383:AAEsRQH703tRv567ytDTecBHgjbop5ItBYg'  # Сюда твой токен от BotFather
logging.basicConfig(level=logging.INFO)

# Инициализация Бота и Сервера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()
handler = app

# Разрешаем сайту на Гитхабе слать данные на наш сервер без блокировок
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Наша база данных в памяти сервера
user_clicks = {}

def get_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text='ОТКРЫТЬ КЛИКЕР 🍆', 
            web_app=WebAppInfo(url='https://muryami27-dotcom.github.io/tg_bot_HuiSosanie/') # Сюда твою ссылку на сайт
        )]]
    )

reply_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Топ лидеров 🏆')]], resize_keyboard=True)

@dp.message(CommandStart())
async def send_welcome(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in user_clicks:
        user_clicks[user_id] = {"name": message.from_user.first_name, "clicks": 0}
    await message.reply("Привет! Любишь сосать? Скорее тыкай на кнопку ниже!💦", reply_markup=get_inline_keyboard())
    await message.answer("А здесь ты можешь посмотреть результаты сосания:", reply_markup=reply_keyboard)

@dp.message(F.text.contains("Топ"))
async def show_top(message: Message):
    if not user_clicks:
        await message.answer("В топе пока никого нет. Будь первым! 💦")
        return
    sorted_users = sorted(user_clicks.items(), key=lambda item: item[1]["clicks"], reverse=True)
    top_text = "🏆 ТОП-ЛИДЕРОВ ПО СОСАНИЮ 🏆\n\n"
    for index, (uid, data) in enumerate(sorted_users[:10], start=1):
        top_text += f"{index}. {data['name']} — {data['clicks']} 🍆\n"
    await message.answer(top_text, parse_mode="Markdown")

# --- ВОТ ЭТОТ ОБНОВЛЕННЫЙ КУСОЧЕК ДЛЯ ПАЧЕК КЛИКОВ ---

# API СЕРВЕРА: Принимает пачку кликов каждые 2 секунды
@app.post("/click")
async def handle_click(request: Request):
    data = await request.json()
    user_id = str(data.get("user_id"))
    name = data.get("name", "Аноним")
    count = int(data.get("count", 1)) # Получаем количество кликов в пачке
    
    if user_id not in user_clicks:
        user_clicks[user_id] = {"name": name, "clicks": 0}
    
    user_clicks[user_id]["clicks"] += count
    return {"status": "success"}

# API СЕРВЕРА: Отдает текущий баланс при открытии игры
@app.get("/get_score")
async def get_score(user_id: str):
    if user_id in user_clicks:
        return {"clicks": user_clicks[user_id]["clicks"]}
    return {"clicks": 0}

# --------------------------------------------------

# Запуск бота в фоновом режиме внутри сервера
async def run_bot():
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
