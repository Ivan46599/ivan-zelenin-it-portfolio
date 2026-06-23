from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from config import Config
import os
from datetime import datetime, timedelta
import time
import threading

app = Flask(__name__)
app.config.from_object(Config)

# Настройка загрузки файлов
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Навигационное меню
nav_menu = [
    {'title': 'Главная', 'url': '/'},
    {'title': 'Меню', 'url': '/menu'},
    {'title': 'Галерея', 'url': '/gallery'},
    {'title': 'Контакты', 'url': '/contacts'},
    {'title': 'Бронирование', 'url': '/booking'}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_nav_menu():
    return dict(nav_menu=nav_menu, today=datetime.now().strftime('%Y-%m-%d'))

def cleanup_expired_bookings():
    """Очищает истекшие бронирования и освобождает столики"""
    try:
        cur = mysql.connection.cursor()
        
        current_time = datetime.now()
        
        # Находим все истекшие бронирования
        cur.execute("""
            SELECT БронированиеID, СтоликID 
            FROM Бронирования 
            WHERE Статус IN ('ожидание', 'подтверждено')
            AND (
                ДатаПосещения < %s 
                OR 
                (
                    ДатаПосещения = %s 
                    AND ADDTIME(
                        CONCAT(ДатаПосещения, ' ', ВремяПосещения), 
                        CONCAT(Продолжительность, ':00:00')
                    ) < %s
                )
            )
        """, (current_time.date(), current_time.date(), current_time))
        
        expired_bookings = cur.fetchall()
        
        if expired_bookings:
            table_ids = []
            booking_ids = []
            
            for booking in expired_bookings:
                booking_ids.append(booking['БронированиеID'])
                table_ids.append(booking['СтоликID'])
            
            # Освобождаем столики
            if table_ids:
                placeholders = ','.join(['%s'] * len(table_ids))
                cur.execute(f"""
                    UPDATE Столики 
                    SET Статус = 'свободен' 
                    WHERE СтоликID IN ({placeholders})
                """, tuple(table_ids))
            
            # Помечаем бронирования как истекшие
            if booking_ids:
                placeholders = ','.join(['%s'] * len(booking_ids))
                cur.execute(f"""
                    UPDATE Бронирования 
                    SET Статус = 'истекло' 
                    WHERE БронированиеID IN ({placeholders})
                """, tuple(booking_ids))
            
            mysql.connection.commit()
            print(f"[{current_time.strftime('%H:%M:%S')}] Очищено {len(expired_bookings)} истекших бронирований")
        
        cur.close()
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка при очистке бронирований: {e}")
        if 'cur' in locals():
            try:
                mysql.connection.rollback()
            except:
                pass

# Простой планировщик на основе threading
def cleanup_scheduler():
    """Запускает очистку каждые 5 минут"""
    while True:
        time.sleep(300)  # 300 секунд = 5 минут
        try:
            cleanup_expired_bookings()
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка в планировщике: {e}")

# Запускаем планировщик в отдельном потоке
scheduler_thread = threading.Thread(target=cleanup_scheduler, daemon=True)
scheduler_thread.start()

# Вызываем очистку при каждом запросе к бронированию
@app.before_request
def before_request():
    if request.endpoint in ['booking', 'get_tables', 'index']:
        cleanup_expired_bookings()

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT Блюда.*, Категории.Название as Категория 
        FROM Блюда 
        JOIN Категории ON Блюда.КатегорияID = Категории.КатегорияID 
        WHERE Блюда.Доступно = TRUE 
        ORDER BY RAND() 
        LIMIT 6
    """)
    popular_dishes = cur.fetchall()
    
    cur.execute("SELECT COUNT(*) as total, SUM(Вместимость) as seats FROM Столики WHERE Статус = 'свободен'")
    tables_info = cur.fetchone()
    
    cur.execute("SELECT * FROM ФотоРесторана ORDER BY Позиция LIMIT 3")
    restaurant_photos = cur.fetchall()
    
    cur.close()
    
    return render_template('index.html', 
                         popular_dishes=popular_dishes,
                         tables_info=tables_info,
                         restaurant_photos=restaurant_photos)

@app.route('/menu')
def menu():
    category_id = request.args.get('category_id', type=int)
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Категории ORDER BY Позиция")
    categories = cur.fetchall()
    
    if category_id:
        cur.execute("""
            SELECT Блюда.*, Категории.Название as Категория 
            FROM Блюда 
            JOIN Категории ON Блюда.КатегорияID = Категории.КатегорияID 
            WHERE Блюда.КатегорияID = %s AND Блюда.Доступно = TRUE
            ORDER BY Блюда.Название
        """, (category_id,))
    else:
        cur.execute("""
            SELECT Блюда.*, Категории.Название as Категория 
            FROM Блюда 
            JOIN Категории ON Блюда.КатегорияID = Категории.КатегорияID 
            WHERE Блюда.Доступно = TRUE
            ORDER BY Категории.Позиция, Блюда.Название
        """)
    
    dishes = cur.fetchall()
    cur.close()
    
    return render_template('menu.html', 
                         categories=categories,
                         dishes=dishes,
                         selected_category=category_id)

@app.route('/gallery')
def gallery():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT Категория FROM ФотоРесторана ORDER BY Категория")
    categories = cur.fetchall()
    
    category_filter = request.args.get('category', 'all')
    if category_filter != 'all':
        cur.execute("SELECT * FROM ФотоРесторана WHERE Категория = %s ORDER BY Позиция", (category_filter,))
    else:
        cur.execute("SELECT * FROM ФотоРесторана ORDER BY Позиция")
    
    gallery_images = cur.fetchall()
    cur.close()
    
    return render_template('gallery.html', 
                         gallery_images=gallery_images,
                         categories=categories,
                         selected_category=category_filter)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        message = request.form['message']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO ОбратнаяСвязь (Имя, Email, Телефон, Сообщение) 
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, message))
            
            mysql.connection.commit()
            flash('Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Ошибка при отправке сообщения: {str(e)}', 'error')
        
        finally:
            cur.close()
        
        return redirect(url_for('contacts'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Контакты LIMIT 1")
    contact_info = cur.fetchone()
    cur.close()
    
    return render_template('contacts.html', contact_info=contact_info)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        date_str = request.form['date']
        time_str = request.form['time']
        guests = int(request.form['guests'])
        table_id = int(request.form['table_id'])
        duration = int(request.form.get('duration', 2))
        comment = request.form.get('comment', '')
        
        try:
            booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if booking_datetime < datetime.now():
                flash('Выбранное время уже прошло. Пожалуйста, выберите другое время.', 'error')
                return redirect(url_for('booking'))
        except ValueError:
            flash('Неверный формат даты или времени.', 'error')
            return redirect(url_for('booking'))
        
        cur = mysql.connection.cursor()
        
        try:
            end_time = (datetime.strptime(time_str, "%H:%M") + timedelta(hours=duration)).strftime("%H:%M")
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM Бронирования 
                WHERE СтоликID = %s 
                AND ДатаПосещения = %s 
                AND Статус IN ('ожидание', 'подтверждено')
                AND (
                    (%s BETWEEN ВремяПосещения AND 
                        ADDTIME(ВремяПосещения, CONCAT(Продолжительность, ':00:00')))
                    OR
                    (%s BETWEEN ВремяПосещения AND 
                        ADDTIME(ВремяПосещения, CONCAT(Продолжительность, ':00:00')))
                    OR
                    (ВремяПосещения BETWEEN %s AND %s)
                )
            """, (table_id, date_str, time_str, end_time, time_str, end_time))
            
            booking_exists = cur.fetchone()['count'] > 0
            
            if booking_exists:
                flash('Этот столик уже забронирован на выбранное время.', 'error')
                return redirect(url_for('booking'))
            
            cur.execute("SELECT КлиентID FROM Клиенты WHERE Телефон = %s", (phone,))
            client = cur.fetchone()
            
            if client:
                client_id = client['КлиентID']
            else:
                cur.execute("""
                    INSERT INTO Клиенты (Имя, Телефон, Email) 
                    VALUES (%s, %s, %s)
                """, (name, phone, email))
                client_id = cur.lastrowid
            
            cur.execute("""
                INSERT INTO Бронирования 
                (КлиентID, СтоликID, ДатаПосещения, ВремяПосещения, 
                 Продолжительность, КоличествоГостей, Комментарий, Статус) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'ожидание')
            """, (client_id, table_id, date_str, time_str, duration, guests, comment))
            
            booking_id = cur.lastrowid
            
            cur.execute("""
                UPDATE Столики 
                SET Статус = 'забронирован' 
                WHERE СтоликID = %s
            """, (table_id,))
            
            mysql.connection.commit()
            
            cur.execute("""
                SELECT b.*, s.Номер as НомерСтолика
                FROM Бронирования b
                JOIN Столики s ON b.СтоликID = s.СтоликID
                WHERE b.БронированиеID = %s
            """, (booking_id,))
            
            booking_info = cur.fetchone()
            
            end_display_time = (datetime.strptime(time_str, "%H:%M") + 
                              timedelta(hours=duration)).strftime("%H:%M")
            
            flash(
                f'✅ Бронирование №{booking_info["БронированиеID"]} успешно создано!<br>'
                f'• Столик №{booking_info["НомерСтолика"]}<br>'
                f'• Дата: {date_str}<br>'
                f'• Время: {time_str} - {end_display_time} ({duration} ч.)<br>'
                f'• Гостей: {guests}<br><br>'
                f'Мы свяжемся с вами для подтверждения в течение 30 минут.',
                'success'
            )
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'❌ Ошибка при создании бронирования: {str(e)}', 'error')
        
        finally:
            cur.close()
        
        return redirect(url_for('booking'))
    
    cleanup_expired_bookings()
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM Столики 
        WHERE Статус = 'свободен' 
        ORDER BY Вместимость
    """)
    tables = cur.fetchall()
    cur.close()
    
    return render_template('booking.html', tables=tables)

@app.route('/api/tables')
def get_tables():
    date = request.args.get('date')
    time = request.args.get('time')
    guests = request.args.get('guests', type=int)
    duration = request.args.get('duration', 2, type=int)
    
    if not all([date, time, guests]):
        return jsonify({'error': 'Missing parameters'}), 400
    
    cur = mysql.connection.cursor()
    cleanup_expired_bookings()
    
    try:
        start_time = datetime.strptime(time, "%H:%M")
        end_time = (start_time + timedelta(hours=duration)).strftime("%H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid time format'}), 400
    
    cur.execute("""
        SELECT DISTINCT СтоликID 
        FROM Бронирования 
        WHERE ДатаПосещения = %s 
        AND Статус IN ('ожидание', 'подтверждено')
        AND (
            (%s BETWEEN ВремяПосещения AND 
                ADDTIME(ВремяПосещения, CONCAT(Продолжительность, ':00:00')))
            OR
            (%s BETWEEN ВремяПосещения AND 
                ADDTIME(ВремяПосещения, CONCAT(Продолжительность, ':00:00')))
            OR
            (ВремяПосещения BETWEEN %s AND %s)
        )
    """, (date, time, end_time, time, end_time))
    
    booked_tables = [row['СтоликID'] for row in cur.fetchall()]
    
    if booked_tables:
        placeholders = ','.join(['%s'] * len(booked_tables))
        query = f"""
            SELECT * FROM Столики 
            WHERE Статус = 'свободен' 
            AND Вместимость >= %s
            AND СтоликID NOT IN ({placeholders})
            ORDER BY Вместимость
        """
        params = (guests,) + tuple(booked_tables)
    else:
        query = """
            SELECT * FROM Столики 
            WHERE Статус = 'свободен' 
            AND Вместимость >= %s
            ORDER BY Вместимость
        """
        params = (guests,)
    
    cur.execute(query, params)
    tables = cur.fetchall()
    cur.close()
    
    result = []
    for table in tables:
        result.append({
            'СтоликID': table['СтоликID'],
            'Номер': table['Номер'],
            'Вместимость': table['Вместимость'],
            'Расположение': table['Расположение'],
            'Фото': table['Фото'],
            'Статус': table['Статус']
        })
    
    return jsonify(result)

@app.route('/dish/<int:dish_id>')
def dish_detail(dish_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT Блюда.*, Категории.Название as Категория 
        FROM Блюда 
        JOIN Категории ON Блюда.КатегорияID = Категории.КатегорияID 
        WHERE БлюдоID = %s
    """, (dish_id,))
    dish = cur.fetchone()
    cur.close()
    
    if not dish:
        flash('Блюдо не найдено', 'error')
        return redirect(url_for('menu'))
    
    return render_template('dish_detail.html', dish=dish)

# Админ-панель
@app.route('/admin/bookings')
def admin_bookings():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            b.*,
            c.Имя as ИмяКлиента,
            c.Телефон as ТелефонКлиента,
            c.Email as EmailКлиента,
            s.Номер as НомерСтолика,
            s.Вместимость,
            CASE 
                WHEN b.Статус IN ('ожидание', 'подтверждено') AND 
                     (b.ДатаПосещения < CURDATE() OR 
                     (b.ДатаПосещения = CURDATE() AND 
                      ADDTIME(b.ВремяПосещения, CONCAT(b.Продолжительность, ':00:00')) < CURTIME()))
                THEN 'истекло'
                ELSE b.Статус
            END as АктуальныйСтатус
        FROM Бронирования b
        JOIN Клиенты c ON b.КлиентID = c.КлиентID
        JOIN Столики s ON b.СтоликID = s.СтоликID
        ORDER BY b.ДатаПосещения DESC, b.ВремяПосещения DESC
    """)
    bookings = cur.fetchall()
    cur.close()
    
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
def update_booking(booking_id):
    action = request.form.get('action')
    cur = mysql.connection.cursor()
    
    try:
        if action == 'confirm':
            cur.execute("""
                UPDATE Бронирования 
                SET Статус = 'подтверждено' 
                WHERE БронированиеID = %s
            """, (booking_id,))
            flash('Бронирование подтверждено', 'success')
            
        elif action == 'cancel':
            # Получаем информацию о бронировании
            cur.execute("SELECT СтоликID FROM Бронирования WHERE БронированиеID = %s", (booking_id,))
            booking = cur.fetchone()
            
            if booking:
                # Освобождаем столик
                cur.execute("UPDATE Столики SET Статус = 'свободен' WHERE СтоликID = %s", (booking['СтоликID'],))
            
            cur.execute("""
                UPDATE Бронирования 
                SET Статус = 'отменено' 
                WHERE БронированиеID = %s
            """, (booking_id,))
            flash('Бронирование отменено', 'success')
        
        mysql.connection.commit()
        
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Ошибка: {str(e)}', 'error')
    
    finally:
        cur.close()
    
    return redirect(url_for('admin_bookings'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'dishes'))
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'restaurant'))
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'tables'))
    
    print("=" * 60)
    print("🍽️  Система бронирования ресторана запущена!")
    print(f"🌐 Адрес: http://localhost:5000")
    print(f"👨‍💼 Админ-панель: http://localhost:5000/admin/bookings")
    print("=" * 60)
    print("Особенности:")
    print("• Временное бронирование (2 часа по умолчанию)")
    print("• Автоматическая очистка истекших бронирований")
    print("• Проверка пересечений по времени")
    print("• Адаптивный интерфейс")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
