import requests
import json
import pandas as pd

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

    def fetch_data(self):
        response = requests.get(self.base_url, params=self.params)
        data = json.loads(response.text)
        return data

    def parse_data(self):
        data = self.fetch_data()
        df = pd.DataFrame(data, columns=["day", "open", "high", "low", "close", "volume"])
        df["day"] = pd.to_datetime(df["day"])
        df = df.set_index("day")
        return df

# 使用示例
stock_code = "sz000001"  # 平安银行
stock_data = StockHistoryData(stock_code)
stock_df = stock_data.parse_data()
print(stock_df.head())