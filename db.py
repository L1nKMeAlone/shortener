import sqlite3
con = sqlite3.connect('shortener.db')
cursor = con.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS "users"(
"id" INTEGER,
"name" TEXT,
"email" TEXT,
"password" TEXT,
PRIMARY KEY ("id" AUTOINCREMENT));
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS "links_type"(
"id" INTEGER,
"name" TEXT,
PRIMARY KEY ("id"));
""")

con.commit()
cursor.execute("""SELECT name FROM links_type where name=?;""", ("general",))
data = cursor.fetchall()
if len(data) == 0:
    cursor.execute('INSERT INTO links_type(id, name) VALUES(?, ?);', ("1", "general",))

cursor.execute("""SELECT name FROM links_type where name=?;""", ("private",))
data = cursor.fetchall()
if len(data) == 0:
    cursor.execute('INSERT INTO links_type(id, name) VALUES(?, ?);', ("2", "private",))

cursor.execute("""SELECT name FROM links_type where name=?;""", ("authorized",))
data = cursor.fetchall()
if len(data) == 0:
    cursor.execute('INSERT INTO links_type(id, name) VALUES(?, ?);', ("3", "authorized",))



cursor.execute("""CREATE TABLE IF NOT EXISTS "user_links"(
"id" INTEGER,
"user_id" INTEGER,
"private_id" INTEGER,
"long_link" TEXT,
"short_link" TEXT,
FOREIGN KEY("private_id") REFERENCES "links_type"("id"),
PRIMARY KEY ("id" AUTOINCREMENT),
FOREIGN KEY("user_id") REFERENCES "users"("id"));

""")

con.commit()

def create_user(name,email,password):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute('INSERT INTO users(name, email, password) VALUES(?, ?, ?);', (name, email, password,))
    con.commit()

def create_user_link(user_id, private_id, long_link, short_link):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute('INSERT INTO user_links(user_id, private_id, long_link, short_link) VALUES(?, ?, ?, ?);', (user_id, private_id, long_link, short_link,))
    con.commit()

def get_all_user_links(user_id):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    return cursor.execute("""SELECT link FROM user_links where user_id=?;""", (user_id,))

def delete_link(user_id, id):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute(f'DELETE FROM user_links WHERE user_id={user_id} AND id={id}')
    con.commit()

def getUser(user_id):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM users where id=? LIMIT 1;""", (user_id,))
    res = cursor.fetchone()
    if not res:
        print("Пользователь не найден")
        return False

    return res

def getUserByEmail(email):
    con = sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM users where email=? LIMIT 1;""", (email,))
    res = cursor.fetchone()
    if not res:
        print("Пользователь не найден")
        return False

    return res

