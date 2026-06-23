-- 1. Модели самолетов с дальностью полета 4200 км
SELECT model_name 
FROM airliners 
WHERE flight_range = 4200;

-- 2. Билеты стоимостью <= 13200
SELECT id 
FROM tickets 
WHERE price <= 13200;

-- 3. Бортовые номера белых самолетов
SELECT side_number 
FROM airliners 
WHERE color = 'white';

-- 4. Дальность полета Cessna 172
SELECT flight_range as max_distance 
FROM airliners 
WHERE model_name = 'Cessna 172';

-- 5. Рейсы в аэропорты PEZ, MMK, VKO
SELECT id 
FROM trips 
WHERE arrival IN ('PEZ', 'MMK', 'VKO');

-- 6. Отмененные рейсы из DME
SELECT id 
FROM trips 
WHERE departure = 'DME' AND status = 'Cancelled';

-- 7. Модели самолетов с дальностью 4200-7900 км
SELECT model_name 
FROM airliners 
WHERE flight_range BETWEEN 4200 AND 7900;

-- 8. Клиенты с именем Daria
SELECT id 
FROM clients 
WHERE name LIKE 'Daria%';

-- 9. Билеты не бизнес-класса
SELECT id 
FROM tickets 
WHERE service_class != 'Business';

-- 10. Пассажир Denis с фамилией на S и телефоном +7XXX0700202
SELECT id, name 
FROM clients 
WHERE name LIKE 'Denis S%' AND phone LIKE '+7___0700202';

-- 11. Пассажиры Volkov/Volkova 21-25 лет
SELECT id 
FROM clients 
WHERE (name LIKE '%Volkov' OR name LIKE '%Volkova') 
AND age BETWEEN 21 AND 25;

-- 12. Билеты бизнес-класса с ценой не в диапазоне 9100-70400
SELECT id, price 
FROM tickets 
WHERE service_class = 'Business' 
AND price NOT BETWEEN 9100 AND 70400;

-- 13. Пассажиры с ID на RCB/FCV и телефоном не на +705
SELECT name 
FROM clients 
WHERE (id LIKE '%RCB' OR id LIKE '%FCV') 
AND phone NOT LIKE '+705%';

-- 14. Сложное условие по самолетам
SELECT side_number 
FROM airliners 
WHERE country != 'Russia' 
OR (country = 'Russia' 
    AND production_year NOT IN (2005, 2008) 
    AND flight_range > 5000);

-- 15. Коды рейсов в воздухе с условиями по аэропортам
SELECT trip_code 
FROM trips 
WHERE status = 'Departed' 
AND (arrival IN ('MQF', 'ABA') 
     OR departure NOT IN ('PYJ', 'CNN'));

-- 16. Билеты по классам и цене с исключением рейсов
SELECT id 
FROM tickets 
WHERE ((service_class = 'Business' AND price < 15000) 
       OR (service_class = 'Economy' AND price > 65000))
AND trip_id NOT IN ('VR5SF5YIWN', 'OZAO28DLFP', 'LL4S1G8PQW');

-- 17. Рейсы с неправильным префиксом кода
SELECT id, trip_code 
FROM trips 
WHERE trip_code NOT LIKE 'FY%';

-- 18. Рейсы из Москвы в воздухе
SELECT trip_code 
FROM trips 
WHERE departure IN ('SVO', 'VKO', 'DME') 
AND status = 'Departed';

-- 19. Ближне- и дальнемагистральные самолеты
SELECT side_number, flight_range 
FROM airliners 
WHERE (flight_range > 1000 AND flight_range <= 2500) 
OR flight_range >= 6000;

-- 20. Билеты с NULL trip_id
SELECT id 
FROM tickets 
WHERE trip_id IS NULL;

-- 21. Класс обслуживания билетов с корректным trip_id
SELECT service_class 
FROM tickets 
WHERE trip_id IS NOT NULL;

-- 22. Билеты с классом не Economy и не NULL
SELECT id 
FROM tickets 
WHERE service_class NOT IN ('Economy') 
AND service_class IS NOT NULL;

-- 23. Билеты с любым NULL полем (кроме id)
SELECT id 
FROM tickets 
WHERE id IS NOT NULL 
AND (trip_id IS NULL OR service_class IS NULL OR price IS NULL OR client_id IS NULL);

-- 24. Билеты с классом не Economy и не Business
SELECT id, trip_id 
FROM tickets 
WHERE service_class NOT IN ('Economy', 'Business') 
AND service_class IS NOT NULL;

-- 25. Клиенты с некорректными билетами рейса RL6EC4YWB1
SELECT client_id 
FROM tickets 
WHERE trip_id = 'RL6EC4YWB1' 
AND id LIKE 'UE01H8UCJQ%' 
AND id != 'UE01H8UCJQ8O';

-- 26. Категории самолетов по дальности
SELECT model_name,
       CASE 
           WHEN flight_range > 1000 AND flight_range <= 2500 THEN 'short-haul'
           WHEN flight_range > 2500 AND flight_range <= 6000 THEN 'medium-haul'
           WHEN flight_range > 6000 THEN 'long-haul'
       END as category
FROM airliners 
WHERE flight_range > 1000;

-- 27. Категории самолетов с UNDEFINED
SELECT model_name,
       CASE 
           WHEN flight_range <= 1000 OR flight_range IS NULL THEN 'UNDEFINED'
           WHEN flight_range > 1000 AND flight_range <= 2500 THEN 'short-haul'
           WHEN flight_range > 2500 AND flight_range <= 6000 THEN 'medium-haul'
           WHEN flight_range > 6000 THEN 'long-haul'
       END as category
FROM airliners;

-- 28. Статус проверки самолетов
SELECT side_number,
       CASE 
           WHEN production_year < 2000 THEN 'review_old'
           WHEN production_year > 2010 THEN 'no_review'
           WHEN flight_range > 6000 THEN 'review_mid_long_haul'
           WHEN flight_range > 2500 THEN 'review_mid_medium_haul'
           ELSE 'review_mid_short_haul'
       END as review_status
FROM airliners 
WHERE production_year BETWEEN 2000 AND 2010 
OR production_year < 2000 
OR production_year > 2010;

-- 29. Имена и телефоны пассажиров с UNDEFINED
SELECT name, COALESCE(phone, 'UNDEFINED') as phone 
FROM clients;

-- 30. Билеты по ценовым категориям
SELECT id, service_class, price
FROM tickets
WHERE (service_class = 'Economy' AND price BETWEEN 10000 AND 11000)
   OR (service_class = 'PremiumEconomy' AND price BETWEEN 20000 AND 30000)
   OR (service_class = 'Business' AND price > 100000);

-- 31. Сортировка билетов по цене
SELECT id, trip_id, price 
FROM tickets 
ORDER BY price ASC;

-- 32. Сложная сортировка билетов
SELECT id, trip_id, price 
FROM tickets 
ORDER BY price ASC, trip_id DESC, id ASC;

-- 33. Уникальные модели самолетов
SELECT DISTINCT model_name 
FROM airliners;

-- 34. Конкатенация имени и возраста
SELECT CONCAT(name, ' (', age, ')') as name_with_age 
FROM clients 
ORDER BY name_with_age;

-- 35. Возмещение за багаж
SELECT id, price - 2500 as returns 
FROM tickets 
WHERE trip_id = '87RVI5T7A2' 
AND price >= 2500;

-- 36. Цены со скидкой 8%
SELECT service_class, price, price * 0.92 as new_price 
FROM tickets;

-- 37. Длина названий моделей на S
SELECT LENGTH(model_name) as len_model_name 
FROM airliners 
WHERE model_name LIKE 'S%';

-- 38. Клиенты с длиной имени 10-13 символов
SELECT id 
FROM clients 
WHERE LENGTH(name) BETWEEN 10 AND 13;

-- 39. Имена с первой заглавной буквой
SELECT id, CONCAT(UPPER(SUBSTRING(name, 1, 1)), LOWER(SUBSTRING(name, 2))) as newname 
FROM clients;

-- 40. Телефоны без пробелов
SELECT id, REPLACE(phone, ' ', '') as newphone 
FROM clients;

-- 41. Маскировка телефонов
SELECT id, 
       CONCAT(SUBSTRING(phone, 1, 2), 
              REPEAT('*', LENGTH(phone) - 4), 
              SUBSTRING(phone, LENGTH(phone) - 1)) as phone 
FROM clients 
WHERE phone IS NOT NULL;

-- 42. Классы возраста самолетов
SELECT side_number,
       CASE 
           WHEN production_year < 2000 THEN 'Old'
           WHEN production_year BETWEEN 2000 AND 2010 THEN 'Mid'
           ELSE 'New'
       END as age
FROM airliners 
WHERE flight_range <= 10000 OR flight_range IS NULL
ORDER BY age;

-- 43. Цены со скидками на определенные рейсы
SELECT id, trip_id,
       CASE 
           WHEN service_class = 'Economy' THEN price * 0.85
           WHEN service_class = 'Business' THEN price * 0.90
           WHEN service_class = 'PremiumEconomy' THEN price * 0.80
           ELSE price
       END as new_price
FROM tickets 
WHERE trip_id IN ('LL4S1G8PQW', '0SE4S0HRRU', 'JQF04Q8I9G');

-- 44. Рейсы прибывшие с ID на Y
SELECT trip_code as flight 
FROM trips 
WHERE status = 'Arrived' 
AND id LIKE 'Y%'
ORDER BY flight;

-- 45. Рейсы в DME в нижнем регистре
SELECT LOWER(departure) as departure, 
       LOWER(status) as status, 
       LOWER(airliner_id) as airliner_id 
FROM trips 
WHERE arrival = 'DME';

-- 46. Пассажиры старше 21 с длиной имени 13
SELECT DISTINCT name 
FROM clients 
WHERE age > 21 
AND LENGTH(name) = 13 
ORDER BY age;

-- 47. Пассажирки Anna с телефонами
SELECT name, COALESCE(phone, 'UNDEFINED') as phone 
FROM clients 
WHERE name LIKE 'Anna%';

-- 48. Аэропорты назначения для самолета 305881
SELECT DISTINCT arrival 
FROM trips 
WHERE airliner_id = '305881' 
ORDER BY arrival;

-- 49. Рейсы определенных самолетов с сортировкой
SELECT id, trip_code 
FROM trips 
WHERE airliner_id IN ('305881', '473503', '603813') 
ORDER BY arrival, trip_code DESC;

-- 50. Статус цены билета
SELECT LOWER(id) as id,
       CASE 
           WHEN price IS NULL THEN 'UNDEFINED'
           ELSE 'DEFINED'
       END as price_status
FROM tickets;

-- 51. Пассажиры самолета 305881
SELECT DISTINCT c.name 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
JOIN trips tr ON t.trip_id = tr.id 
WHERE tr.airliner_id = '305881';

-- 52. Пассажиры отложенных рейсов
SELECT DISTINCT c.name, tr.departure 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
JOIN trips tr ON t.trip_id = tr.id 
WHERE tr.status = 'Delayed';

-- 53. Самолеты без рейсов
SELECT a.model_name 
FROM airliners a 
LEFT JOIN trips t ON a.id = t.airliner_id 
WHERE t.id IS NULL;

-- 54. Пассажиры эконом-премиум с ценой ниже средней
SELECT c.name, t.price 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
WHERE t.service_class = 'PremiumEconomy' 
AND t.price < (SELECT AVG(price) FROM tickets WHERE price IS NOT NULL);

-- 55. Пассажиры летавшие на российских самолетах
SELECT DISTINCT c.id, c.name 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
JOIN trips tr ON t.trip_id = tr.id 
JOIN airliners a ON tr.airliner_id = a.id 
WHERE a.country = 'Russia';

-- 56. Пассажиры летавшие на самолетах старше них
SELECT DISTINCT c.id, c.name 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
JOIN trips tr ON t.trip_id = tr.id 
JOIN airliners a ON tr.airliner_id = a.id 
WHERE a.production_year < c.age;

-- 57. Максимальная цена билета в DME
SELECT MAX(t.price) as max_price 
FROM tickets t 
JOIN trips tr ON t.trip_id = tr.id 
WHERE tr.arrival = 'DME' 
AND t.price IS NOT NULL;

-- 58. Количество рейсов на белых самолетах
SELECT COUNT(*) as count 
FROM trips tr 
JOIN airliners a ON tr.airliner_id = a.id 
WHERE a.color = 'white';

-- 59. Пассажиры летавшие первым классом
SELECT DISTINCT c.id, c.name 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
WHERE t.service_class = 'FirstClass';

-- 60. Максимальная цена на билеты самолетов с макс. дальностью
SELECT MAX(t.price) as max_price 
FROM tickets t 
JOIN trips tr ON t.trip_id = tr.id 
JOIN airliners a ON tr.airliner_id = a.id 
WHERE a.flight_range = (SELECT MAX(flight_range) FROM airliners) 
AND t.price IS NOT NULL;

-- 61. Количество Надежд на самолетах в пути
SELECT COUNT(DISTINCT c.id) as hope_count 
FROM clients c 
JOIN tickets t ON c.id = t.client_id 
JOIN trips tr ON t.trip_id = tr.id 
WHERE c.name LIKE 'Nadezhda%' 
AND tr.status = 'Departed';

-- 62. Затраты на акцию
SELECT SUM(t.price) - SUM(
    CASE 
        WHEN t.service_class = 'Economy' THEN t.price * 0.85
        WHEN t.service_class = 'FirstClass' THEN t.price * 0.90
        WHEN t.service_class = 'PremiumEconomy' THEN t.price * 0.80
        ELSE t.price
    END
) as expenses
FROM tickets t 
WHERE t.trip_id IN ('DAA22Y84O7', '41BVLBDKOH', 'VCKEGVKWW8') 
AND t.price IS NOT NULL;

-- 63. Средняя дальность Airbus с 2008 года
SELECT AVG(flight_range) as avg_range 
FROM airliners 
WHERE model_name LIKE 'Airbus%' 
AND production_year >= 2008;

-- 64. Модели с разностью дальности > 1000
SELECT model_name 
FROM airliners 
GROUP BY model_name 
HAVING MAX(flight_range) - MIN(flight_range) > 1000 
ORDER BY MAX(flight_range) - MIN(flight_range) DESC;

-- 65. Средняя цена по классам обслуживания
SELECT service_class, AVG(price) as avg_price 
FROM tickets 
WHERE service_class IS NOT NULL 
AND trip_id NOT IN ('FYNDDJVU', 'FYMKPDZC') 
GROUP BY service_class 
ORDER BY avg_price;

-- 66. Статистика по категориям самолетов
SELECT 
    CASE 
        WHEN flight_range > 1000 AND flight_range <= 2500 THEN 'short-haul'
        WHEN flight_range > 2500 AND flight_range <= 6000 THEN 'medium-haul'
        WHEN flight_range > 6000 THEN 'long-haul'
    END as category,
    AVG(production_year) as avg_year,
    COUNT(*) as cnt
FROM airliners 
WHERE flight_range > 1000 
GROUP BY category;

-- 67. Билеты > 60% от максимального для пассажира
SELECT t1.client_id, t1.id 
FROM tickets t1 
JOIN (
    SELECT client_id, MAX(price) as max_price 
    FROM tickets 
    WHERE price IS NOT NULL 
    GROUP BY client_id
) t2 ON t1.client_id = t2.client_id 
WHERE t1.price > t2.max_price * 0.6 
ORDER BY t1.client_id;

-- 68. Разность средней цены рейса и общей средней
SELECT 
    (SELECT AVG(price) FROM tickets WHERE trip_id = '8RF8OIOVFR' AND price IS NOT NULL) - 
    (SELECT AVG(price) FROM tickets WHERE price IS NOT NULL) as diff;

-- 69. Разность средней цены рейсов и общей средней
SELECT 
    (SELECT AVG(price) FROM tickets WHERE trip_id IN (
        SELECT id FROM trips WHERE trip_code IN ('FYIHSLAA', 'FYDKIBWN')
    ) AND price IS NOT NULL) - 
    (SELECT AVG(price) FROM tickets WHERE price IS NOT NULL) as diff;

-- 70. Классы возраста самолетов
SELECT side_number,
       CASE 
           WHEN production_year < 2000 THEN 'Old'
           WHEN production_year BETWEEN 2000 AND 2010 THEN 'Mid'
           ELSE 'New'
       END as age
FROM airliners 
WHERE flight_range <= 10000 OR flight_range IS NULL
ORDER BY age;