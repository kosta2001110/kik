import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# ============================================
# === НАСТРОЙКИ ===
# ============================================

URL = 'https://books.toscrape.com/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# ============================================
# === ПАРСИНГ ===
# ============================================

def parse_books():
    print("🔌 Подключение к сайту...")
    print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    response = requests.get(URL, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Ошибка: {response.status_code}")
        return
    
    print("✅ Сайт загружен!")
    
    soup = BeautifulSoup(response.text, 'lxml')
    books = soup.find_all('article', class_='product_pod')
    
    print(f"📚 Найдено книг: {len(books)}")
    
    books_data = []
    
    for book in books:
        try:
            title = book.find('h3').find('a')['title']
            price = book.find('p', class_='price_color').text
            rating_class = book.find('p', class_='star-rating')['class']
            rating = rating_class[1] if len(rating_class) > 1 else 'No Rating'
            link = URL + 'catalogue/' + book.find('h3').find('a')['href']
            
            data = {
                'title': title,
                'price': price,
                'rating': rating,
                'link': link,
                'parsed_date': datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            books_data.append(data)
            
            print(f"✓ {title[:50]}... - {price}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    # ============================================
    # === СОХРАНЕНИЕ ===
    # ============================================
    
    if books_data:
        df = pd.DataFrame(books_data)
        df.to_csv('books_day1.csv', index=False, encoding='utf-8-sig')
        df.to_excel('books_day1.xlsx', index=False)
        
        print(f"\n{'='*50}")
        print(f"✅ СОХРАНЕНО: {len(books_data)} книг")
        print(f"📁 Файлы: books_day1.csv, books_day1.xlsx")
        print(f"{'='*50}")
    else:
        print("\n⚠️ Нет данных")

# ============================================
# === ЗАПУСК ===
# ============================================

if __name__ == '__main__':
    parse_books()