from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import asyncio
import os

# Токен от BotFather
TOKEN = os.getenv('TOKEN', 'TOKEN')

print(f"🔑 Токен: {TOKEN[:20]}...")
print("🤖 Запуск бота...")

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Курс юаня
YUAN_RATE = 11.2

# Клавиатура с кнопками (ИСПРАВЛЕНО для aiogram 3.x!)
def get_category_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='👟 Кроссовки', callback_data='sneakers')],
        [InlineKeyboardButton(text='👜 Сумка', callback_data='bag')],
        [InlineKeyboardButton(text='⌚ Часы', callback_data='watch')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработчик /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    print(f"📩 /start от {message.from_user.username}")
    await message.answer(
        '👋 Привет! Я бот-калькулятор.\n\n'
        'Введи цену в юанях, я рассчитаю стоимость в рублях.\n\n'
        'Или выбери категорию:',
        reply_markup=get_category_keyboard()
    )
    print("✅ Ответ отправлен")

# Обработчик текста (числа)
@dp.message(lambda message: message.text and message.text.replace('.', '').isdigit())
async def calculate_price(message: types.Message):
    try:
        price = float(message.text)
        result = price * YUAN_RATE + 1350 + 1500
        print(f"🧮 {price} юаней = {result}₽")
        await message.answer(
            f'💰 Расчёт:\n'
            f'{price} × {YUAN_RATE} + 1350 + 1500 = **{result:.0f}₽**\n\n'
            'Введи другую цену или нажми /start',
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await message.answer('❌ Введи корректное число')

# Обработчик кнопок
@dp.callback_query(lambda callback: callback.data)
async def category_selected(callback: types.CallbackQuery):
    category = callback.data
    delivery = {
        'sneakers': 1350,
        'bag': 850,
        'watch': 500
    }
    names = {
        'sneakers': '👟 Кроссовки',
        'bag': '👜 Сумка',
        'watch': '⌚ Часы'
    }
    
    print(f"🔘 Категория: {category}")
    
    await callback.message.answer(
        f'Выбрано: {names[category]}\n'
        f'Доставка: {delivery[category]}₽\n\n'
        f'Введи цену товара в юанях (курс: {YUAN_RATE}₽):'
    )
    await callback.answer()

# Запуск
async def main():
    print("✅ Бот запущен! Ожидание сообщений...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

 # Для Render
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))

# В main() добавь:
async def main():
    print("✅ Бот запущен!")
    threading.Thread(target=run_flask, daemon=True).start()
    await dp.start_polling(bot)

app = Flask(__name__)
@app.route('/')
def home():
    return '''
    <h1>🤖 Telegram Bot is Running!</h1>
    <p>Бот работает 24/7 на Render</p>
    <p><a href="https://t.me/Kroso_bot">Открыть бота в Telegram</a></p>
    '''

@app.route('/health')
def health():
    return 'ОК', 200

def run_flask():
    port = int(os.getenv('PORT', 8000))
    print(f"🌐 Flask запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    bot_thread = Thread(target=lambda: asyncio.run(run.bot()), daemon=True)
    bot_thread.start()

    run_flask()