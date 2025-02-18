# Развертывание FastAPI 

Это приложение FastAPI предназначено для регистрации пользователя и работе с реферальными программами. Оно использует асинхронные вызовы и подключается к базе данных PostgreSQL.
### Основные компоненты приложения
## Эндпоинты
 1. Регистрация пользователя
**POST /register**  

---
 2. Получение токена доступа
**POST /token**  

---
 3. Создание реферального кода
**POST /referral-code**  

---
 4. Удаление реферального кода
**DELETE /referral-code**  

---
 5. Получение реферального кода по email
**GET /referral-code-by-email/{email}**  

---
 6. Получение рефералов по ID реферера
**GET /referrals/{referrer_id}**  



3. **Подключение к базе данных**:
   - Используется SQLAlchemy для работы с базой данных и асинхронные сессии для выполнения запросов.   
5. **Docker и Docker Compose**:
   - Приложение упаковано в Docker-контейнер, что упрощает его развертывание.
6. **Запустите контейнер базы данных:**:
     - Запустите контейнер базы данных docker-compose up --build
 
7. **Запуск приложения**:
     - Заполнить .env файл с подключением. DATABASE_URL=......
     - В alembic ini ввести sqlalchemy.url = "...."
     - Заполнить API ключ в модуле app/utils.py HUNTER_API_KEY = '.....'
     - Ввести команду docker-compose up -d 
     - Запуск сервера uvicorn main:app --reload  
8.  Войти по адрессу http://127.0.0.1:8000/docs/ 
9. Реализован кеш с помощью словаря.
10. Так же реализован Hunter IO для проверки указанного email 	адреса;
