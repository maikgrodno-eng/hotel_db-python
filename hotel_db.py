import psycopg2


class DBFacade:

    def __init__(self):

        self.DB_CONNECTION = psycopg2.connect(
            dbname='hotel_db',
            user='postgres',
            password='123456',
            host='localhost',
            port=5432
        )
        self.cursor = self.DB_CONNECTION.cursor()
        self.create_tables()

    def create_tables(self):

        try:

            create_category_table = """
                CREATE TABLE IF NOT EXISTS category (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    price NUMERIC(10,2)
                );
            """

            create_number_table = """
                CREATE TABLE IF NOT EXISTS number (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category_id INTEGER REFERENCES category(id) ON DELETE CASCADE                    
                );
            """

            create_visitor_table = """
                CREATE TABLE IF NOT EXISTS visitor (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    number_id INTEGER REFERENCES number(id) ON DELETE SET NULL
                );
            """

            self.cursor.execute(create_category_table)
            self.cursor.execute(create_number_table)
            self.cursor.execute(create_visitor_table)

            self.DB_CONNECTION.commit()
            print("Таблицы созданы успешно!")

        except Exception as e:

            print(f"Ошибка при создании таблиц: {e}")
            self.DB_CONNECTION.rollback()

    def add_category(self):

        try:
            user_input = input(" Выберите категорию номера \n 'Эконом' - 1 \n 'Стандарт' - 2 \n 'Люкс' - 3  \n Введите категорию номера: ")

            price_category = float(input("Введите стоимость номера за сутки: "))

            if user_input == '1':
                name_category = 'Эконом'

            elif user_input == '2':
                name_category = 'Стандарт'

            elif user_input == '3':
                name_category = 'Люкс'

            else:
                print("Неверный выбор!")
                return

            add_category = """
                    INSERT INTO category (name, price) VALUES (%s, %s);
                """
            self.cursor.execute(add_category, (name_category, price_category))

            self.DB_CONNECTION.commit()

            print(f"Категория '{name_category}' успешно добавлена, стоимость в сутки составит: {price_category} руб.!")

        except Exception as e:

            print(f"Ошибка при добавлении категории: {e}")

            self.DB_CONNECTION.rollback()

    def add_number(self):

        try:
            number_name = input("Введите название номера: ")

            self.cursor.execute("SELECT id, name, price FROM category")

            categories = self.cursor.fetchall()

            print("\nДоступные категории:")

            for category in categories:
                print(f"ID: {category[0]}, {category[1]} - {category[2]} руб.")

            category_id = int(input("Выберите ID категории: "))

            add_number = """
                    INSERT INTO number (name, category_id) VALUES (%s, %s);
                """
            self.cursor.execute(add_number, (number_name, category_id))

            self.DB_CONNECTION.commit()

            print(f"Номер '{number_name}' успешно добавлен!")

        except Exception as e:

            print(f"Ошибка при добавлении номера: {e}")
            self.DB_CONNECTION.rollback()

    def add_visitor_query(self):

        try:

            visitor_name = input("Введите Имя и Фамилию посетителя отеля: ")

            self.cursor.execute("""
                    SELECT n.id, n.name, c.name, c.price 
                    FROM number n 
                    JOIN category c ON n.category_id = c.id
                    WHERE n.id NOT IN (SELECT number_id FROM visitor WHERE number_id IS NOT NULL)
                """)

            print("\nДоступные номера:")

            available_numbers = self.cursor.fetchall()

            for number in available_numbers:
                print(f"ID: {number[0]}, Номер: {number[1]}, Категория: {number[2]}, Цена: {number[3]} руб.")

            number_id = int(input("Выберите ID номера: "))

            add_visitor_query = """
                    INSERT INTO visitor (name, number_id) VALUES (%s, %s);
                """

            self.cursor.execute(add_visitor_query, (visitor_name, number_id))

            self.DB_CONNECTION.commit()

            print(f"Посетитель '{visitor_name}' заселен в отель!")

        except Exception as e:

            print(f"Ошибка при добавлении посетителя: {e}")
            self.DB_CONNECTION.rollback()

    def show_all_visitor(self):

        try:
            query = """
                SELECT v.name, n.name, c.name, c.price
                FROM visitor v
                JOIN number n ON v.number_id = n.id
                JOIN category c ON n.category_id = c.id
                ORDER BY v.name
            """
            self.cursor.execute(query)

            visitors = self.cursor.fetchall()

            print("\nСписок всех посетителей:")

            for visitor in visitors:
                print(
                    f"Посетитель: {visitor[0]}, Номер: {visitor[1]}, Категория: {visitor[2]}, Цена: {visitor[3]} руб.")

        except Exception as e:

            print(f"Ошибка при получении списка посетителей: {e}")

    def show_available_number(self):

        try:
            query = """
                SELECT n.id, n.name, c.name, c.price
                FROM number n
                JOIN category c ON n.category_id = c.id
                WHERE n.id NOT IN (SELECT number_id FROM visitor WHERE number_id IS NOT NULL)
                ORDER BY c.price, n.name
            """
            self.cursor.execute(query)

            available_numbers = self.cursor.fetchall()

            print("\nСвободные номера:")

            for number in available_numbers:
                print(
                    f"ID номера: {number[0]}, номер: {number[1]}, категория: {number[2]}, стоимость: {number[3]} руб.")

        except Exception as e:

            print(f"Ошибка при получении свободных номеров: {e}")

    def __del__(self):

        self.DB_CONNECTION.close()


def main():
    db = DBFacade()

    while True:

        print("\nУПРАВЛЕНИЕ ГОСТИНИЦЕЙ\n")
        print("1. Добавить категорию номера")
        print("2. Добавить номер")
        print("3. Добавить посетителя")
        print("4. Показать всех посетителей")
        print("5. Показать свободные номера")
        print("0. Выход")

        choice = input("Выберите действие (0-5): ")

        if choice == '0':
            print("Вы вышли из программы!")
            break

        elif choice == '1':
            db.add_category()

        elif choice == '2':
            db.add_number()

        elif choice == '3':
            db.add_visitor_query()

        elif choice == '4':
            db.show_all_visitor()

        elif choice == '5':
            db.show_available_number()

        else:
            print("Неверный ввод, необходимо вводить числа от '0' до '5', повторите ввод!")


if __name__ == "__main__":
    main()
