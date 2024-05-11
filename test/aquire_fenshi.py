import requests
import json
import mysql.connector

host = '127.0.0.1'
user = 'root'
password = 'chujiao'
database = 'sys'

class StockHistoryData:
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.base_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
        self.params = {
            "symbol": self.stock_code,
            "scale": "5",  # 5分钟
#            "ma": "5,10,20",
            "datalen": "5000"
        }

    def fetch_data(self, len):
        self.params['datalen'] = len
        response = requests.get(self.base_url, params=self.params)
        data = json.loads(response.text)
        return data


def get_insert_sql_str(sets):
    sets2 = sets.copy()
    keys = ', '.join(sets2.keys())
    values = ', '.join(f"'{v}'" for v in sets2.values())
    sql = f"({keys}) VALUES ({values})"
    return sql


def get_cursor():
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    return conn, cursor


def release_cursor(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()


def execute_sql(sql):
    while True:
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            updated_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            return updated_rows

        except Exception as e:
            cursor.close()
            conn.close()
            raise ValueError(str(e))


if __name__ == "__main__":
    fn = 'settings/A股个股.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        ls = f.readlines()
    for l in ls[1:]:
        ts_code,symbol,name,area,industry,list_date = l.strip().split(',')
        c1, c2 = ts_code.split('.')
        code = c2+c1
        stock_data = StockHistoryData(code)
        data = stock_data.fetch_data(5000)
        conn, cursor = get_cursor()
        sql = '''
            CREATE TABLE zyx.`min5` (
                `datetime` varchar(19) NOT NULL,
                `price` float DEFAULT NULL,
                `volume` float DEFAULT NULL,
                PRIMARY KEY (`datetime`),
                UNIQUE KEY `code` (`datetime`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                '''
        sql = sql.replace('min5', code)
        cursor.execute(sql)
        for d in data:
            sets = {'datetime':d['day'], 'price':d['close'], 'volume':d['volume']}
            insert_str = get_insert_sql_str(sets)
            sql = f"INSERT INTO zyx.{code} {insert_str}"
            cursor.execute(sql)
        release_cursor(conn, cursor)


if 0:
    # 使用示例
    stock_code = "sz000001"  # 平安银行
    stock_data = StockHistoryData(stock_code)
    stock_df = stock_data.fetch_data()
    print(stock_df.head())