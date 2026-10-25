## Требования

- Python 3.10+
- Docker (контейнер PostgreSQL с именем `pg`)

## Установка

1. Запустите базу данных и загрузите схему и данные:
   ```powershell
   docker start pg
   Get-Content schema.sql | docker exec -i pg psql -U postgres
   Get-Content seed.sql   | docker exec -i pg psql -U postgres
   ```
2. Создайте виртуальное окружение и установите зависимости:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Скопируйте `.env.example` в `.env` и **замените значения-заглушки на свои**:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:ВАШ_ПАРОЛЬ@localhost:5432/postgres
   ```
   Файл `.env` не попадает в репозиторий (он указан в `.gitignore`).

## Запуск

```powershell
python dashboard.py
```

## Пример вывода

```text
=== Store Dashboard ===
Users: 1000 | Products: 200 | Orders: 30000

Catalog:
  Aero Backpack 126              $   55.79   (stock 378)
  ...

Top customers:
  user168@example.com - 144 items
  user183@example.com - 142 items
  user826@example.com - 140 items

1) Добавить товар  2) Оформить заказ  0) Выход
```

## Структура проекта

- `dashboard.py` — основная программа
- `requirements.txt` — зависимости
- `.env.example` — пример файла настроек
- `schema.sql`, `seed.sql` — схема и тестовые данные (если добавляете их в репозиторий)
