import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()


def get_engine():
    """Create and return a SQLAlchemy engine from DATABASE_URL."""
    url = os.getenv("DATABASE_URL")
    # TODO: create the engine; handle a missing URL gracefully
    if not url:
        print("Ошибка: DATABASE_URL не задана.")
        sys.exit(1)
    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        print("Ошибка: проверка не прошла.")
        sys.exit(1)
    return create_engine(url)


def store_report(engine):
    """Print counts, the catalog, and the top 3 customers."""
    with engine.connect() as conn:
        # TODO: COUNT(*) on users, products, orders
        # TODO: SELECT name, price, stock FROM products ORDER BY name
        # TODO: top 3 customers by SUM(quantity) via a join + GROUP BY
        users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        orders = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        print("=== Store Dashboard ===")
        print(f"Users: {users} | Products: {products} | Orders: {orders}")

        rows = conn.execute(
            text("SELECT name, price, stock FROM products ORDER BY name")
        ).fetchall()
        print()
        print("Catalog:")
        for row in rows:
            print(f"  {row.name:<30} ${row.price:>8.2f}   (stock {row.stock})")

        top = conn.execute(text("""
        SELECT u.email, SUM(o.quantity) AS total 
        FROM orders o 
        JOIN users u ON u.id = o.user_id 
        GROUP BY u.id, u.email ORDER BY total DESC, u.email ASC 
        LIMIT 3
        """)).fetchall()

        print()
        print("Top customers:")
        for row in top:
            n = int(row.total)
            word = "item" if n == 1 else "items"
            print(f"  {row.email} - {n} {word}")


def add_product(engine, name, category, price, stock):
    """INSERT a product and return its new id."""
    with engine.begin() as conn:  # begin() commits automatically at the end
        # TODO: INSERT ... RETURNING id, with named parameters (include category)
        new_product = conn.execute(
            text(
                "INSERT INTO products (name, category, price, stock) "
                "VALUES (:name, :category, :price, :stock) RETURNING id"
            ),
            {
                "name": name,
                "category": category,
                "price": price,
                "stock": stock,
            },
        ).scalar_one()
    return new_product


def place_order(engine, email, product_name, quantity):
    """Create an order and decrement stock in one transaction."""
    with engine.begin() as conn:  # begin() commits on success, rolls back on error
        # TODO: look up user_id by email and product (id + stock) by name
        # TODO: if stock < quantity, raise an error to trigger rollback
        # TODO: INSERT the order, then UPDATE the product's stock
        if quantity < 1:
            raise ValueError("Количество должно быть не меньше 1")

        user = conn.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": email}
        ).first()
        if user is None:
            raise ValueError("Не удалось найти такого пользователя")

        product = conn.execute(
            text("SELECT id, stock FROM products WHERE name = :name"),
            {"name": product_name},
        ).first()
        if product is None:
            raise ValueError("Не удалось найти такой продукт")
        if product.stock < quantity:
            raise ValueError("Недостаточно товаров на складе")

        conn.execute(
            text("INSERT INTO orders (user_id, product_id, quantity, status) "
            "VALUES (:user_id, :product_id, :quantity, :status)"),
            {"user_id": user.id, "product_id": product.id, "quantity": quantity, "status": "pending"},)
        conn.execute(
            text("UPDATE products SET stock = stock - :quantity WHERE id = :product_id"),
            {"quantity": quantity, "product_id": product.id},)


def main():
    engine = get_engine()
    store_report(engine)
    # TODO: a small menu to add a product or place an order
    while True:
        print()
        print("1) Добавить товар  2) Оформить заказ  0) Выход")
        choice = input("Выбор: ").strip()

        if choice == "1":
            name = input("Название товара: ").strip()
            category = input("Категория: ").strip()
            if not name or not category:
                print("Название и категория обязательны.")
                continue

            try:
                price = float(input("Цена: ").replace(",", "."))
                stock = int(input("Остаток: "))
            except ValueError:
                print("Цена должна быть числом, остаток целым числом.")
                continue

            if price < 0 or stock < 0:
                print("Цена и остаток не могут быть отрицательными.")
                continue

            try:
                new_id = add_product(engine, name, category, price, stock)
            except SQLAlchemyError:
                print("Не удалось добавить товар: база отклонила значения.")
                continue
            print(f"Товар добавлен, id: {new_id}")

        elif choice == "2":
            email = input("Email пользователя: ").strip()
            product_name = input("Название товара: ").strip()

            try:
                quantity = int(input("Количество: "))
            except ValueError:
                print("Количество должно быть целым числом.")
                continue

            try:
                place_order(engine, email, product_name, quantity)
            except ValueError as e:
                print(f"Заказ отклонён: {e}")
                continue
            except SQLAlchemyError:
                print("Заказ отклонён: база не приняла данные (проверьте количество).")
                continue
            print("Заказ оформлен.")

        elif choice == "0":
            break

        else:
            print("Неизвестный пункт меню.")

if __name__ == "__main__":
    main()
