from flask import Flask, render_template_string, request, redirect, url_for
import os
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# URL вебхука
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), default='Не указан')
    service = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.name}>'

# Создаём базу данных
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Мой сайт</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #121212;
                    color: white;
                    text-align: center;
                    padding: 50px 20px;
                }
                h1 { font-size: 48px; margin-bottom: 20px; }
                p { font-size: 20px; color: #aaa; }
                .services {
                    margin-top: 30px;
                    display: flex;
                    justify-content: center;
                    gap: 30px;
                    flex-wrap: wrap;
                }
                .service {
                    background: #1e1e1e;
                    padding: 25px;
                    border-radius: 10px;
                    width: 220px;
                    cursor: pointer;
                }
                .service h2 { color: #7289da; margin-bottom: 10px; }
                .service .price {
                    font-size: 24px;
                    font-weight: bold;
                    color: #43b581;
                    margin: 10px 0;
                }
                .order-form {
                    background: #1e1e1e;
                    padding: 40px;
                    border-radius: 10px;
                    margin-top: 50px;
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                }
                .order-form h2 { color: #7289da; margin-bottom: 20px; }
                .order-form input,
                .order-form textarea {
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: none;
                    border-radius: 5px;
                    background: #2a2a2a;
                    color: white;
                    font-size: 16px;
                }
                .order-form button {
                    width: 100%;
                    padding: 15px;
                    background: #5865f2;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 18px;
                    cursor: pointer;
                    margin-top: 15px;
                }
                .order-form button:hover { background: #4752c4; }
                .success { color: #43b581; font-size: 18px; margin-top: 15px; }
                .admin-link {
                    margin-top: 50px;
                    color: #aaa;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <h1>Привет, я Милкес</h1>
            <p>Делаю ботов и сайты на заказ</p>
            
            <div class="services">
                <div class="service">
                    <h2>Бот для Discord</h2>
                    <div class="price">3000</div>
                    <p>Модерация, игры, уведомления</p>
                </div>
                <div class="service">
                    <h2>Парсер данных</h2>
                    <div class="price">5000</div>
                    <p>Сбор информации с сайтов</p>
                </div>
                <div class="service">
                    <h2>Сайт-визитка</h2>
                    <div class="price">10000</div>
                    <p>Простой сайт для бизнеса</p>
                </div>
            </div>
            
            <div class="order-form">
                <h2>Оставить заявку</h2>
                <form method="POST" action="/order">
                    <input type="text" name="name" placeholder="Ваше имя" required>
                    <input type="email" name="email" placeholder="Ваша почта" required>
                    <input type="tel" name="phone" placeholder="Телефон (Не обязательно)">
                    <textarea name="service" placeholder="Какая услуга нужна?" rows="4" required></textarea>
                    <button type="submit">Отправить заявку</button>
                </form>
                {% if success %}
                <div class="success">✅ Заявка отправлена! Свяжусь с тобой в ближайшее время.</div>
                {% endif %}
            </div>
            
            <a href="/admin" class="admin-link">Админ-панель</a>
        </body>
        </html>
    ''')

# Обработка заказа
@app.route('/order', methods=['POST'])
def order():
    name = request.form['name']
    email = request.form['email']
    phone = request.form.get('phone', 'Не указан')
    service = request.form['service']
    
    # Сохраняем в базу данных
    new_order = Order(name=name, email=email, phone=phone, service=service)
    db.session.add(new_order)
    db.session.commit()
    
    # Отправка в Discord
    if WEBHOOK_URL:
        payload = {
            "content": f"⚠ НОВЫЙ ЗАКАЗ!\nИмя: {name}\nПочта: {email}\nТелефон: {phone}\nУслуга: {service}"
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except:
            print("❌ Не удалось отправить в Discord")
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Заявка отправлена</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #121212;
                    color: white;
                    text-align: center;
                    padding: 100px 20px;
                }
                h1 { color: #43b581; }
                p { font-size: 20px; color: #aaa; }
                a { color: #5865f2; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>✅ Заявка отправлена!</h1>
            <p>Свяжусь с тобой в ближайшее время</p>
            <p><a href="/">← Вернуться на главную</a></p>
        </body>
        </html>
    ''')

# Админ-панель
@app.route('/admin')
def admin():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Админ-панель</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #121212;
                    color: white;
                    padding: 20px;
                }
                h1 { color: #7289da; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    border: 1px solid #333;
                    padding: 12px;
                    text-align: left;
                }
                th { background: #1e1e1e; color: #7289da; }
                tr:nth-child(even) { background: #1a1a1a; }
                .back { color: #5865f2; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>📋 Все заказы</h1>
            <a href="/" class="back">← На главную</a>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Почта</th>
                    <th>Телефон</th>
                    <th>Услуга</th>
                    <th>Дата</th>
                </tr>
                {% for order in orders %}
                <tr>
                    <td>{{ order.id }}</td>
                    <td>{{ order.name }}</td>
                    <td>{{ order.email }}</td>
                    <td>{{ order.phone }}</td>
                    <td>{{ order.service }}</td>
                    <td>{{ order.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
    ''', orders=orders)

# ============================================
# === TELEGRAM БОТ ===
# ============================================

TOKEN = os.getenv('TOKEN', '8529982995:AAEWg7v34cLxgKbDtTLY9ZUI2mRpxsTnfUE')

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Курс юаня
YUAN_RATE = 11.2

# Клавиатура
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

# Обработчик чисел
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
        await message.answer('❌ Введи корректное число (например: 214)')

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

# Запуск бота
async def run_bot():
    print("🤖 Запуск Telegram бота...")
    await dp.start_polling(bot)

def start_bot():
    asyncio.run(run_bot())

# ============================================
# === ЗАПУСК ПРИЛОЖЕНИЯ ===
# ============================================

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    print("🚀 Запуск приложения...")
    bot_thread = Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.getenv('PORT', 8000))
    print(f"🌐 Сайт запускается на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)