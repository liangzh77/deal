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

def duplicate_schema(schema_src, schema_dst=None, with_content=True):
    try:
        if schema_dst is None:
            schema_dst = 'zoo_'+schema_src
        print(f'创建schema:{schema_dst}')
        sql = f"CREATE DATABASE `{schema_dst}`"
        count = execute_sql(sql, logging=False)
        if count==0:
            raise ValueError(f'schema已经存在：{schema_dst}')

        print(f'复制schema:{schema_src}')
        schema_data = {}
        res = query_sql(f"show tables from {schema_src}",logging=False)
        tables = list(map(lambda d: d[f'Tables_in_{schema_src}'], res))
        for table in tables:
            print(f'复制table:{table}')
            table_data = {}
            res = query_sql(f"SHOW CREATE TABLE {schema_src}.{table}",logging=False)
            sql = res[0]['Create Table']
            start_str = 'CREATE TABLE '
            sql = start_str + schema_dst+ '.' + sql[len(start_str):]
            count = execute_sql(sql, logging=False)
            if with_content:
                res = query_sql(f"SELECT * FROM {schema_src}.{table}",logging=False)
                insert_user_info(res, schema_dst, table)
        print('done')
    except Exception as e:
        print(e)


if 1:
    duplicate_schema('common')
#    duplicate_schema('ps插件')
if 0:
    duplicate_schema('ps插件','ae插件', with_content=False)
