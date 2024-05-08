import sqlite3

conn = sqlite3.connect('deal.db')
cursor = conn.cursor()
def create_table():
    SQL_CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS PEOPLE
                        (ID INT PRIMARY KEY NOT NULL,
                        NAME TEXT NOT NULL,
                        AGE INT NOT NULL);'''
    conn.execute(SQL_CREATE_TABLE)

def insert_one():
    SQL_INSERT_ONE_DATA = "INSERT INTO PEOPLE(id,name,age) VALUES(4,'xag',23);"
    try:
        conn.execute(SQL_INSERT_ONE_DATA)
        # 必须要提交，才能正确执行
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('插入一条记录失败，回滚~')

def insert_many(data):
    SQL_INSERT_MANY_DATA = 'INSERT INTO PEOPLE (id,name,age) VALUES(?,?,?);'
    try:
        conn.executemany(SQL_INSERT_MANY_DATA, data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print('插入多条记录失败，回滚~')

def query_one(id):
    SQL_QUERY_ONE_DATA = "SELECT * FROM PEOPLE WHERE id={}"
    cursor.execute(SQL_QUERY_ONE_DATA.format(id))
    result = cursor.fetchall()
    print(type(result))
    print(result)

def update_one(id, name, age):
    SQL_UPDATE_ONE_DATA = "UPDATE PEOPLE SET NAME = '{}',AGE={} where id = {}"
    sql_update = SQL_UPDATE_ONE_DATA.format(name, age, id)
    print(sql_update)
    conn.execute(sql_update)
    conn.commit()

def del_one(id):
    SQL_DEL_ONE_DATA = "DELETE FROM PEOPLE where id ={}"
    sql_del = SQL_DEL_ONE_DATA.format(id)
    conn.execute(sql_del)
    conn.commit()

def teardown():
    cursor.close()
    conn.close()

create_table()
insert_one()
insert_many([(1, '张三', 11), (5, '李四', 12), (6, '王五', 13)])
query_one(5)
update_one(1,'刘六',61)
del_one(1)
