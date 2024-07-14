import psycopg2
import configparser

def get_password():
    data = configparser.ConfigParser()
    data.read('password.ini')
    password = data["password"]["password"]
    name_bd = data["password"]["name_bd"]
    token = data["password"]["token"]
    return [password, name_bd, token]

def drop_tables():
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS users_words CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
                DROP TABLE IF EXISTS words CASCADE;
            """)
            conn.commit()

def create_table():
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS words(
                    id SERIAL PRIMARY KEY,
                    eng VARCHAR NOT NULL UNIQUE,
                    rus VARCHAR NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    name VARCHAR,
                    surname VARCHAR,
                    nickname VARCHAR,
                    chat_id BIGINT UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users_words(
                    id SERIAL PRIMARY KEY,
                    id_user INTEGER REFERENCES users(id),
                    id_word INTEGER REFERENCES words(id)
                );
            """)
            conn.commit()

def add_initial_words(eng, rus):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO words (eng, rus) 
                VALUES (%s, %s)
                ON CONFLICT (eng) DO NOTHING;
            """, (eng, rus))
            conn.commit()

def add_user(name, surname, nickname, chat_id):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name, surname, nickname, chat_id) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (chat_id) DO NOTHING 
                RETURNING id;
            """, (name, surname, nickname, chat_id))
            user_id = cur.fetchone()
            conn.commit()
            return user_id

def get_one_random_word(current_user_id):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT words.eng, words.rus 
                FROM words
                LEFT JOIN users_words ON words.id = users_words.id_word
                WHERE users_words.id_word IS NULL OR users_words.id_user = %s
                ORDER BY RANDOM() LIMIT 1;
            """, (current_user_id,))
            row = cur.fetchone()
            if row:
                return row[0], row[1]
            else:
                print("Таблица 'words' пуста.")
                return None, None

def get_three_random_words(current_user_id, target_word):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT eng FROM words
                LEFT JOIN users_words ON words.id = users_words.id_word
                WHERE (users_words.id_word IS NULL OR users_words.id_user = %s) AND eng != %s
                ORDER BY RANDOM() LIMIT 3;
            """, (current_user_id, target_word))
            return [row[0] for row in cur.fetchall()]

def get_current_user_id(chat_id):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM users 
                WHERE chat_id = %s;
            """, (chat_id,))
            curUser = cur.fetchone()
            return curUser[0] if curUser else None

def add_user_words(eng, rus, user_id):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO words (eng, rus) 
                VALUES (%s, %s)
                ON CONFLICT (eng) DO NOTHING
                RETURNING id;
            """, (eng, rus))
            word_id = cur.fetchone()
            if not word_id:
                cur.execute("""
                    SELECT id FROM words WHERE eng = %s;
                """, (eng,))
                word_id = cur.fetchone()
            if not word_id:
                return False
            else:
                cur.execute("""
                    INSERT INTO users_words (id_user, id_word) 
                    VALUES (%s, %s);
                """, (user_id, word_id[0]))
                conn.commit()
                return True

def delete_words(word, user_id):
    with psycopg2.connect(dbname=get_password()[1], user='postgres', password=get_password()[0]) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM words 
                WHERE eng = %s OR rus = %s;
            """, (word, word))
            word_id = cur.fetchone()
            if word_id:
                cur.execute("""
                    DELETE FROM users_words 
                    WHERE id_user = %s AND id_word = %s;
                """, (user_id, word_id[0]))
                cur.execute("""
                    DELETE FROM words 
                    WHERE id = %s;
                """, (word_id[0],))
                conn.commit()
                return True
            return False

# Удаление существующих таблиц и создание новых таблиц
drop_tables()
create_table()
add_initial_words('hello', 'привет')
add_initial_words('world', 'мир')
add_initial_words('apple', 'яблоко')
add_initial_words('orange', 'апельсин')
add_initial_words('banana', 'банан')
add_initial_words('grape', 'виноград')
add_initial_words('water', 'вода')
add_initial_words('coffee', 'кофе')
add_initial_words('tea', 'чай')
add_initial_words('bread', 'хлеб')
add_initial_words('butter', 'масло')
add_initial_words('cheese', 'сыр')
add_initial_words('milk', 'молоко')
add_initial_words('egg', 'яйцо')
add_initial_words('meat', 'мясо')
add_initial_words('fish', 'рыба')
add_initial_words('chicken', 'курица')
add_initial_words('bicycle', 'велосипед')
add_initial_words('bus', 'автобус')
add_initial_words('train', 'поезд')
add_initial_words('airplane', 'самолет')
add_initial_words('boat', 'лодка')
add_initial_words('ship', 'корабль')
add_initial_words('computer', 'компьютер')
add_initial_words('phone', 'телефон')
add_initial_words('table', 'стол')
add_initial_words('chair', 'стул')
add_initial_words('bed', 'кровать')
add_initial_words('window', 'окно')
add_initial_words('door', 'дверь')
add_initial_words('house', 'дом')
add_initial_words('building', 'здание')
add_initial_words('street', 'улица')
add_initial_words('flower', 'цветок')
add_initial_words('tree', 'дерево')
add_initial_words('book', 'книга')
add_initial_words('pen', 'ручка')
add_initial_words('paper', 'бумага')

