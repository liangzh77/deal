import os, pymysql, sys
sys.path.append(os.getcwd())
from datetime import datetime
from tool.tool import *
from mysql_db.mysql_tool import *

# MySQL连接信息
host = '127.0.0.1'
user = 'root'
password = 'chujiao'
database = 'douyin'

backup_dir = 'data_db'
backup_interval_minutes = 60*12

def get_latest_backup_time():
    latest_time = 0
    for root2, dirs2, files2 in os.walk(backup_dir):
        for f in files2:
            s = os.path.splitext(f)[0]
            try:
                date_obj = datetime.datetime.strptime(s, "backup_%Y%m%d_%H%M%S")
                timestamp = int(date_obj.timestamp())
                latest_time = max(timestamp, latest_time)
            except:
                pass
        break
    return latest_time


def backup_db_csv(minutes_interval=60):
    latest_time = get_latest_backup_time()
    if time.time()-latest_time<backup_interval_minutes*minutes_interval:
        return

    backup_filename = backup_dir + f'/backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    print('开始备份数据库，保存到：' + backup_filename)
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )

    # 创建游标
    cursor = connection.cursor()
    keys = get_table_columns('user_info', 'douyin', logging=False)
    cursor.execute("SELECT * FROM douyin.user_info")
    ll = cursor.fetchall()
    ll2 = [dict(zip(keys, row)) for row in ll]
    write_csv_file(backup_filename, ll2)

    # 关闭游标和连接
    cursor.close()
    connection.close()
    print('done')


def backup_db_pickle():
    print('开始备份数据库')
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor()
    res = query_sql("SHOW SCHEMAS",logging=False)
    schemas = list(map(lambda d: d['Database'], res))
    for k in ['information_schema', 'mysql', 'performance_schema', 'sys']:
        if k in schemas:
            schemas.remove(k)
    pickle_data = {}
    for schema in schemas:
        print(f'备份schema:{schema}')
        schema_data = {}
        res = query_sql(f"show tables from {schema}",logging=False)
        tables = list(map(lambda d: d[f'Tables_in_{schema}'], res))
        for table in tables:
            print(f'备份table:{table}')
            table_data = {}
            res = query_sql(f"SHOW CREATE TABLE {schema}.{table}",logging=False)
            sql = res[0]['Create Table']
            table_data['sql'] = sql
            res = query_sql(f"SELECT * FROM {schema}.{table}",logging=False)
            table_data['data'] = res
            schema_data[table] = table_data
        pickle_data[schema] = schema_data
    # 关闭游标和连接
    cursor.close()
    connection.close()
    backup_filename = backup_dir + f'/backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl'
    print('写文件：' + backup_filename)
    with open(backup_filename, 'wb') as file:
        pickle.dump(pickle_data, file)

    print('done')


def restore_db(backup_filename):
    import pickle

    with open(backup_filename, 'rb') as file:
        # 从文件中读取并反序列化对象
        schemas = pickle.load(file)
        
    schema_names = list(schemas.keys())
    schema_names.reverse()
    for schema_name in schema_names:
        schema = schemas[schema_name]
        sql = f"CREATE DATABASE `{schema_name}`"
        count = execute_sql(sql, logging=False)
        if count==0:
            raise ValueError(f'schema已经存在：{schema_name}')
        for table_name in schema:
            table = schema[table_name]
            sql = table['sql']
            start_str = 'CREATE TABLE '
            sql = start_str + schema_name+ '.' + sql[len(start_str):]
            count = execute_sql(sql, logging=False)
            insert_user_info(table['data'], schema_name, table_name)
    print('done')


#backup_db_pickle()
restore_db('C:/liangz77/python_projects/douyin_filter/data_db/backup_20240425_113831.pkl')
