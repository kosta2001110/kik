from flask import Flask, render_template_string, request, jsonify
import os
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Discord вебхук
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)  # TG/Discord
    email = db.Column(db.String(100))
    service = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Отправка в Discord
def send_discord(order):
    if not WEBHOOK_URL:
        print("⚠️ DISCORD_WEBHOOK_URL не задан")
        return
    
    embed = {
        "title": "🛒 Новый заказ!",
        "color": 5865922,  # Discord blurple
        "fields": [
            {"name": "👤 Имя", "value": order.name, "inline": True},
            {"name": "💬 Контакты", "value": order.contact, "inline": True},
            {"name": "📧 Email", "value": order.email or "Не указан", "inline": True},
            {"name": "📦 Услуга", "value": order.service, "inline": False},
            {"name": "🕐 Время", "value": order.created_at.strftime('%d.%m.%Y %H:%M'), "inline": True}
        ],
        "footer": {"text": "Заказ с сайта"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        print(f"✅ Discord уведомление отправлено для {order.name}")
    except Exception as e:
        print(f"❌ Ошибка отправки в Discord: {e}")

# Главная страница
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Мои Услуги</title>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: #121212;
                    color: #eee;
                    padding: 20px;
                    line-height: 1.6;
                }
                .container { max-width: 1000px; margin: 0 auto; }
                h1 {
                    text-align: center;
                    font-size: 42px;
                    color: #7289da;
                    margin: 30px 0 10px;
                }
                .subtitle {
                    text-align: center;
                    color: #aaa;
                    font-size: 18px;
                    margin-bottom: 40px;
                }
                
                /* Карточки услуг */
                .services {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                    gap: 25px;
                    margin: 40px 0;
                }
                .service-card {
                    background: #1e1e1e;
                    padding: 25px;
                    border-radius: 12px;
                    border: 2px solid #2a2a2a;
                    transition: border-color 0.3s;
                    text-align: center;
                }
                .service-card:hover { border-color: #7289da; }
                .service-card h3 {
                    color: #7289da;
                    font-size: 22px;
                    margin-bottom: 12px;
                }
                .service-card p { color: #aaa; margin: 10px 0; }
                .price {
                    font-size: 28px;
                    font-weight: bold;
                    color: #43b581;
                    margin: 15px 0;
                }
                .order-btn {
                    background: #5865f2;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background 0.3s;
                }
                .order-btn:hover { background: #4752c4; }
                
                /* Модальное окно */
                .modal {
                    display: none;
                    position: fixed;
                    top: 0; left: 0;
                    width: 100%; height: 100%;
                    background: rgba(0,0,0,0.85);
                    z-index: 1000;
                    align-items: center;
                    justify-content: center;
                }
                .modal.active { display: flex; }
                .modal-content {
                    background: #1e1e1e;
                    padding: 30px;
                    border-radius: 12px;
                    width: 90%;
                    max-width: 450px;
                    border: 2px solid #7289da;
                    position: relative;
                }
                .close {
                    position: absolute;
                    top: 12px; right: 20px;
                    font-size: 28px;
                    cursor: pointer;
                    color: #aaa;
                }
                .close:hover { color: #fff; }
                .modal h2 {
                    color: #7289da;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .modal input {
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: 1px solid #333;
                    border-radius: 6px;
                    background: #2a2a2a;
                    color: #fff;
                    font-size: 15px;
                }
                .modal input:focus {
                    outline: none;
                    border-color: #7289da;
                }
                .submit-btn {
                    width: 100%;
                    padding: 14px;
                    background: #43b581;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    margin-top: 15px;
                    transition: background 0.3s;
                }
                .submit-btn:hover { background: #3ba571; }
                .success-msg {
                    text-align: center;
                    color: #43b581;
                    margin-top: 15px;
                    display: none;
                }
                
                /* Админ ссылка */
                .admin-link {
                    display: block;
                    text-align: center;
                    margin-top: 50px;
                    color: #7289da;
                    text-decoration: none;
                }
                .admin-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Мои Услуги</h1>
                <p class="subtitle">Делаю ботов и сайты на заказ</p>
                
                <div class="services">
                    <div class="service-card">
                        <h3>🤖 Discord Бот</h3>
                        <p>Модерация, игры, уведомления</p>
                        <div class="price">3 000₽</div>
                        <button class="order-btn" onclick="openModal('Discord Бот')">Заказать</button>
                    </div>
                    <div class="service-card">
                        <h3>📊 Парсер данных</h3>
                        <p>Сбор информации с сайтов</p>
                        <div class="price">5 000₽</div>
                        <button class="order-btn" onclick="openModal('Парсер данных')">Заказать</button>
                    </div>
                    <div class="service-card">
                        <h3>🌐 Сайт-визитка</h3>
                        <p>Адаптивный дизайн, форма заявок</p>
                        <div class="price">10 000₽</div>
                        <button class="order-btn" onclick="openModal('Сайт-визитка')">Заказать</button>
                    </div>
                </div>
                
                <a href="/admin" class="admin-link">🔧 Админ-панель</a>
            </div>
            
            <!-- Модальное окно -->
            <div id="orderModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <h2>📋 Оформить заказ</h2>
                    <form id="orderForm">
                        <input type="text" id="name" placeholder="Ваше имя *" required>
                        <input type="text" id="contact" placeholder="Telegram или Discord *" required>
                        <input type="email" id="email" placeholder="Email (необязательно)">
                        <input type="hidden" id="service">
                        <button type="submit" class="submit-btn">Отправить заявку</button>
                        <p class="success-msg" id="successMsg">✅ Заявка отправлена!</p>
                    </form>
                </div>
            </div>
            
            <script>
                function openModal(service) {
                    document.getElementById('service').value = service;
                    document.getElementById('orderModal').classList.add('active');
                }
                function closeModal() {
                    document.getElementById('orderModal').classList.remove('active');
                    document.getElementById('orderForm').reset();
                    document.getElementById('successMsg').style.display = 'none';
                }
                
                document.getElementById('orderForm').onsubmit = async function(e) {
                    e.preventDefault();
                    
                    const btn = this.querySelector('.submit-btn');
                    const originalText = btn.textContent;
                    btn.textContent = 'Отправка...';
                    btn.disabled = true;
                    
                    try {
                        const response = await fetch('/order', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                name: document.getElementById('name').value,
                                contact: document.getElementById('contact').value,
                                email: document.getElementById('email').value,
                                service: document.getElementById('service').value
                            })
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            document.getElementById('successMsg').style.display = 'block';
                            setTimeout(() => {
                                closeModal();
                                btn.textContent = originalText;
                                btn.disabled = false;
                            }, 2000);
                        }
                    } catch (err) {
                        alert('❌ Ошибка отправки. Попробуйте ещё раз.');
                        btn.textContent = originalText;
                        btn.disabled = false;
                    }
                };
                
                // Закрыть modal при клике вне
                document.getElementById('orderModal').onclick = function(e) {
                    if (e.target === this) closeModal();
                };
                // Закрыть по Escape
                document.onkeydown = function(e) {
                    if (e.key === 'Escape') closeModal();
                };
            </script>
        </body>
        </html>
    ''')

# Обработка заказа (AJAX)
@app.route('/order', methods=['POST'])
def order():
    data = request.json
    new_order = Order(
        name=data['name'],
        contact=data['contact'],
        email=data.get('email', ''),
        service=data['service']
    )
    db.session.add(new_order)
    db.session.commit()
    
    # Отправка в Discord
    send_discord(new_order)
    
    return jsonify({'success': True})

# Админ-панель
@app.route('/admin')
def admin():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    rows = ''.join(f'''
        <tr>
            <td>{o.id}</td>
            <td>{o.name}</td>
            <td>{o.contact}</td>
            <td>{o.email or '-'}</td>
            <td>{o.service}</td>
            <td>{o.created_at.strftime('%d.%m.%Y %H:%M')}</td>
        </tr>
    ''' for o in orders)
    
    return render_template_string(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Админ-панель</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; padding: 20px; }}
                h1 {{ color: #7289da; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #333; padding: 12px; text-align: left; }}
                th {{ background: #1e1e1e; color: #7289da; }}
                tr:nth-child(even) {{ background: #1a1a1a; }}
                a {{ color: #5865f2; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>📋 Все заказы</h1>
            <p><a href="/">← На главную</a></p>
            <table>
                <tr><th>ID</th><th>Имя</th><th>Контакты</th><th>Email</th><th>Услуга</th><th>Дата</th></tr>
                {rows}
            </table>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)