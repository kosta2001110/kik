from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import asyncio
import os

# TOKEN
TOKEN = os.getenv('TOKEN')
print(f"🔑 Токен: {TOKEN[:20] if TOKEN else 'NOT SET'}...")

# Инициализация (aiogram 2.x)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)  # ← Передаём bot!
YUAN_RATE = 11.2

def get_category_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='👟 Кроссовки', callback_data='sneakers')],
        [InlineKeyboardButton(text='👜 Сумка', callback_data='bag')],
        [InlineKeyboardButton(text='⌚ Часы', callback_data='watch')]
    ]
    return InlineKeyboardMarkup(row_width=1)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    print(f"📩 /start от {message.from_user.username}")
    await message.answer(
        '👋 Привет! Я бот-калькулятор.\n\n'
        'Введи цену в юанях, я рассчитаю стоимость в рублях.\n\n'
        'Или выбери категорию:',
        reply_markup=get_category_keyboard()
    )

@dp.message_handler(lambda message: message.text and message.text.replace('.', '').isdigit())
async def calculate_price(message: types.Message):
    try:
        price = float(message.text)
        result = price * YUAN_RATE + 1350 + 1500
        print(f"🧮 {price} юаней = {result}₽")
        await message.answer(
            f'💰 Расчёт:\n{price} × {YUAN_RATE} + 1350 + 1500 = **{result:.0f}₽**\n\n'
            'Введи другую цену или нажми /start',
            parse_mode='Markdown'
        )
    except:
        await message.answer('❌ Введи корректное число (например: 214)')

@dp.callback_query_handler()
async def category_selected(callback: types.CallbackQuery):
    category = callback.data
    delivery = {'sneakers': 1350, 'bag': 850, 'watch': 500}
    names = {'sneakers': '👟 Кроссовки', 'bag': '👜 Сумка', 'watch': '⌚ Часы'}
    
    print(f"🔘 Категория: {category}")
    await callback.message.answer(
        f'Выбрано: {names[category]}\n'
        f'Доставка: {delivery[category]}₽\n\n'
        f'Введи цену товара в юанях (курс: {YUAN_RATE}₽):'
    )
    await callback.answer()

async def run_bot():
    print("✅ Бот запущен! Ожидание сообщений...")
    await dp.start_polling()

# FLASK СЕРВЕР
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>🤖 Telegram Bot is Running!</h1><p>Бот работает 24/7 на Render</p>'

@app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    port = int(os.getenv('PORT', 8000))
    print(f"🌐 Flask запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)

# ЗАПУСК
if __name__ == '__main__':
    bot_thread = Thread(target=lambda: asyncio.run(run_bot()), daemon=True)
    bot_thread.start()
    run_flask()