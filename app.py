from flask import Flask, render_template_string, request
import os
import requests

app = Flask(__name__)

# URL вебхука (ЗАМЕНИ НА СВОЙ!)
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# Главная страница
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Мой Сайт</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #121212;
                    color: white;
                    text-align: center;
                    padding: 50px 20px;
                }
                h1 {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 20px;
                    color: #aaa;
                }
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
                .service h2 {
                    color: #7289da;
                    margin-bottom: 10px;
                }
                .service .price {
                    font-size: 24px;
                    font-weight: bold;
                    color: #43b581;
                    margin: 10px 0;
                }
                .service .price::before {
                    content: "₽";
                    font-size: 16px;
                    color: #aaa;
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
                .order-form h2 {
                    color: #7289da;
                    margin-bottom: 20px;
                }
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
                .order-form button:hover {
                    background: #4752c4;
                }
                .success {
                    color: #43b581;
                    font-size: 18px;
                    margin-top: 15px;
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
    
    # Отправка в Discord через вебхук
    payload = {
        "content": f"⚠ НОВЫЙ ЗАКАЗ!\nИмя: {name}\nПочта: {email}\nТелефон: {phone}\nУслуга: {service}"
    }
    requests.post(WEBHOOK_URL, json=payload)
    
    # Вывод в консоль (для проверки)
    print(f"\n⚠ НОВЫЙ ЗАКАЗ!")
    print(f"Имя: {name}")
    print(f"Почта: {email}")
    print(f"Телефон: {phone}")
    print(f"Услуга: {service}\n")
    
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
                h1 {
                    color: #43b581;
                }
                p {
                    font-size: 20px;
                    color: #aaa;
                }
                a {
                    color: #5865f2;
                    text-decoration: none;
                }
            </style>
        </head>
        <body>
            <h1>✅ Заявка отправлена!</h1>
            <p>Свяжусь с тобой в ближайшее время</p>
            <p><a href="/">← Вернуться на главную</a></p>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)